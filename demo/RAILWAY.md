# Railway Deployment - FastAPI Matrix Admin Demo

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/rasinmuhammed/fastapi-matrix-admin)

### Manual Deployment

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login to Railway:**
```bash
railway login
```

3. **Deploy:**
```bash
railway init
railway up
```

4. **Get your URL:**
```bash
railway open
```

### Environment Variables

No environment variables required! The demo uses SQLite and works out of the box.

### What Gets Deployed

- **FastAPI app** with Matrix UI theme
- **4 auto-discovered models** (BlogPost, Product, Author, Category)
- **SQLite database** with pre-seeded demo data
- **Read-only mode** for public safety

### Local Development

```bash
cd demo
pip install -r requirements.txt
python app.py
# Visit http://localhost:8000/admin
```

### Features

✨ Matrix green/black theme  
🔍 Auto-discovery with `admin.auto_discover(Base)`  
📝 Full CRUD operations  
🎨 Smooth animations and micro-interactions  
⚡ Instant startup with seed data

### Tech Stack

- FastAPI
- SQLAlchemy 2.0 (async)
- SQLite (aiosqlite)
- Jinja2 templates
- Tailwind CSS (CDN)
- HTMX for dynamic interactions

Enjoy your live demo! 🚀
