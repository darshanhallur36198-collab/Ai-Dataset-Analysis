/* ════════════════════════════════════════════════
   AI Autonomous Data Analyst — app.js
   Full SPA navigation + analysis pipeline
   ════════════════════════════════════════════════ */

// ─── Cached analysis data ─────────────────────────────────────────
let analysisData = null;

// ─── Settings (with defaults) ─────────────────────────────────────
function getSettings() {
    return {
        apiUrl:    localStorage.getItem('api_url')       || 'http://127.0.0.1:8000',
        maxCharts: parseInt(localStorage.getItem('max_charts') || '12'),
        theme:     localStorage.getItem('chart_theme')   || 'plotly_dark',
    };
}

function saveSettings() {
    localStorage.setItem('api_url',      document.getElementById('setting-api-url').value.trim());
    localStorage.setItem('max_charts',   document.getElementById('setting-max-charts').value);
    localStorage.setItem('chart_theme',  document.getElementById('setting-theme').value);
    const msg = document.getElementById('settings-msg');
    msg.style.display = 'block';
    setTimeout(() => msg.style.display = 'none', 2500);
}

// ─── Section Titles ───────────────────────────────────────────────
const SECTION_META = {
    'section-dashboard': { title: 'Data Analytics Overview',  sub: 'Upload a dataset to begin autonomous analysis' },
    'section-graphs':    { title: 'Visualization Suite',      sub: 'Interactive charts generated from your dataset'  },
    'section-cleaning':  { title: 'Data Cleaning Report',     sub: 'Automatic detection and repair of data issues'   },
    'section-ml':        { title: 'ML Predictions',           sub: 'Automated machine learning on your dataset'      },
    'section-reports':   { title: 'Statistical Report',       sub: 'Full dataset summary and descriptive statistics' },
    'section-settings':  { title: 'Settings',                 sub: 'Configure API endpoint and dashboard preferences'},
};

// ─── Navigation ───────────────────────────────────────────────────
function initNav() {
    const items = document.querySelectorAll('.nav-item');
    items.forEach(item => {
        item.addEventListener('click', () => {
            const target = item.dataset.section;

            // toggle active class on nav items
            items.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            // show/hide sections
            document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active-section'));
            document.getElementById(target).classList.add('active-section');

            // update header
            const meta = SECTION_META[target];
            if (meta) {
                document.getElementById('page-title').textContent    = meta.title;
                document.getElementById('page-subtitle').textContent = meta.sub;
            }

            // If user clicks Graphs after upload, re-populate if needed
            if (target === 'section-graphs' && analysisData) populateGraphsSection(analysisData.charts);
        });
    });
}

// ─── File input ───────────────────────────────────────────────────
function initFileInput() {
    const fileInput  = document.getElementById('dataset');
    const fileLabel  = document.getElementById('file-name');
    const analyzeBtn = document.getElementById('analyze-btn');
    const dropZone   = document.getElementById('drop-zone');

    fileInput.addEventListener('change', e => {
        if (e.target.files.length > 0) {
            fileLabel.textContent  = `📄 ${e.target.files[0].name}`;
            analyzeBtn.disabled    = false;
        }
    });

    ['dragenter','dragover','dragleave','drop'].forEach(evt => {
        dropZone.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
    });
    ['dragenter','dragover'].forEach(e => dropZone.addEventListener(e, () => dropZone.classList.add('dragover')));
    ['dragleave','drop'].forEach(e => dropZone.addEventListener(e, () => dropZone.classList.remove('dragover')));

    dropZone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

// ─── Populate KPI bar ─────────────────────────────────────────────
function populateKPIs(analysis) {
    const missingTotal = Object.values(analysis.missing).reduce((a, b) => a + b, 0);
    const health = Math.max(0, 100 - (missingTotal / (analysis.rows * analysis.columns) * 100));
    document.getElementById('kpi-rows').textContent     = analysis.rows.toLocaleString();
    document.getElementById('kpi-cols').textContent     = analysis.columns;
    document.getElementById('kpi-health').textContent   = `${Math.round(health)}%`;
    document.getElementById('kpi-insights').textContent = analysis.insights.length;
    document.getElementById('kpi-box').style.display    = 'grid';
}

// ─── AI Insight bubbles ───────────────────────────────────────────
function populateInsights(insights) {
    const panel   = document.getElementById('ai-assistant');
    const bubbles = document.getElementById('ai-bubbles');
    panel.style.display = 'block';
    bubbles.innerHTML   = '';
    insights.forEach((text, i) => {
        setTimeout(() => {
            const div = document.createElement('div');
            div.className   = 'bubble';
            div.textContent = text;
            bubbles.appendChild(div);
        }, i * 280);
    });
}

// ─── Render a Plotly chart inside a card ─────────────────────────
function renderChart(chartData, index, container) {
    const settings = getSettings();
    const card = document.createElement('div');
    card.className = 'chart-card';

    const header = document.createElement('div');
    header.className   = 'chart-header';
    header.textContent = (chartData.layout.title && chartData.layout.title.text) || `Chart ${index + 1}`;

    const plotDiv = document.createElement('div');
    plotDiv.id        = `chart_${container.id}_${index}`;
    plotDiv.className = 'plotly-box';

    card.appendChild(header);
    card.appendChild(plotDiv);
    container.appendChild(card);

    const layout = { ...chartData.layout, template: settings.theme, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)' };
    Plotly.newPlot(plotDiv.id, chartData.data, layout, { responsive: true });
}

// ─── Dashboard charts (after upload) ─────────────────────────────
function populateDashboardCharts(charts) {
    const container = document.getElementById('chart-container');
    container.innerHTML = '';
    const settings = getSettings();
    charts.slice(0, settings.maxCharts).forEach((c, i) => renderChart(c, i, container));
}

// ─── Graphs section ───────────────────────────────────────────────
function populateGraphsSection(charts) {
    const container = document.getElementById('all-charts-container');
    container.innerHTML = '';
    if (!charts || charts.length === 0) {
        container.innerHTML = '<div class="empty-state" style="grid-column:1/-1">📊 No charts yet — run an analysis first.</div>';
        return;
    }
    const settings = getSettings();
    charts.slice(0, settings.maxCharts).forEach((c, i) => renderChart(c, i, container));

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            // (simple visual filter — can be extended by tagging chart types)
        });
    });
}

