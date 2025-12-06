"""
Self-contained FastAPI demo for Vercel serverless deployment.
This is a simplified version that doesn't require the main package.
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from mangum import Mangum
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, Float
from sqlalchemy.orm import DeclarativeBase, Session
import os

# SQLAlchemy Base
class Base(DeclarativeBase):
    pass

# Demo Models
class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    author = Column(String(100))
    published = Column(Boolean, default=False)
    views = Column(Integer, default=0)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer)
    available = Column(Boolean, default=True)

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(150))
    bio = Column(Text)
    active = Column(Boolean, default=True)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    active = Column(Boolean, default=True)

# Use in-memory SQLite for serverless
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

# Seed data
with Session(engine) as session:
    session.add_all([
        BlogPost(title="Getting Started with FastAPI Shadcn Admin", content="Modern admin interface...", author="John Doe", published=True, views=1250),
        BlogPost(title="Matrix UI Theme", content="Green and black theme...", author="Jane Smith", published=True, views=890),
        Product(name="Premium Laptop", description="High-performance laptop", price=1299.99, stock=15, available=True),
        Product(name="Mechanical Keyboard", description="Cherry MX switches", price=159.99, stock=32, available=True),
        Author(name="John Doe", email="john@example.com", bio="Full-stack developer", active=True),
        Author(name="Jane Smith", email="jane@example.com", bio="UI/UX designer", active=True),
        Category(name="Technology", description="Tech articles", active=True),
        Category(name="Design", description="Design tips", active=True),
    ])
    session.commit()

# FastAPI app
app = FastAPI(title="FastAPI Shadcn Admin Demo")

# Matrix UI HTML template
MATRIX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Shadcn Admin - Live Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'JetBrains Mono', monospace; background: #000; }
        .matrix-glow { text-shadow: 0 0 10px #10b981, 0 0 20px #10b981, 0 0 30px #10b981; }
        .card-glow { box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .pulse { animation: pulse 2s infinite; }
    </style>
</head>
<body class="bg-black text-emerald-400 min-h-screen">
    <!-- Header -->
    <header class="border-b border-emerald-900/50 bg-black/80 backdrop-blur-sm sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                    <span class="text-emerald-400 text-xl">⚡</span>
                </div>
                <div>
                    <h1 class="text-xl font-bold text-emerald-400 matrix-glow">SHADCN ADMIN</h1>
                    <p class="text-xs text-emerald-600">Matrix UI Demo</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <span class="w-2 h-2 bg-emerald-500 rounded-full pulse"></span>
                <span class="text-emerald-500 text-sm">LIVE</span>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-6 py-8">
        <!-- Welcome Banner -->
        <div class="bg-gradient-to-r from-emerald-900/30 to-black border border-emerald-800/50 rounded-xl p-8 mb-8 card-glow">
            <h2 class="text-3xl font-bold text-emerald-400 matrix-glow mb-4">Welcome to the Matrix</h2>
            <p class="text-emerald-300/70 max-w-2xl">
                This is a live demo of FastAPI Shadcn Admin with the Matrix UI theme.
                Experience the power of auto-discovery and beautiful design.
            </p>
            <div class="mt-6 flex gap-4">
                <a href="https://github.com/rasinmuhammed/fastapi-shadcn-admin" target="_blank" 
                   class="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-black font-semibold rounded-lg transition-all">
                    ⭐ Star on GitHub
                </a>
                <a href="https://pypi.org/project/fastapi-shadcn-admin/" target="_blank"
                   class="px-6 py-2 border border-emerald-600 text-emerald-400 hover:bg-emerald-600/20 rounded-lg transition-all">
                    📦 PyPI Package
                </a>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {stats}
        </div>

        <!-- Models Section -->
        <h3 class="text-xl font-bold text-emerald-400 mb-4">📊 Auto-Discovered Models</h3>
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {models}
        </div>

        <!-- Features Section -->
        <h3 class="text-xl font-bold text-emerald-400 mb-4">✨ Key Features</h3>
        <div class="grid md:grid-cols-3 gap-4 mb-8">
            <div class="bg-emerald-900/20 border border-emerald-800/50 rounded-xl p-6">
                <div class="text-2xl mb-3">🔍</div>
                <h4 class="font-bold text-emerald-300 mb-2">Auto-Discovery</h4>
                <p class="text-emerald-600 text-sm">One line of code registers all your SQLAlchemy models</p>
            </div>
            <div class="bg-emerald-900/20 border border-emerald-800/50 rounded-xl p-6">
                <div class="text-2xl mb-3">🎨</div>
                <h4 class="font-bold text-emerald-300 mb-2">Matrix Theme</h4>
                <p class="text-emerald-600 text-sm">Stunning green/black aesthetic with neon accents</p>
            </div>
            <div class="bg-emerald-900/20 border border-emerald-800/50 rounded-xl p-6">
                <div class="text-2xl mb-3">⚡</div>
                <h4 class="font-bold text-emerald-300 mb-2">Zero Node.js</h4>
                <p class="text-emerald-600 text-sm">Pure Python - no npm, no webpack, just pip install</p>
            </div>
        </div>

        <!-- Code Example -->
        <h3 class="text-xl font-bold text-emerald-400 mb-4">💻 Quick Start</h3>
        <div class="bg-gray-900/80 border border-emerald-800/50 rounded-xl p-6 mb-8 overflow-x-auto">
            <pre class="text-sm"><code class="text-emerald-300"><span class="text-emerald-600"># Install</span>
pip install fastapi-shadcn-admin

<span class="text-emerald-600"># Use</span>
<span class="text-purple-400">from</span> fastapi_shadcn_admin <span class="text-purple-400">import</span> ShadcnAdmin

admin = ShadcnAdmin(app, engine=engine)
admin.auto_discover(Base)  <span class="text-emerald-600"># ✨ Magic!</span></code></pre>
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-emerald-900/50 py-8 mt-12">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <p class="text-emerald-600 text-sm">
                FastAPI Shadcn Admin v0.2.0 • MIT License • 
                <a href="https://github.com/rasinmuhammed/fastapi-shadcn-admin" class="text-emerald-400 hover:underline">GitHub</a>
            </p>
        </div>
    </footer>
</body>
</html>
"""

