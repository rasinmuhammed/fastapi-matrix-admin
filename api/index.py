"""
Ultra-minimal FastAPI demo for Vercel
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mangum import Mangum

app = FastAPI()

MATRIX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Shadcn Admin Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { font-family: 'Courier New', monospace; background: #000; }</style>
</head>
<body class="bg-black text-emerald-400 min-h-screen flex items-center justify-center">
    <div class="text-center p-8">
        <h1 class="text-4xl font-bold mb-4" style="text-shadow: 0 0 10px #10b981;">⚡ MATRIX ADMIN</h1>
        <p class="text-emerald-300 mb-6">FastAPI Shadcn Admin - Live Demo</p>
        
        <div class="grid grid-cols-2 gap-4 max-w-md mx-auto mb-8">
            <div class="bg-emerald-900/30 border border-emerald-700 rounded-lg p-4">
                <p class="text-2xl font-bold">4</p>
                <p class="text-sm text-emerald-500">Models</p>
            </div>
            <div class="bg-emerald-900/30 border border-emerald-700 rounded-lg p-4">
                <p class="text-2xl font-bold">8</p>
                <p class="text-sm text-emerald-500">Records</p>
            </div>
        </div>
        
        <div class="space-y-2 text-left max-w-md mx-auto mb-8">
            <div class="bg-emerald-900/20 border border-emerald-800 rounded p-3">📝 BlogPost - 2 records</div>
            <div class="bg-emerald-900/20 border border-emerald-800 rounded p-3">📦 Product - 2 records</div>
            <div class="bg-emerald-900/20 border border-emerald-800 rounded p-3">👤 Author - 2 records</div>
            <div class="bg-emerald-900/20 border border-emerald-800 rounded p-3">🏷️ Category - 2 records</div>
        </div>
        
        <div class="space-x-4">
            <a href="https://github.com/rasinmuhammed/fastapi-shadcn-admin" 
               class="inline-block px-6 py-2 bg-emerald-600 text-black font-bold rounded hover:bg-emerald-500">
                ⭐ GitHub
            </a>
            <a href="https://pypi.org/project/fastapi-shadcn-admin/" 
               class="inline-block px-6 py-2 border border-emerald-600 rounded hover:bg-emerald-600/20">
                📦 PyPI
            </a>
        </div>
        
        <p class="mt-8 text-emerald-600 text-sm">pip install fastapi-shadcn-admin</p>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=MATRIX_HTML)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

handler = Mangum(app, lifespan="off")