// ─── Data Cleaning section ────────────────────────────────────────
function populateCleaningSection(analysis) {
    const el = document.getElementById('cleaning-info');
    const missing = analysis.missing;
    const totalMissing = Object.values(missing).reduce((a, b) => a + b, 0);

    const rows = Object.entries(missing).map(([col, cnt]) => `
        <tr>
            <td style="padding:8px 12px;">${col}</td>
            <td style="padding:8px 12px; text-align:center;">${cnt}</td>
            <td style="padding:8px 12px; text-align:center;">
                <span style="color:${cnt === 0 ? '#38ef7d' : '#f64f59'}">
                    ${cnt === 0 ? '✅ Clean' : '⚠️ Had missing'}
                </span>
            </td>
        </tr>`).join('');

    el.innerHTML = `
        <p style="margin-bottom:14px; color:var(--text-secondary)">
            Total missing values found: <strong style="color:#ffd200">${totalMissing}</strong>
            &nbsp;|&nbsp; All filled automatically using median / "Unknown" fill strategy.
        </p>
        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
            <thead>
                <tr style="background:rgba(108,99,255,0.15); color:#9d95ff;">
                    <th style="padding:10px 12px; text-align:left">Column</th>
                    <th style="padding:10px 12px">Missing Before</th>
                    <th style="padding:10px 12px">Status</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>`;
}

// ─── ML section ───────────────────────────────────────────────────
function populateMLSection(ml) {
    const el = document.getElementById('ml-result');
    if (!ml || ml.error) {
        el.innerHTML = `<div class="empty-state" style="color:#f98d95">⚠️ ${ml ? ml.error : 'ML not available'}</div>`;
        return;
    }
    const score = ml.r2_score !== null ? (ml.r2_score * 100).toFixed(1) + '%' : 'N/A';
    const features = (ml.features_used || []).join(', ');
    el.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:20px; margin-top:10px">
            <div class="kpi-card" style="background:linear-gradient(135deg,rgba(108,99,255,0.25),rgba(62,198,224,0.1));border-color:rgba(108,99,255,0.4)">
                <span class="kpi-label">Target Column</span>
                <span class="kpi-val" style="font-size:1.4rem; color:#9d95ff">${ml.target_column}</span>
            </div>
            <div class="kpi-card" style="background:linear-gradient(135deg,rgba(17,153,142,0.25),rgba(56,239,125,0.1));border-color:rgba(17,153,142,0.4)">
                <span class="kpi-label">Model</span>
                <span class="kpi-val" style="font-size:1.1rem; color:#38ef7d">${ml.model_type}</span>
            </div>
            <div class="kpi-card" style="background:linear-gradient(135deg,rgba(247,151,30,0.25),rgba(255,210,0,0.1));border-color:rgba(247,151,30,0.4)">
                <span class="kpi-label">Accuracy (R²)</span>
                <span class="kpi-val" style="font-size:1.8rem; color:#ffd200">${score}</span>
            </div>
        </div>
        <div style="margin-top:20px; padding:14px; background:rgba(255,255,255,0.03); border-radius:10px; font-size:0.88rem; color:var(--text-secondary)">
            <strong style="color:var(--text-primary)">Features used:</strong> ${features}
        </div>`;
}

// ─── Upload & Analysis Pipeline ───────────────────────────────────
async function upload() {
    const fileInput  = document.getElementById('dataset');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loader     = document.getElementById('loader');

    if (!fileInput.files || fileInput.files.length === 0) return;

    const settings = getSettings();
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    analyzeBtn.disabled        = true;
    loader.style.display       = 'flex';

    try {
        const response = await fetch(`${settings.apiUrl}/upload`, { method: 'POST', body: formData });
        const result   = await response.json();

        if (!response.ok || result.status === 'error') {
            throw new Error(result.message || 'Analysis failed');
        }

        analysisData = result;

        // 1. KPIs
        populateKPIs(result.analysis);

        // 2. Dashboard: AI bubbles + charts
        populateInsights(result.analysis.insights);
        populateDashboardCharts(result.charts || []);

        // 3. Pre-populate other sections (silent)
        populateGraphsSection(result.charts || []);
        populateCleaningSection(result.analysis);
        populateMLSection(result.ml_prediction);

        // 4. Reports
        document.getElementById('result').textContent = JSON.stringify(result.analysis, null, 2);

    } catch (err) {
        alert('❌ ' + err.message);
    } finally {
        loader.style.display = 'none';
        analyzeBtn.disabled  = false;
    }
}

// ─── Init ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initNav();
    initFileInput();

    // Restore settings UI
    const { apiUrl, maxCharts, theme } = getSettings();
    document.getElementById('setting-api-url').value   = apiUrl;
    document.getElementById('setting-max-charts').value = maxCharts;
    document.getElementById('setting-theme').value     = theme;
});