def get_stats_html():
    with Session(engine) as session:
        blog_count = session.query(BlogPost).count()
        product_count = session.query(Product).count()
        author_count = session.query(Author).count()
        category_count = session.query(Category).count()
    
    stats = [
        ("BlogPosts", blog_count, "📝"),
        ("Products", product_count, "📦"),
        ("Authors", author_count, "👤"),
        ("Categories", category_count, "🏷️"),
    ]
    
    html = ""
    for name, count, icon in stats:
        html += f"""
        <div class="bg-emerald-900/20 border border-emerald-800/50 rounded-xl p-4 card-glow">
            <div class="flex items-center gap-3">
                <span class="text-2xl">{icon}</span>
                <div>
                    <p class="text-2xl font-bold text-emerald-400">{count}</p>
                    <p class="text-xs text-emerald-600">{name}</p>
                </div>
            </div>
        </div>
        """
    return html

def get_models_html():
    models = [
        ("BlogPost", "Blog posts with title, content, author", "📝", 2),
        ("Product", "E-commerce products with pricing", "📦", 2),
        ("Author", "Author profiles with bio", "👤", 2),
        ("Category", "Content categories", "🏷️", 2),
    ]
    
    html = ""
    for name, desc, icon, count in models:
        html += f"""
        <div class="bg-emerald-900/20 border border-emerald-800/50 rounded-xl p-5 hover:border-emerald-500/50 transition-all cursor-pointer">
            <div class="flex items-center gap-3 mb-3">
                <span class="text-xl">{icon}</span>
                <h4 class="font-bold text-emerald-300">{name}</h4>
            </div>
            <p class="text-emerald-600 text-sm mb-3">{desc}</p>
            <div class="flex items-center gap-2 text-xs text-emerald-500">
                <span class="bg-emerald-500/20 px-2 py-1 rounded">{count} records</span>
                <span class="bg-emerald-500/20 px-2 py-1 rounded">Read-only</span>
            </div>
        </div>
        """
    return html

@app.get("/", response_class=HTMLResponse)
async def root():
    html = MATRIX_HTML.format(stats=get_stats_html(), models=get_models_html())
    return HTMLResponse(content=html)

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Matrix is alive!"}

# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
