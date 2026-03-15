document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('dataset');
    const fileNameDisplay = document.getElementById('file-name');
    const analyzeBtn = document.getElementById('analyze-btn');
    const dropZone = document.getElementById('drop-zone');
    
    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = `Selected: ${e.target.files[0].name}`;
            analyzeBtn.disabled = false;
        } else {
            fileNameDisplay.textContent = '';
            analyzeBtn.disabled = true;
        }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        let files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });
});

async function upload() {
    const fileInput = document.getElementById("dataset");
    const loader = document.getElementById("loader");
    const resultContainer = document.getElementById("result-container");
    const resultElement = document.getElementById("result");
    const btn = document.getElementById("analyze-btn");
    
    // Professional UI Elements
    const kpiBox = document.getElementById("kpi-box");
    const chartContainer = document.getElementById("chart-container");
    const aiAssistant = document.getElementById("ai-assistant");
    const aiBubbles = document.getElementById("ai-bubbles");
    const mlContainer = document.getElementById("ml-container");
    const mlResult = document.getElementById("ml-result");

    if (!fileInput.files || fileInput.files.length === 0) return;

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // UI Reset
    btn.disabled = true;
    loader.style.display = "block";
    
    try {
        let response = await fetch("http://127.0.0.1:8000/upload", {
            method: "POST",
            body: formData
        });
        
        let result = await response.json();
        if (!response.ok) throw new Error(result.message || "Analysis failed");

        // 1. Populate KPIs
        kpiBox.style.display = "grid";
        document.getElementById("kpi-rows").textContent = result.analysis.rows.toLocaleString();
        document.getElementById("kpi-cols").textContent = result.analysis.columns;
        document.getElementById("kpi-insights").textContent = result.analysis.insights.length;
        
        // Simple health score logic
        const missingCount = Object.values(result.analysis.missing).reduce((a, b) => a + b, 0);
        const health = Math.max(0, 100 - (missingCount / (result.analysis.rows * result.analysis.columns) * 100));
        document.getElementById("kpi-health").textContent = `${Math.round(health)}%`;

        // 2. AI Assistant Narrative
        aiAssistant.style.display = "block";
        aiBubbles.innerHTML = "";
        result.analysis.insights.forEach((insight, i) => {
            setTimeout(() => {
                const bubble = document.createElement("div");
                bubble.className = "bubble";
                bubble.textContent = insight;
                aiBubbles.appendChild(bubble);
            }, i * 300);
        });

        // 3. Render Dashboard Charts (Wrapped in Cards)
        chartContainer.innerHTML = "";
        if (result.charts) {
            result.charts.forEach((chartData, index) => {
                const card = document.createElement("div");
                card.className = "chart-card";
                card.innerHTML = `<div class="chart-header">📊 ${chartData.layout.title.text || 'Visualization'}</div>`;
                
                const plotDiv = document.createElement("div");
                plotDiv.id = `chart-${index}`;
                plotDiv.className = "plotly-box";
                card.appendChild(plotDiv);
                chartContainer.appendChild(card);

                Plotly.newPlot(plotDiv.id, chartData.data, chartData.layout, {responsive: true});
            });
        }

        // 4. ML Predictions
        if (result.ml_prediction && !result.ml_prediction.error) {
            mlContainer.style.display = "block";
            mlResult.innerHTML = `
                <div style="padding: 10px; border-left: 4px solid var(--accent-color); background: rgba(88, 166, 255, 0.05); border-radius: 4px;">
                    <p><strong>Predicted Target:</strong> ${result.ml_prediction.target_column}</p>
                    <p><strong>Model:</strong> ${result.ml_prediction.model_type}</p>
                    <p><strong>Accuracy (R2):</strong> <span style="color: var(--accent-color); font-weight: bold;">${result.ml_prediction.r2_score}</span></p>
                </div>
            `;
        } else {
            mlContainer.style.display = "none";
        }

        // 5. Raw Stats
        resultElement.textContent = JSON.stringify(result.analysis, null, 2);
        resultContainer.style.display = "block";
        
    } catch (error) {
        alert(error.message);
    } finally {
        loader.style.display = "none";
        btn.disabled = false;
    }
}