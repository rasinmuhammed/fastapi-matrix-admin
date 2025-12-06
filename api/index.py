from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        html = """<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Shadcn Admin Demo</title>
    <style>
        body { 
            font-family: 'Courier New', monospace; 
            background: #000; 
            color: #10b981; 
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container { text-align: center; padding: 2rem; }
        h1 { font-size: 2.5rem; text-shadow: 0 0 10px #10b981; }
        .card { 
            background: rgba(16, 185, 129, 0.1); 
            border: 1px solid #10b981; 
            padding: 1rem; 
            margin: 0.5rem;
            border-radius: 8px;
            display: inline-block;
            min-width: 120px;
        }
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: #10b981;
            color: #000;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            margin: 0.5rem;
        }
        .btn-outline {
            background: transparent;
            border: 1px solid #10b981;
            color: #10b981;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ MATRIX ADMIN</h1>
        <p>FastAPI Shadcn Admin - Live Demo</p>
        
        <div style="margin: 2rem 0;">
            <div class="card"><strong>4</strong><br><small>Models</small></div>
            <div class="card"><strong>8</strong><br><small>Records</small></div>
        </div>
        
        <div style="margin: 1.5rem 0; text-align: left; max-width: 300px; margin-left: auto; margin-right: auto;">
            <div class="card" style="display: block; margin: 0.5rem 0;">📝 BlogPost - Auto-discovered</div>
            <div class="card" style="display: block; margin: 0.5rem 0;">📦 Product - Auto-discovered</div>
            <div class="card" style="display: block; margin: 0.5rem 0;">👤 Author - Auto-discovered</div>
            <div class="card" style="display: block; margin: 0.5rem 0;">🏷️ Category - Auto-discovered</div>
        </div>
        
        <a href="https://github.com/rasinmuhammed/fastapi-shadcn-admin" class="btn">⭐ GitHub</a>
        <a href="https://pypi.org/project/fastapi-shadcn-admin/" class="btn btn-outline">📦 PyPI</a>
        
        <p style="margin-top: 2rem; opacity: 0.7;">pip install fastapi-shadcn-admin</p>
    </div>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
