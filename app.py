from flask import Flask, render_template, request, jsonify, send_file, Response
import asyncio
import os
import json
import io
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

from llama_index.llms.google_genai import GoogleGenAI
from tavily import AsyncTavilyClient
from llama_index.core.workflow import Event
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step, Context

app = Flask(__name__)
llm = GoogleGenAI(model="gemini-2.5-flash", api_key=gemini_api_key)

async def search_web(query: str) -> str:
    """Useful for using the web to answer questions."""
    client = AsyncTavilyClient(api_key=tavily_api_key)
    return str(await client.search(query))

async def search_stock_news(query: str) -> str:
    """Search for latest stock market news."""
    client = AsyncTavilyClient(api_key=tavily_api_key)
    return str(await client.search(query, search_depth="advanced"))

class GenerateEvent(Event):
    research_topic: str

class QuestionEvent(Event):
    question: str

class AnswerEvent(Event):
    question: str
    answer: str

class ProgressEvent(Event):
    msg: str

class FeedbackEvent(Event):
    research_topic: str
    feedback: str

class ReviewEvent(Event):
    report: str

question_agent = FunctionAgent(
    tools=[],
    llm=llm,
    verbose=False,
    system_prompt="Generate questions on the given topic one per line. No markdown."
)

answer_agent = FunctionAgent(
    tools=[search_web],
    llm=llm,
    verbose=False,
    system_prompt="Answer the given question using web search. Return just the answer."
)

stock_agent = FunctionAgent(
    tools=[search_stock_news],
    llm=llm,
    verbose=False,
    system_prompt="""You are a stock market research expert for Indian markets.
    Search for latest stock news, market trends, and financial data.
    Find top 5 stocks promising to invest in tomorrow.
    For each stock include:
    1. Stock name and NSE/BSE symbol
    2. Current price and trend
    3. Why it looks good to invest
    4. Risk level (Low/Medium/High)
    5. Recent news affecting it
    Always mention this is not financial advice."""
)

report_agent = FunctionAgent(
    tools=[],
    llm=llm,
    verbose=False,
    system_prompt="Combine all answers into a comprehensive well structured report."
)

review_agent = FunctionAgent(
    tools=[],
    llm=llm,
    verbose=False,
    system_prompt="Review the report. If good respond with just ACCEPTABLE. Otherwise suggest more questions."
)

