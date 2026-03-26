"""
Setup and Installation Script
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required!")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def create_virtual_env():
    """Create virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return
    
    print("📦 Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅ Virtual environment created")


def install_dependencies():
    """Install required packages"""
    print("📥 Installing dependencies...")
    
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # Unix-like
        pip_path = os.path.join("venv", "bin", "pip")
    
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed")


def create_directories():
    """Create necessary directories"""
    dirs = ["tmp_uploads", "output_resumes", "logs"]
    
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Created {dir_name} directory")


def create_env_file():
    """Create .env file from template"""
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        return
    
    print("📝 Creating .env file from template...")
    if os.path.exists(".env.example"):
        with open(".env.example", "r") as f:
            content = f.read()
        with open(".env", "w") as f:
            f.write(content)
        print("✅ .env file created - please fill in your API keys")
    else:
        print("⚠️  .env.example not found")


def verify_installation():
    """Verify installation by importing modules"""
    print("\n🔍 Verifying installation...")
    
    try:
        import telegram
        print("✅ python-telegram-bot installed")
    except ImportError:
        print("❌ python-telegram-bot not installed")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber installed")
    except ImportError:
        print("❌ pdfplumber not installed")
        return False
    
    try:
        import reportlab
        print("✅ reportlab installed")
    except ImportError:
        print("❌ reportlab not installed")
        return False
    
    try:
        import sklearn
        print("✅ scikit-learn installed")
    except ImportError:
        print("❌ scikit-learn not installed")
        return False
    
    print("\n✅ All core dependencies verified!\n")
    return True


def main():
    """Run setup"""
    print("=" * 50)
    print("Resume Analyzer Bot - Setup Script")
    print("=" * 50 + "\n")
    
    check_python_version()
    create_virtual_env()
    create_directories()
    install_dependencies()
    create_env_file()
    
    if verify_installation():
        print("\n" + "=" * 50)
        print("✨ Setup completed successfully!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Edit .env file with your API keys")
        print("2. Activate virtual environment:")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("3. Run the bot:")
        print("   python bot.py")
        print("\n" + "=" * 50)
    else:
        print("\n❌ Setup incomplete - fix errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
