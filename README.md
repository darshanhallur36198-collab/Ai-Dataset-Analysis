# AI Autonomous Data Analyst 📊

An AI-driven BI dashboard that automatically cleans, analyzes, and visualizes your datasets (CSV, Excel, JSON).

## 🚀 How to Run in VS Code

I have pre-configured VS Code to make running this project simple:

### Option A: The "One-Click" Way (Recommended)
1.  **Open the "Run and Debug" panel** (Ctrl+Shift+D).
2.  Select **`Full App: Run Both`** from the dropdown at the top.
3.  **Press F5.** 
    *   This will automatically start the Backend server.
    *   It will then open a browser window pointed at `http://localhost:5500`.

### Option B: Using the Terminal (Manual)
If you prefer starting things manually, run these in two separate terminals:

**1. Backend (FastAPI)**
```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000 --reload
```

**2. Frontend (Live Server)**
```powershell
npx -y http-server ./frontend -p 5500
```
*Wait, if you see the website at `http://localhost:5500`, you're good!*

## 🛠️ Requirements
*   Python 3.10+
*   Node.js (for the frontend server)
*   **Gemini API Key:** Configure this in the **Settings** section of the dashboard to use the "Chat with Data" feature.

## ✨ Features
- **Auto-Analysis:** No "Calculate" button needed. Drop a file and it starts.
- **Data Cleaning:** Automatic missing value repair.
- **Visualization Suite:** Interactive charts via Plotly.
- **AI Narrative:** Text-based insights into your data.
- **Chat with Data:** Natural language querying (Power by Gemini).