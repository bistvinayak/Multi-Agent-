import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

from llama_index.llms.google_genai import GoogleGenAI
llm = GoogleGenAI(model="gemini-2.5-flash", api_key=gemini_api_key)

from tavily import AsyncTavilyClient

async def search_web(query: str) -> str:
    """Useful for using the web to answer questions."""
    client = AsyncTavilyClient(api_key=tavily_api_key)
    return str(await client.search(query))

from llama_index.core.workflow import Event

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

from llama_index.core.agent.workflow import FunctionAgent

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

from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step, Context

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
        ctx.write_event_to_stream(ProgressEvent(msg=f"Topic: {ev.research_topic}"))
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

async def main():
    print("\n Starting Deep Research Workflow with Gemini...\n")
    workflow = DeepResearchWorkflow(timeout=300)
    handler = workflow.run(
        research_topic="History of Cricket in India",
        question_agent=question_agent,
        answer_agent=answer_agent,
        report_agent=report_agent,
        review_agent=review_agent
    )
    async for ev in handler.stream_events():
        if isinstance(ev, ProgressEvent):
            print(f"-- {ev.msg}")
    final_result = await handler
    print("\n" + "="*50)
    print("FINAL REPORT")
    print("="*50 + "\n")
    print(final_result)
    with open("report.txt", "w") as f:
        f.write(final_result)
    print("\nReport saved to report.txt")

if __name__ == "__main__":
    asyncio.run(main())

