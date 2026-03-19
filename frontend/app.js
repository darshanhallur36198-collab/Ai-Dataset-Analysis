/* ═══════════════════════════════════════════════════════════════
   AI Autonomous Data Analyst — app.js
   AUTO-ANALYSIS: analysis runs immediately on file selection
   ═══════════════════════════════════════════════════════════════ */

let analysisData = null;

// ─── Settings ──────────────────────────────────────────────────
function getSettings() {
    return {
        apiUrl:    localStorage.getItem('api_url')    || 'http://127.0.0.1:8000',
        maxCharts: parseInt(localStorage.getItem('max_charts') || '20'),
        theme:     localStorage.getItem('chart_theme') || 'plotly_dark',
        geminiKey: localStorage.getItem('gemini_key')  || '',
    };
}

function saveSettings() {
    localStorage.setItem('api_url',     document.getElementById('setting-api-url').value.trim());
    localStorage.setItem('max_charts',  document.getElementById('setting-max-charts').value);
    localStorage.setItem('chart_theme', document.getElementById('setting-theme').value);
    localStorage.setItem('gemini_key',  document.getElementById('setting-gemini-key').value.trim());

    // ── Re-render all open charts with the new theme ──────────
    if (analysisData && analysisData.charts) {
        populateDashboardCharts(analysisData.charts);
        populateGraphsSection(analysisData.charts);
    }

    const msg = document.getElementById('settings-msg');
    msg.style.display = 'block';
    setTimeout(() => msg.style.display = 'none', 2500);
}

// ─── Section meta ──────────────────────────────────────────────
const SECTION_META = {
    'section-dashboard': { title: 'Ai Dataset Analytics',  sub: 'Automatic AI-driven analysis & insights' },
    'section-graphs':    { title: 'Visualization Suite',      sub: 'All generated charts from your dataset' },
    'section-cleaning':  { title: 'Data Cleaning Report',     sub: 'Automatic missing value & type repairs' },
    'section-ml':        { title: 'ML Predictions',           sub: 'Automated regression / classification' },
    'section-reports':   { title: 'Statistical Report',       sub: 'Full descriptive statistics & summaries' },
    'section-chat':      { title: 'Chat With Data',           sub: 'Ask natural language questions about your dataset' },
    'section-settings':  { title: 'Settings',                 sub: 'Configure API, chart limits & theme' },
};

// ─── Navigation ────────────────────────────────────────────────
function initNav() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active-section'));
            document.getElementById(item.dataset.section).classList.add('active-section');

            const meta = SECTION_META[item.dataset.section];
            if (meta) {
                document.getElementById('page-title').textContent    = meta.title;
                document.getElementById('page-subtitle').textContent = meta.sub;
            }
        });
    });
}

// ─── Drag-and-drop + auto-analysis on file select ──────────────
function initFileInput() {
    const fileInput = document.getElementById('dataset');
    const dropZone  = document.getElementById('drop-zone');

    // Auto-run analysis as soon as a file is chosen
    fileInput.addEventListener('change', e => {
        if (e.target.files.length > 0) {
            document.getElementById('file-name').textContent = `📄 ${e.target.files[0].name}`;
            runAnalysis(e.target.files[0]);   // ← AUTOMATIC
        }
    });

    ['dragenter','dragover','dragleave','drop'].forEach(evt =>
        dropZone.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); })
    );
    ['dragenter','dragover'].forEach(e => dropZone.addEventListener(e, () => dropZone.classList.add('dragover')));
    ['dragleave','drop'].forEach(e => dropZone.addEventListener(e, () => dropZone.classList.remove('dragover')));

    dropZone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            document.getElementById('file-name').textContent = `📄 ${files[0].name}`;
            runAnalysis(files[0]);   // ← AUTOMATIC on drop
        }
    });
}

