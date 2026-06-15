<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deep Research AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #0d1117;
            color: #e6edf3;
            min-height: 100vh;
        }
        .header {
            background: #161b22;
            padding: 15px 40px;
            border-bottom: 1px solid #21262d;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo { font-size: 1.4em; font-weight: bold; color: #58a6ff; }
        .badge {
            background: #238636;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
        }
        .main { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        .hero { text-align: center; margin-bottom: 40px; }
        .hero h1 {
            font-size: 2.8em;
            background: linear-gradient(90deg, #58a6ff, #bc8cff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .hero p { color: #8b949e; font-size: 1.1em; }
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 25px;
            background: #161b22;
            padding: 5px;
            border-radius: 12px;
            border: 1px solid #21262d;
        }
        .tab {
            flex: 1;
            padding: 12px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            transition: all 0.3s;
            background: transparent;
            color: #8b949e;
        }
        .tab.active {
            background: linear-gradient(135deg, #1f6feb, #388bfd);
            color: white;
        }
        .tab:hover:not(.active) { background: #21262d; color: #e6edf3; }
        .panel { display: none; }
        .panel.active { display: block; }
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
        input {
            flex: 1;
            padding: 14px 18px;
            border-radius: 10px;
            border: 1px solid #21262d;
            background: #161b22;
            color: #e6edf3;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s;
        }
        input:focus { border-color: #58a6ff; }
        .btn {
            padding: 14px 24px;
            border-radius: 10px;
            border: none;
            font-size: 1em;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #1f6feb, #388bfd);
            color: white;
        }
        .btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-green {
            background: linear-gradient(135deg, #238636, #2ea043);
            color: white;
            width: 100%;
            padding: 16px;
            font-size: 1.1em;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .btn-green:hover { opacity: 0.9; }
        .btn-green:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-red {
            background: linear-gradient(135deg, #da3633, #f85149);
            color: white;
            padding: 10px 18px;
            font-size: 0.9em;
            border-radius: 8px;
        }
        .btn-gray {
            background: #21262d;
            color: #e6edf3;
            padding: 10px 18px;
            font-size: 0.9em;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        .progress-box {
            background: #161b22;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            display: none;
            border: 1px solid #21262d;
        }
        .progress-title {
            color: #58a6ff;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .progress-logs { max-height: 180px; overflow-y: auto; }
        .log-item {
            padding: 7px 12px;
            margin-bottom: 4px;
            background: #0d1117;
            border-radius: 6px;
            color: #8b949e;
            font-size: 0.85em;
            border-left: 3px solid #58a6ff;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-8px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .report-box {
            background: #161b22;
            border-radius: 12px;
            padding: 25px;
            display: none;
            border: 1px solid #21262d;
        }
        .report-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #21262d;
            flex-wrap: wrap;
            gap: 10px;
        }
        .report-title { color: #58a6ff; font-size: 1.2em; font-weight: 600; }
        .report-actions { display: flex; gap: 8px; }
        .report-content {
            white-space: pre-wrap;
            color: #e6edf3;
            line-height: 1.8;
            font-size: 0.95em;
        }
        .spinner {
            width: 18px;
            height: 18px;
            border: 2px solid #21262d;
            border-top: 2px solid #58a6ff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            display: inline-block;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .status-bar {
            display: none;
            align-items: center;
            gap: 10px;
            color: #58a6ff;
            margin-bottom: 15px;
            font-size: 0.95em;
        }
        .stock-info {
            background: #161b22;
            border: 1px solid #21262d;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            color: #8b949e;
            font-size: 0.9em;
        }
        .stock-info h3 { color: #2ea043; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🔬 Deep Research AI</div>
        <div class="badge">Powered by Gemini</div>
    </div>

    <div class="main">
        <div class="hero">
            <h1>Research Anything</h1>
            <p>Multi-agent AI research powered by Gemini + Tavily Web Search</p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('research')">🔍 Deep Research</button>
            <button class="tab" onclick="switchTab('stocks')">📈 Stock Research</button>
        </div>

        <!-- Research Panel -->
        <div class="panel active" id="research-panel">
            <div class="search-box">
                <input type="text" id="topicInput"
                    placeholder="Enter any research topic..."
                    onkeypress="if(event.key==='Enter') startResearch()"/>
                <button class="btn btn-primary" id="researchBtn" onclick="startResearch()">
                    Research
                </button>
            </div>

            <div class="status-bar" id="statusBar">
                <div class="spinner"></div>
                <span id="statusText">Researching...</span>
            </div>

            <div class="progress-box" id="progressBox">
                <div class="progress-title">📊 Live Progress</div>
                <div class="progress-logs" id="progressLogs"></div>
            </div>

            <div class="report-box" id="reportBox">
                <div class="report-header">
                    <div class="report-title">📄 Research Report</div>
                    <div class="report-actions">
                        <button class="btn btn-red" onclick="downloadPDF()">📥 Download PDF</button>
                        <button class="btn btn-gray" onclick="copyReport()">📋 Copy</button>
                    </div>
                </div>
                <div class="report-content" id="reportContent"></div>
            </div>
        </div>

        <!-- Stock Panel -->
        <div class="panel" id="stocks-panel">
            <div class="stock-info">
                <h3>📈 AI Stock Analyst</h3>
                <p>Get AI-powered analysis of top Indian stocks to watch tomorrow based on latest news and market trends. <strong>Not financial advice.</strong></p>
            </div>

            <button class="btn btn-green" id="stockBtn" onclick="getStockResearch()">
                🔍 Analyze Top Stocks for Tomorrow
            </button>

            <div class="status-bar" id="stockStatusBar">
                <div class="spinner"></div>
                <span>Analyzing stock market...</span>
            </div>

            <div class="report-box" id="stockReportBox">
                <div class="report-header">
                    <div class="report-title">📈 Stock Analysis Report</div>
                    <div class="report-actions">
                        <button class="btn btn-red" onclick="downloadStockPDF()">📥 Download PDF</button>
                        <button class="btn btn-gray" onclick="copyStockReport()">📋 Copy</button>
                    </div>
                </div>
                <div class="report-content" id="stockReportContent"></div>
            </div>
        </div>
    </div>

    <script>
        let currentReport = "";
        let currentStockReport = "";

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-panel').classList.add('active');
        }

        function addLog(msg) {
            const logs = document.getElementById("progressLogs");
            const div = document.createElement("div");
            div.className = "log-item";
            div.textContent = "📌 " + msg;
            logs.appendChild(div);
            logs.scrollTop = logs.scrollHeight;
        }

        async function startResearch() {
            const topic = document.getElementById("topicInput").value.trim();
            if (!topic) { alert("Please enter a research topic!"); return; }

            const btn = document.getElementById("researchBtn");
            const statusBar = document.getElementById("statusBar");
            const progressBox = document.getElementById("progressBox");
            const reportBox = document.getElementById("reportBox");
            const progressLogs = document.getElementById("progressLogs");

            btn.disabled = true;
            btn.textContent = "Researching...";
            statusBar.style.display = "flex";
            progressBox.style.display = "block";
            reportBox.style.display = "none";
            progressLogs.innerHTML = "";

            try {
                const response = await fetch("/research", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ topic })
                });
                const data = await response.json();
                if (data.error) { alert("Error: " + data.error); return; }
                data.logs.forEach(log => addLog(log));
                currentReport = data.report;
                document.getElementById("reportContent").textContent = data.report;
                reportBox.style.display = "block";
            } catch (e) {
                alert("Error: " + e.message);
            } finally {
                btn.disabled = false;
                btn.textContent = "Research";
                statusBar.style.display = "none";
            }
        }

        async function getStockResearch() {
            const btn = document.getElementById("stockBtn");
            const statusBar = document.getElementById("stockStatusBar");
            const reportBox = document.getElementById("stockReportBox");

            btn.disabled = true;
            btn.textContent = "Analyzing...";
            statusBar.style.display = "flex";
            reportBox.style.display = "none";

            try {
                const response = await fetch("/stock-research");
                const data = await response.json();
                if (data.error) { alert("Error: " + data.error); return; }
                currentStockReport = data.report;
                document.getElementById("stockReportContent").textContent = data.report;
                reportBox.style.display = "block";
            } catch (e) {
                alert("Error: " + e.message);
            } finally {
                btn.disabled = false;
                btn.textContent = "🔍 Analyze Top Stocks for Tomorrow";
                statusBar.style.display = "none";
            }
        }

        async function downloadPDF() {
            if (!currentReport) { alert("No report yet!"); return; }
            const response = await fetch("/download-pdf", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ report: currentReport })
            });
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "research_report.pdf";
            a.click();
        }

        async function downloadStockPDF() {
            if (!currentStockReport) { alert("No report yet!"); return; }
            const response = await fetch("/download-pdf", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ report: currentStockReport })
            });
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "stock_report.pdf";
            a.click();
        }

        function copyReport() {
            navigator.clipboard.writeText(currentReport);
            alert("Copied!");
        }

        function copyStockReport() {
            navigator.clipboard.writeText(currentStockReport);
            alert("Copied!");
        }
    </script>
</body>
</html>