class DeepResearchWorkflow(Workflow):

    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> GenerateEvent:
        self.question_agent = ev.question_agent
        self.answer_agent = ev.answer_agent
        self.report_agent = ev.report_agent
        self.review_agent = ev.review_agent
        self.review_cycles = 0
        self.research_topic = ev.research_topic
        self.total_questions = 0
        ctx.write_event_to_stream(ProgressEvent(msg="Starting research..."))
        return GenerateEvent(research_topic=ev.research_topic)

    @step
    async def generate_questions(self, ctx: Context, ev: GenerateEvent | FeedbackEvent) -> QuestionEvent:
        ctx.write_event_to_stream(ProgressEvent(msg=f"Generating questions on: {ev.research_topic}"))
        prompt = f"Generate questions on: {ev.research_topic}"
        if isinstance(ev, FeedbackEvent):
            prompt += f" Feedback: {ev.feedback}"
        result = await self.question_agent.run(user_msg=prompt)
        lines = str(result).split("\n")
        questions = [line.strip() for line in lines if line.strip() != ""]
        self.total_questions = len(questions)
        ctx.write_event_to_stream(ProgressEvent(msg=f"Generated {len(questions)} questions"))
        for question in questions:
            ctx.send_event(QuestionEvent(question=question))

    @step
    async def answer_question(self, ctx: Context, ev: QuestionEvent) -> AnswerEvent:
        ctx.write_event_to_stream(ProgressEvent(msg=f"Answering: {ev.question}"))
        result = await self.answer_agent.run(user_msg=f"Answer this: {ev.question}")
        ctx.write_event_to_stream(ProgressEvent(msg=f"Answered: {ev.question}"))
        return AnswerEvent(question=ev.question, answer=str(result))

    @step
    async def write_report(self, ctx: Context, ev: AnswerEvent) -> ReviewEvent:
        research = ctx.collect_events(ev, [AnswerEvent] * self.total_questions)
        if research is None:
            ctx.write_event_to_stream(ProgressEvent(msg="Collecting answers..."))
            return None
        ctx.write_event_to_stream(ProgressEvent(msg="Writing report..."))
        all_answers = ""
        for q_and_a in research:
            all_answers += f"Q: {q_and_a.question}\nA: {q_and_a.answer}\n\n"
        result = await self.report_agent.run(
            user_msg=f"Write report on: {self.research_topic}\n\n{all_answers}"
        )
        return ReviewEvent(report=str(result))

    @step
    async def review(self, ctx: Context, ev: ReviewEvent) -> StopEvent | FeedbackEvent:
        ctx.write_event_to_stream(ProgressEvent(msg="Reviewing report..."))
        result = await self.review_agent.run(
            user_msg=f"Review report on: {self.research_topic}\n\n{ev.report}"
        )
        self.review_cycles += 1
        if str(result).strip() == "ACCEPTABLE" or self.review_cycles >= 3:
            ctx.write_event_to_stream(ProgressEvent(msg=f"Done after {self.review_cycles} cycles!"))
            return StopEvent(result=ev.report)
        else:
            ctx.write_event_to_stream(ProgressEvent(msg="Needs more research..."))
            return FeedbackEvent(research_topic=self.research_topic, feedback=str(result))

async def run_research(topic):
    progress_logs = []
    workflow = DeepResearchWorkflow(timeout=300)
    handler = workflow.run(
        research_topic=topic,
        question_agent=question_agent,
        answer_agent=answer_agent,
        report_agent=report_agent,
        review_agent=review_agent
    )
    async for ev in handler.stream_events():
        if isinstance(ev, ProgressEvent):
            progress_logs.append(ev.msg)
    final_result = await handler
    return final_result, progress_logs

async def run_stock_research():
    result = await stock_agent.run(
        user_msg="""Search for the latest Indian stock market news today.
        Find top 5 stocks to invest in tomorrow on NSE/BSE.
        Include stock name, symbol, price trend, reason to invest,
        risk level, and recent news. Add disclaimer this is not financial advice."""
    )
    return str(result)

def create_pdf(report_text):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=inch, leftMargin=inch,
                               topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = []
        lines = report_text.split('\n')
        for line in lines:
            if line.startswith('##'):
                from reportlab.lib import colors
                style = ParagraphStyle('h', parent=styles['Heading1'],
                                      fontSize=16, spaceAfter=12,
                                      textColor=colors.HexColor('#1f6feb'))
                story.append(Paragraph(line.replace('#','').strip(), style))
            elif line.strip():
                style = ParagraphStyle('b', parent=styles['Normal'],
                                      fontSize=11, spaceAfter=8, leading=16)
                story.append(Paragraph(line.strip(), style))
            else:
                story.append(Spacer(1, 0.1*inch))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/research", methods=["POST"])
def research():
    topic = request.json.get("topic")
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    report, logs = loop.run_until_complete(run_research(topic))
    loop.close()
    return jsonify({"report": report, "logs": logs})

@app.route("/stock-research", methods=["GET"])
def stock_research():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run_stock_research())
    loop.close()
    return jsonify({"report": result})

@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    report_text = request.json.get("report", "")
    if not report_text:
        return jsonify({"error": "No report"}), 400
    pdf_buffer = create_pdf(report_text)
    if pdf_buffer is None:
        return jsonify({"error": "PDF generation failed"}), 500
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="research_report.pdf"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="127.0.0.1")
