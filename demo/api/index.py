"""
Vercel serverless handler for FastAPI
"""
from mangum import Mangum
from app import app

# Mangum wraps FastAPI for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")
