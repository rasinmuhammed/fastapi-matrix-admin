"""
Simple Test Application for FastAPI Matrix Admin
Demonstrates basic usage with SQLAlchemy models
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from sqlalchemy import String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from fastapi_matrix_admin import MatrixAdmin
from fastapi_matrix_admin.auth.models import AdminUserMixin, pwd_context


# SQLAlchemy Base
class Base(DeclarativeBase):
    pass


# Admin User Model
class User(AdminUserMixin, Base):
    __tablename__ = "users"


# Test Models
class Company(Base):
    """Company model"""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    industry: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    employees: Mapped[list["Employee"]] = relationship(back_populates="company")

    def __admin_repr__(self):
        return self.name


class Employee(Base):
    """Employee model"""

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150))
    salary: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="employees")

    def __admin_repr__(self):
        return f"{self.name} ({self.email})"


# Create async engine
engine = create_async_engine(
    "sqlite+aiosqlite:///./test_app.db",
    echo=False,
)


# Lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        # Create admin user
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin = User(
                username="admin",
                email="admin@test.com",
                password_hash=pwd_context.hash("admin123"),
                roles=["admin"],
                is_superuser=True,
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            print("✅ Created admin user: admin / admin123")

        # Seed test data
        result = await session.execute(select(Company))
        if not result.scalars().first():
            # Companies
            c1 = Company(name="TechCorp", industry="Technology", active=True)
            c2 = Company(name="FinanceHub", industry="Finance", active=True)
            session.add_all([c1, c2])
            await session.flush()

            # Employees
            employees = [
                Employee(
                    name="John Doe",
                    email="john@techcorp.com",
                    salary=85000,
                    company_id=c1.id,
                ),
                Employee(
                    name="Jane Smith",
                    email="jane@techcorp.com",
                    salary=95000,
                    company_id=c1.id,
                ),
                Employee(
                    name="Bob Johnson",
                    email="bob@financehub.com",
                    salary=78000,
                    company_id=c2.id,
                ),
            ]
            session.add_all(employees)
            await session.commit()
            print("✅ Seeded test data")

    yield  # App runs

    # Shutdown
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Test App - FastAPI Matrix Admin",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return RedirectResponse(url="/admin")


# Initialize Matrix Admin
admin = MatrixAdmin(
    app,
    engine=engine,
    secret_key="test-secret-key-min-32-characters-long",
    title="Test Admin Panel",
)

# Register models
admin.register(
    Company,
    name="Companies",
    icon="briefcase",
    list_display=["id", "name", "industry", "active"],
    searchable_fields=["name", "industry"],
    filter_fields=["active", "industry"],
)

admin.register(
    Employee,
    name="Employees",
    icon="users",
    list_display=["id", "name", "email", "company", "salary", "active"],
    searchable_fields=["name", "email"],
    filter_fields=["active", "company"],
)

admin.register(
    User,
    name="Admin Users",
    icon="shield",
    list_display=["username", "email", "is_active", "roles"],
    readonly=True,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
