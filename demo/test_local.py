#!/usr/bin/env python3
"""
Local test script for Vercel demo
Run this before deploying to make sure everything works
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def main():
    print("🚀 Testing Vercel Demo Locally\n")
    print("=" * 60)

    # Check if we're in the right directory
    demo_dir = Path(__file__).parent
    if not (demo_dir / "app.py").exists():
        print("❌ Error: Must run from demo/ directory")
        sys.exit(1)

    print("✅ Found demo/app.py")

    # Check Python version
    if sys.version_info < (3, 11):
        print(
            f"⚠️  Warning: Python {sys.version_info.major}.{sys.version_info.minor} detected"
        )
        print("   Recommended: Python 3.11+")
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            check=True,
            cwd=demo_dir,
        )
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Clean old database
    db_file = demo_dir / "demo.db"
    if db_file.exists():
        db_file.unlink()
        print("✅ Cleaned old database")

    # Start server
    print("\n🌐 Starting development server...")
    print("   URL: http://localhost:8000/admin")
    print("   Press Ctrl+C to stop\n")
    print("=" * 60)

    try:
        # Give server time to start
        time.sleep(2)

        # Open browser
        webbrowser.open("http://localhost:8000/admin")

        # Run server
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app:app", "--reload", "--port", "8000"],
            cwd=demo_dir,
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. If everything works, commit your changes")
        print("   2. Deploy to Vercel: vercel --prod")
        print("   3. Visit your live demo!")


if __name__ == "__main__":
    main()
