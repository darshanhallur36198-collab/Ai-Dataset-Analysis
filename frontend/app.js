document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('dataset');
    const fileNameDisplay = document.getElementById('file-name');
    const analyzeBtn = document.getElementById('analyze-btn');
    const dropZone = document.getElementById('drop-zone');
    
    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            fileNameDisplay.style.color = 'var(--text-primary)';
            analyzeBtn.disabled = false;
        } else {
            fileNameDisplay.textContent = 'Drag & Drop CSV, or Click to Browse';
            fileNameDisplay.style.color = 'var(--text-secondary)';
            analyzeBtn.disabled = true;
        }
    });

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            // Trigger change event manually
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
    
    // Dashboard Elements
    const chartContainer = document.getElementById("chart-container");
    const chartsWrapper = document.getElementById("charts-wrapper");
    const mlContainer = document.getElementById("ml-container");
    const mlResult = document.getElementById("ml-result");
    const aiAssistant = document.getElementById("ai-assistant");
    const aiBubbles = document.getElementById("ai-bubbles");

    if (!fileInput.files || fileInput.files.length === 0) return;

    let file = fileInput.files[0];
    let formData = new FormData();
    formData.append("file", file);

    // Reset UI
    btn.disabled = true;
    loader.style.display = "block";
    resultContainer.style.display = "none";
    chartsWrapper.style.display = "none";
    mlContainer.style.display = "none";
    aiAssistant.style.display = "none";
    chartContainer.innerHTML = "";
    mlResult.innerHTML = "";
    aiBubbles.innerHTML = "";

    try {
        let response = await fetch("http://127.0.0.1:8000/upload", {
            method: "POST",
            body: formData
        });
        
        let result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || "Failed to analyze data");
        }

        // Display AI Assistant Bubbles
        if (result.analysis && result.analysis.insights) {
            aiAssistant.style.display = "block";
            result.analysis.insights.forEach((insight, i) => {
                setTimeout(() => {
                    const bubble = document.createElement("div");
                    bubble.className = "bubble";
                    bubble.textContent = insight;
                    aiBubbles.appendChild(bubble);
                }, i * 400);
            });
        }

        // 1. Display Basic Stats Analysis
        resultElement.innerText = JSON.stringify(result.analysis || result, null, 2);
        
        // 2. Render Machine Learning Prediction Engine
        if (result.ml_prediction) {
            mlContainer.style.display = "block";
            if (result.ml_prediction.error) {
                 mlResult.innerHTML = `<p style="color:#ff7b72">${result.ml_prediction.error}</p>`;
            } else {
                 mlResult.innerHTML = `
                    <div style="background: rgba(83, 155, 245, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid var(--accent-color);">
                        <p><strong>Predicted Target:</strong> ${result.ml_prediction.target_column}</p>
                        <p><strong>Model:</strong> ${result.ml_prediction.model_type}</p>
                        <p><strong>Accuracy (R2 Score):</strong> <span style="color:#a5d6ff; font-weight:bold;">${result.ml_prediction.r2_score}</span></p>
                    </div>
                 `;
            }
        }

        // 3. Render Plotly Charts (AI Dashboard)
        if (result.charts && result.charts.length > 0) {
            chartsWrapper.style.display = "block";
            
            result.charts.forEach((chartData, index) => {
                let div = document.createElement("div");
                div.id = "plotly-chart-" + index;
                div.className = "plotly-box";
                chartContainer.appendChild(div);

                Plotly.newPlot(
                    div.id,
                    chartData.data,
                    chartData.layout,
                    {responsive: true}
                );
            });
        }
        
        if (result.status === "error") {
            resultElement.style.color = "#ff7b72";
        } else {
            resultElement.style.color = "#a5d6ff";
        }
        
    } catch (error) {
        resultElement.innerText = `Error: ${error.message}`;
        resultElement.style.color = "#ff7b72";
    } finally {
        loader.style.display = "none";
        resultContainer.style.display = "block";
        btn.disabled = false;
        
        // Scroll to results
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
}