// ─── Progress bar helper ───────────────────────────────────────
const STEPS = [
    'Reading dataset…',
    'Cleaning & validating data…',
    'Running statistical analysis…',
    'Generating AI visualizations…',
    'Training ML model…',
    'Building narrative insights…',
    'Finalizing dashboard…',
];

function setProgress(pct, label) {
    document.getElementById('progress-bar').style.width  = pct + '%';
    document.getElementById('progress-label').textContent = label;
}

function showProgress() {
    document.getElementById('progress-wrap').style.display = 'block';
    document.getElementById('kpi-box').style.display       = 'none';
    document.getElementById('ai-assistant').style.display  = 'none';
    document.getElementById('chart-container').innerHTML   = '';
    setProgress(5, STEPS[0]);
}

function hideProgress() {
    document.getElementById('progress-wrap').style.display = 'none';
}

// Fake incremental progress animation while waiting for the API
function animateProgress(startPct, endPct, duration, labelStart) {
    return new Promise(resolve => {
        const fps      = 30;
        const steps    = (duration / 1000) * fps;
        const stepSize = (endPct - startPct) / steps;
        let current    = startPct;
        let labelIdx   = STEPS.indexOf(labelStart);

        const interval = setInterval(() => {
            current += stepSize;
            setProgress(Math.min(current, endPct), STEPS[Math.min(labelIdx, STEPS.length - 1)]);
            if (current >= endPct) { clearInterval(interval); resolve(); }
        }, 1000 / fps);
    });
}

