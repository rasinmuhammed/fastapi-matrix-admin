"""
Live Demo for Vercel - FastAPI Shadcn Admin
Showcases Matrix UI theme and auto_discover feature
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy import String, Integer, Boolean, Text, Float
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from fastapi_shadcn_admin import ShadcnAdmin

# SQLAlchemy Base
class Base(DeclarativeBase):
    pass


# Demo Models - Showcase auto_discover
class BlogPost(Base):
    """Blog posts with title, content, and author"""
    __tablename__ = "blog_posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(100))
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    views: Mapped[int] = mapped_column(Integer, default=0)


class Product(Base):
    """E-commerce products"""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer)
    available: Mapped[bool] = mapped_column(Boolean, default=True)


class Author(Base):
    """Author profiles"""
    __tablename__ = "authors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150))
    bio: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    posts_count: Mapped[int] = mapped_column(Integer, default=0)


class Category(Base):
    """Content categories"""
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


# Create async SQLite engine
engine = create_async_engine(
    "sqlite+aiosqlite:///./demo.db",
    echo=False,
    connect_args={"check_same_thread": False}
)


# Lifespan context for startup/shutdown (serverless compatible)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed demo data
    from sqlalchemy import select, func
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        result = await session.execute(select(func.count()).select_from(BlogPost))
        count = result.scalar()
        
        if count == 0:
            # Add demo blog posts
            session.add_all([
                BlogPost(
                    title="Getting Started with FastAPI Shadcn Admin",
                    content="FastAPI Shadcn Admin provides a beautiful, modern admin interface for your FastAPI applications. With auto-discovery, you can have a fully functional admin panel in minutes!",
                    author="John Doe",
                    published=True,
                    views=1250
                ),
                BlogPost(
                    title="Matrix UI Theme - Dark Mode Done Right",
                    content="Our Matrix-inspired green and black theme isn't just beautiful—it's functional. Terminal-style typography, neon accents, and smooth animations create an immersive experience.",
                    author="Jane Smith",
                    published=True,
                    views=890
                ),
                BlogPost(
                    title="Auto-Discovery: The Magic Behind the Scenes",
                    content="With just one line of code—admin.auto_discover(Base)—all your SQLAlchemy models become fully-featured admin pages. CRUD operations, search, pagination, all automatic!",
                    author="Alice Johnson",
                    published=True,
                    views=1450
                ),
                BlogPost(
                    title="Draft: Upcoming Features",
                    content="We're working on advanced features like file uploads, rich text editing, and custom dashboards. Stay tuned!",
                    author="Bob Wilson",
                    published=False,
                    views=45
                ),
            ])
            
            # Add demo products
            session.add_all([
                Product(
                    name="Premium Laptop",
                    description="High-performance laptop with 16GB RAM and 512GB SSD. Perfect for development and design work.",
                    price=1299.99,
                    stock=15,
                    available=True
                ),
                Product(
                    name="Mechanical Keyboard",
                    description="Cherry MX Blue switches, RGB backlight, programmable macros. The ultimate developer keyboard.",
                    price=159.99,
                    stock=32,
                    available=True
                ),
                Product(
                    name="4K Monitor",
                    description="27-inch 4K IPS display with 144Hz refresh rate. Stunning colors and smooth performance.",
                    price=499.99,
                    stock=8,
                    available=True
                ),
                Product(
                    name="Wireless Mouse",
                    description="Ergonomic wireless mouse with customizable buttons and long battery life.",
                    price=49.99,
                    stock=0,
                    available=False
                ),
            ])
            
            # Add demo authors
            session.add_all([
                Author(
                    name="John Doe",
                    email="john@example.com",
                    bio="Full-stack developer with 10 years of experience. Passionate about clean code and modern web technologies.",
                    active=True,
                    posts_count=1
                ),
                Author(
                    name="Jane Smith",
                    email="jane@example.com",
                    bio="UI/UX designer and frontend developer. Loves creating beautiful, user-friendly interfaces.",
                    active=True,
                    posts_count=1
                ),
                Author(
                    name="Alice Johnson",
                    email="alice@example.com",
                    bio="Backend architect specializing in Python and FastAPI. Open source contributor.",
                    active=True,
                    posts_count=1
                ),
                Author(
                    name="Bob Wilson",
                    email="bob@example.com",
                    bio="Technical writer and developer advocate. Making complex tech simple since 2015.",
                    active=False,
                    posts_count=1
                ),
            ])
            
            # Add demo categories
            session.add_all([
                Category(
                    name="Technology",
                    description="Articles about software development, programming languages, and tech trends.",
                    active=True
                ),
                Category(
                    name="Design",
                    description="UI/UX design, web design, and visual creativity.",
                    active=True
                ),
                Category(
                    name="Tutorial",
                    description="Step-by-step guides and how-to articles.",
                    active=True
                ),
                Category(
                    name="News",
                    description="Latest tech news and industry updates.",
                    active=False
                ),
            ])
            
            await session.commit()
    
    yield  # App runs here
    
    # Shutdown (cleanup if needed)
    await engine.dispose()


# Create FastAPI app with lifespan
app = FastAPI(
    title="FastAPI Shadcn Admin - Live Demo",
    description="Showcasing Matrix UI and Auto-Discovery",
    version="1.0.0",
    lifespan=lifespan
)

# Redirect root to admin
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/admin")


# Initialize admin with read-only mode for public demo
admin = ShadcnAdmin(
    app,
    engine=engine,
    secret_key="demo-live-key-for-vercel-deployment",
    title="FastAPI Shadcn Admin Demo",
    readonly=True  # Read-only mode: visitors can browse but not modify data
)

# 🎯 Auto-discover ALL models with ONE LINE!
admin.auto_discover(Base)