// ─── Main analysis pipeline ────────────────────────────────────
async function runAnalysis(file) {
    const settings = getSettings();
    const formData = new FormData();
    formData.append('file', file);

    showProgress();

    // Animate progress while request is in-flight
    const progressPromise = (async () => {
        await animateProgress(5,  25, 800,  STEPS[0]);
        await animateProgress(25, 50, 1200, STEPS[1]);
        await animateProgress(50, 70, 1000, STEPS[2]);
        await animateProgress(70, 85, 800,  STEPS[3]);
        await animateProgress(85, 95, 600,  STEPS[4]);
    })();

    let result;
    try {
        const response = await fetch(`${settings.apiUrl}/upload`, { method: 'POST', body: formData });
        result = await response.json();

        // Wait until animation at least reaches 95%
        await progressPromise;

        if (!response.ok || result.status === 'error') throw new Error(result.message || 'Analysis failed');
    } catch (err) {
        hideProgress();
        showError(err.message);
        return;
    }

    setProgress(100, '✅ Analysis complete!');
    await new Promise(r => setTimeout(r, 600));
    hideProgress();

    analysisData = result;

    // ── Populate every section ──────────────────────────────────
    populateKPIs(result.analysis);
    populateInsights(result.analysis.insights);
    populateDashboardCharts(result.charts || []);
    populateGraphsSection(result.charts || []);
    populateCleaningSection(result.analysis);
    populateMLSection(result.ml_prediction);
    populateReportsSection(result.analysis);

    // Auto-scroll to results
    document.getElementById('ai-assistant').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ─── Error display ──────────────────────────────────────────────
function showError(msg) {
    const el = document.getElementById('chart-container');
    el.innerHTML = `<div class="empty-state" style="color:#f98d95; grid-column:1/-1">❌ ${msg}</div>`;
}

// ─── KPI bar ───────────────────────────────────────────────────
function populateKPIs(analysis) {
    const missing = Object.values(analysis.missing).reduce((a, b) => a + b, 0);
    const health  = Math.max(0, 100 - (missing / (analysis.rows * analysis.columns) * 100));
    document.getElementById('kpi-rows').textContent     = analysis.rows.toLocaleString();
    document.getElementById('kpi-cols').textContent     = analysis.columns;
    document.getElementById('kpi-health').textContent   = `${Math.round(health)}%`;
    document.getElementById('kpi-insights').textContent = analysis.insights.length;
    document.getElementById('kpi-box').style.display    = 'grid';
}

// ─── AI insight bubbles ────────────────────────────────────────
function populateInsights(insights) {
    const panel   = document.getElementById('ai-assistant');
    const bubbles = document.getElementById('ai-bubbles');
    bubbles.innerHTML = '';
    panel.style.display = 'block';
    insights.forEach((text, i) => setTimeout(() => {
        const div = document.createElement('div');
        div.className   = 'bubble';
        div.textContent = text;
        bubbles.appendChild(div);
    }, i * 250));
}

// ─── Render one Plotly chart into a container ──────────────────
function renderChart(chartData, index, container, prefix = 'c') {
    const settings  = getSettings();
    const chartType = chartData._chart_type || 'other';

    const card = document.createElement('div');
    card.className          = 'chart-card';
    card.dataset.chartType  = chartType;

    const header = document.createElement('div');
    header.className = 'chart-header';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';

    const titleSpan = document.createElement('span');
    titleSpan.textContent = (chartData.layout?.title?.text || `Chart ${index + 1}`).replace(/<[^>]+>/g, '');
    header.appendChild(titleSpan);

    // 🔄 Rotation & 📥 Download Buttons
    const btnGroup = document.createElement('div');
    btnGroup.style.display = 'flex';
    btnGroup.style.gap = '8px';

    const canRotate = chartData.data.some(d => ['bar', 'box'].includes(d.type));
    if (canRotate) {
        const rotBtn = document.createElement('button');
        rotBtn.innerHTML = '🔄 Rotate';
        rotBtn.className = 'btn-mini';
        rotBtn.onclick = () => toggleRotation(`${prefix}_${index}`);
        btnGroup.appendChild(rotBtn);
    }

    const dlBtn = document.createElement('button');
    dlBtn.innerHTML = '📥 Download';
    dlBtn.className = 'btn-mini';
    dlBtn.onclick = () => downloadChart(`${prefix}_${index}`, titleSpan.textContent);
    btnGroup.appendChild(dlBtn);

    header.appendChild(btnGroup);

    const plotDiv = document.createElement('div');
    plotDiv.id        = `${prefix}_${index}`;
    plotDiv.className = 'plotly-box';

    card.appendChild(header);
    card.appendChild(plotDiv);
    container.appendChild(card);

    const layout = {
        ...chartData.layout,
        template: settings.theme,
    };

    if (settings.theme === 'plotly_dark') {
        layout.paper_bgcolor = 'rgba(0,0,0,0)';
        layout.plot_bgcolor  = 'rgba(0,0,0,0)';
        layout.font          = { color: '#c9d1d9', family: 'Inter, Segoe UI, sans-serif' };
    } else {
        // Remove strictly-enforced dark mode rules from backend layout overrides
        delete layout.paper_bgcolor;
        delete layout.plot_bgcolor;
        layout.paper_bgcolor = '#ffffff';
        layout.font = { color: '#333333', family: 'Inter, Segoe UI, sans-serif' };
        
        // Make the chart card light to visibly match the bright chart
        card.style.background = 'rgba(255, 255, 255, 0.95)';
        card.style.borderColor = '#e1e4e8';
        card.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
        header.style.borderBottomColor = '#eaeaea';
        titleSpan.style.color = '#111111';
        Array.from(btnGroup.children).forEach(btn => {
            btn.style.borderColor = '#ccc';
            btn.style.color = '#444';
            btn.style.background = '#f5f5f5';
        });
    }

    Plotly.newPlot(plotDiv.id, JSON.parse(JSON.stringify(chartData.data)), layout, { responsive: true, displayModeBar: false });
}

// ─── Download Chart as PNG ─────────────────────────────────────
function downloadChart(id, title) {
    const el = document.getElementById(id);
    Plotly.downloadImage(el, {
        format: 'png',
        width: 1200,
        height: 800,
        filename: title.trim().replace(/\s+/g, '_') || 'chart'
    });
}

// ─── Download Full Report as JSON ──────────────────────────────
function downloadReport() {
    if (!analysisData) return alert('No report available to download.');
    
    const dataStr = JSON.stringify(analysisData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'ai_data_report.json';
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

// ─── Swap X and Y on the fly ───────────────────────────────────
function toggleRotation(id) {
    const el = document.getElementById(id);
    const data = el.data;
    const layout = el.layout;

    data.forEach(trace => {
        if (['bar', 'box', 'histogram'].includes(trace.type)) {
            // Swap Data
            const oldX = trace.x;
            const oldY = trace.y;
            trace.x = oldY;
            trace.y = oldX;
            // Swap Orientation
            trace.orientation = (trace.orientation === 'h') ? 'v' : 'h';
        }
    });

    // Swap Axis Titles
    const oldXTitle = layout.xaxis.title.text;
    const oldYTitle = layout.yaxis.title.text;
    Plotly.relayout(id, {
        'xaxis.title.text': oldYTitle,
        'yaxis.title.text': oldXTitle
    });
    Plotly.redraw(id);
}

// ─── Dashboard charts (first 6 as preview) ────────────────────
function populateDashboardCharts(charts) {
    const container = document.getElementById('chart-container');
    container.innerHTML = '';
    if (!charts.length) return;
    charts.slice(0, 6).forEach((c, i) => renderChart(c, i, container, 'dash'));
}

// ─── Graphs section (all charts) ──────────────────────────────
function populateGraphsSection(charts) {
    const container = document.getElementById('all-charts-container');
    container.innerHTML = '';
    if (!charts.length) {
        container.innerHTML = '<div class="empty-state" style="grid-column:1/-1">No charts available yet.</div>';
        return;
    }
    const settings = getSettings();
    charts.slice(0, settings.maxCharts).forEach((c, i) => renderChart(c, i, container, 'graph'));

    // Filter button wiring
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

// ─── Data Cleaning section ─────────────────────────────────────
function populateCleaningSection(analysis) {
    const el  = document.getElementById('cleaning-info');
    const missing = analysis.missing;
    const total   = Object.values(missing).reduce((a, b) => a + b, 0);

    const rows = Object.entries(missing).map(([col, cnt]) => `
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
            <td style="padding:10px 14px; color:var(--text-primary)">${col}</td>
            <td style="padding:10px 14px; text-align:center; color:${cnt > 0 ? '#f98d95' : '#38ef7d'}">${cnt}</td>
            <td style="padding:10px 14px; text-align:center">
                <span style="padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600;
                    background:${cnt === 0 ? 'rgba(56,239,125,0.15)' : 'rgba(249,141,149,0.15)'};
                    color:${cnt === 0 ? '#38ef7d' : '#f98d95'}">
                    ${cnt === 0 ? '✅ Clean' : '⚡ Auto-fixed'}
                </span>
            </td>
        </tr>`).join('');

    el.innerHTML = `
        <div style="display:flex; gap:20px; flex-wrap:wrap; margin-bottom:20px">
            <div style="background:rgba(108,99,255,0.1); border:1px solid rgba(108,99,255,0.3); border-radius:10px; padding:14px 22px">
                <div style="font-size:1.8rem; font-weight:800; color:#9d95ff">${Object.keys(missing).length}</div>
                <div style="font-size:0.78rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:1px">Total Columns</div>
            </div>
            <div style="background:rgba(249,141,149,0.1); border:1px solid rgba(249,141,149,0.3); border-radius:10px; padding:14px 22px">
                <div style="font-size:1.8rem; font-weight:800; color:#f98d95">${total}</div>
                <div style="font-size:0.78rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:1px">Missing Values Found & Fixed</div>
            </div>
        </div>
        <table style="width:100%; border-collapse:collapse; font-size:0.9rem">
            <thead>
                <tr style="background:rgba(108,99,255,0.12)">
                    <th style="padding:10px 14px; text-align:left; color:#9d95ff">Column</th>
                    <th style="padding:10px 14px; color:#9d95ff">Missing Values</th>
                    <th style="padding:10px 14px; color:#9d95ff">Status</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>`;
}

// ─── ML section ────────────────────────────────────────────────
function populateMLSection(ml) {
    const el = document.getElementById('ml-result');
    if (!ml || ml.error) {
        el.innerHTML = `<div class="empty-state" style="color:#f98d95">⚠️ ${ml ? ml.error : 'Not available'}</div>`;
        return;
    }
    const score = ml.r2_score !== null ? (parseFloat(ml.r2_score) * 100).toFixed(1) + '%' : 'N/A';
    el.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:20px">
            <div class="kpi-card" style="background:linear-gradient(135deg,rgba(108,99,255,0.2),rgba(62,198,224,0.1));border-color:rgba(108,99,255,0.4)">
                <span class="kpi-label">Target Column</span>
                <span class="kpi-val" style="font-size:1.3rem; color:#9d95ff">${ml.target_column}</span>
            </div>
            <div class="kpi-card" style="background:linear-gradient(135deg,rgba(17,153,142,0.2),rgba(56,239,125,0.1));border-color:rgba(17,153,142,0.4)">
                <span class="kpi-label">Model Used</span>
                <span class="kpi-val" style="font-size:1.1rem; color:#38ef7d">${ml.model_type}</span>
            </div>
            <div class="kpi-card" style="background:linear-gradient(135deg,rgba(247,151,30,0.2),rgba(255,210,0,0.1));border-color:rgba(247,151,30,0.4)">
                <span class="kpi-label">Accuracy (R²)</span>
                <span class="kpi-val" style="color:#ffd200">${score}</span>
            </div>
        </div>
        <div style="margin-top:18px; padding:14px 18px; background:rgba(255,255,255,0.03); border-radius:10px; font-size:0.88rem; color:var(--text-secondary)">
            <strong style="color:var(--text-primary)">Features used: </strong>${(ml.features_used || []).join(', ') || 'all numeric columns'}
        </div>`;
}

// ─── Reports section ─────────────────────────────────────────────
function populateReportsSection(analysis) {
    const el = document.getElementById('result');
    if (!analysis || !analysis.summary) {
        el.innerHTML = '<div class="empty-state">No statistics available.</div>';
        return;
    }

    const summary = analysis.summary;
    const columns = Object.keys(summary);
    if (columns.length === 0) {
        el.innerHTML = '<div class="empty-state">No numeric columns found for statistics.</div>';
        return;
    }

    const statKeys = new Set();
    columns.forEach(col => {
        if (summary[col] && typeof summary[col] === 'object') {
            Object.keys(summary[col]).forEach(k => statKeys.add(k));
        }
    });
    const statsList = Array.from(statKeys);

    let thead = `
        <thead>
            <tr style="background:rgba(108,99,255,0.12); border-bottom: 2px solid rgba(108,99,255,0.3);">
                <th style="padding:14px 18px; text-align:left; color:#9d95ff; font-weight:700; font-size: 0.95rem;">Feature</th>
                ${statsList.map(stat => `<th style="padding:14px 18px; text-align:right; color:#9d95ff; font-weight:700; font-size: 0.95rem; text-transform:capitalize;">${stat}</th>`).join('')}
            </tr>
        </thead>`;

    let tbody = `<tbody>`;
    columns.forEach(col => {
        let statsObj = summary[col];
        if (statsObj && typeof statsObj === 'object') {
            tbody += `<tr style="border-bottom:1px solid rgba(255,255,255,0.05); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.03)'" onmouseout="this.style.background='transparent'">
                <td style="padding:14px 18px; color:var(--text-primary); font-weight: 600; white-space: nowrap;">${col}</td>
                ${statsList.map(stat => {
                    let val = statsObj[stat];
                    if (typeof val === 'number') {
                        val = Number.isInteger(val) ? val.toLocaleString() : parseFloat(val).toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");
                    }
                    return `<td style="padding:14px 18px; text-align:right; color:var(--text-secondary)">${val !== undefined && val !== null ? val : '-'}</td>`;
                }).join('')}
            </tr>`;
        }
    });
    tbody += `</tbody>`;

    el.innerHTML = `
        <div style="overflow-x: auto; background: rgba(30, 30, 35, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <table style="width:100%; border-collapse:collapse; font-size:0.95rem;">
                ${thead}
                ${tbody}
            </table>
        </div>
    `;
}

// ─── Chat with Data section ────────────────────────────────────
async function sendChatQuery() {
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;

    if (!analysisData || !analysisData.file_path) {
        alert("Please upload a dataset first on the Dashboard!");
        return;
    }

    const settings = getSettings();
    if (!settings.geminiKey) {
        alert("Please configure your Google Gemini API Key in the Settings section before chatting.");
        return;
    }

    // Hide empty state
    const emptyState = document.getElementById('chat-empty-state');
    if (emptyState) emptyState.style.display = 'none';

    const messagesBox = document.getElementById('chat-messages');

    // Add user message
    const userDiv = document.createElement('div');
    userDiv.style.background = 'rgba(108, 99, 255, 0.15)';
    userDiv.style.padding = '12px 18px';
    userDiv.style.borderRadius = '12px 12px 0 12px';
    userDiv.style.alignSelf = 'flex-end';
    userDiv.style.maxWidth = '80%';
    userDiv.innerHTML = `<strong style="color:var(--text-primary)">You:</strong> <span style="color:var(--text-secondary)">${query.replace(/</g,"&lt;")}</span>`;
    messagesBox.appendChild(userDiv);

    input.value = '';
    
    // Add loading indicator
    const aiDiv = document.createElement('div');
    aiDiv.style.background = 'rgba(56, 239, 125, 0.1)';
    aiDiv.style.padding = '12px 18px';
    aiDiv.style.borderRadius = '12px 12px 12px 0';
    aiDiv.style.alignSelf = 'flex-start';
    aiDiv.style.maxWidth = '80%';
    aiDiv.innerHTML = `<strong style="color:var(--text-primary)">AI:</strong> <span style="color:var(--text-secondary)"><span class="spinner" style="width:14px;height:14px;border-width:2px;display:inline-block"></span> Thinking...</span>`;
    messagesBox.appendChild(aiDiv);

    // Scroll bottom
    messagesBox.scrollTop = messagesBox.scrollHeight;

    try {
        const response = await fetch(`${settings.apiUrl}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                file_path: analysisData.file_path,
                api_key: settings.geminiKey
            })
        });

        const result = await response.json();
        
        let mdText = result.response || result.detail || "Error from server";
        
        // Simple Markdown parsing for bold/italics
        mdText = mdText.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
        mdText = mdText.replace(/\\*(.*?)\\*/g, '<em>$1</em>');
        mdText = mdText.replace(/\\n/g, '<br>');

        aiDiv.innerHTML = `<strong style="color:var(--text-primary)">AI:</strong> <span style="color:var(--text-secondary); line-height: 1.5;">${mdText}</span>`;
    } catch (err) {
        aiDiv.innerHTML = `<strong style="color:#f98d95">AI Error:</strong> <span style="color:var(--text-secondary)">${err.message}</span>`;
    }
    
    // Scroll bottom
    messagesBox.scrollTop = messagesBox.scrollHeight;
}

// Support Enter key for chat input
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    if(chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatQuery();
            }
        });
    }
});

// ─── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initNav();
    initFileInput();

    const { apiUrl, maxCharts, theme, geminiKey } = getSettings();
    document.getElementById('setting-api-url').value    = apiUrl;
    document.getElementById('setting-max-charts').value = maxCharts;
    document.getElementById('setting-theme').value      = theme;
    document.getElementById('setting-gemini-key').value = geminiKey;
});