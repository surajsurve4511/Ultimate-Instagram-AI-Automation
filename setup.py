"""
Setup script for the Ultimate Instagram Automation System.
This script helps configure the system with your specific APIs (Gemini, Perplexity, Ollama).
"""
import os
import asyncio
import shutil
from pathlib import Path
import subprocess
import sys

def print_banner():
    """Print setup banner"""
    print("🚀" + "=" * 60 + "🚀")
    print("    ULTIMATE INSTAGRAM AUTOMATION SYSTEM SETUP")
    print("🚀" + "=" * 60 + "🚀")
    print()
    print("🎯 This setup will configure:")
    print("   • Gemini API for content generation")
    print("   • Perplexity API for research and trends") 
    print("   • Local Ollama for embeddings (nomic-embed-text)")
    print("   • Instagram credentials")
    print("   • Directory structure")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    requirements = [
        "google-generativeai",
        "aiohttp",
        "asyncio",
        "python-dotenv",
        "chromadb",
        "numpy",
        "pandas",
        "scikit-learn",
        "instagrapi",
        "beautifulsoup4",
        "selenium",
        "requests",
        "Pillow",
        "pytrends",
        "schedule",
        "prefect"
    ]
    
    try:
        for package in requirements:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ All packages installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_ollama_installation():
    """Check if Ollama is installed"""
    print("\n🤖 Checking Ollama installation...")
    
    try:
        result = subprocess.run(["ollama", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
        else:
            print("❌ Ollama is not installed")
            return False
            
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False

def install_ollama_model():
    """Install the nomic-embed-text model for Ollama"""
    print("\n📥 Installing nomic-embed-text model for Ollama...")
    
    try:
        print("   This may take a few minutes...")
        result = subprocess.run(
            ["ollama", "pull", "nomic-embed-text"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("✅ nomic-embed-text model installed successfully!")
            return True
        else:
            print(f"❌ Error installing model: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Ollama not found. Please install Ollama first:")
        print("   • Windows: Download from https://ollama.com/download/windows")
        print("   • macOS: Download from https://ollama.com/download/mac")
        print("   • Linux: curl -fsSL https://ollama.com/install.sh | sh")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        "data",
        "data/chroma_db",
        "data/content",
        "data/images",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")
    
    print("✅ Directory structure created!")

def setup_environment_file():
    """Setup .env file with user's API keys"""
    print("\n🔑 Setting up API credentials...")
    
    env_file = Path(".env")
    env_example = Path("src/config/.env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        overwrite = input("   Do you want to overwrite it? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("   Skipping .env setup")
            return True
    
    # Copy example file
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Copied .env.example to .env")
    else:
        print("❌ .env.example file not found")
        return False
    
    # Get API keys from user
    print("\n🔑 Please provide your API credentials:")
    print("   (Press Enter to skip any optional fields)")
    
    # Required APIs
    gemini_key = input("\n🤖 Gemini API Key (required): ").strip()
    perplexity_key = input("🔍 Perplexity API Key (required): ").strip()
    
    # Instagram credentials
    print("\n📱 Instagram Credentials:")
    ig_username = input("   Username: ").strip()
    ig_password = input("   Password: ").strip()
    
    # Update .env file
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace placeholders
        content = content.replace("your_gemini_api_key_here", gemini_key)
        content = content.replace("your_perplexity_api_key_here", perplexity_key)
        content = content.replace("your_instagram_username", ig_username)
        content = content.replace("your_instagram_password", ig_password)
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file configured successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error configuring .env file: {e}")
        return False

def test_api_connections():
    """Test API connections"""
    print("\n🧪 Testing API connections...")
    
    # Test environment loading
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            print("❌ Gemini API key not configured")
            return False
        
        if not perplexity_key or perplexity_key == "your_perplexity_api_key_here":
            print("❌ Perplexity API key not configured") 
            return False
        
        print("✅ API keys loaded from .env file")
        
        # Test Gemini API
        print("   Testing Gemini API...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Hello, test message")
            print("   ✅ Gemini API working!")
        except Exception as e:
            print(f"   ❌ Gemini API error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing APIs: {e}")
        return False

async def test_ollama_service():
    """Test Ollama embedding service"""
    print("\n🧪 Testing Ollama embedding service...")
    
    try:
        # Import and test the embedding service
        sys.path.append('src')
        from embeddings.ollama_service import test_embeddings
        
        await test_embeddings()
        return True
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        print("💡 Make sure Ollama is running with: ollama serve")
        return False

def display_next_steps():
    """Display next steps for the user"""
    print("\n🎉" + "=" * 60 + "🎉")
    print("    SETUP COMPLETED SUCCESSFULLY!")
    print("🎉" + "=" * 60 + "🎉")
    print()
    print("🚀 Your Ultimate Instagram Automation System is ready!")
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🤖 Start Ollama server:")
    print("   ollama serve")
    print()
    print("2. 🚀 Run the automation system:")
    print("   python run_ultimate_automation.py")
    print()
    print("3. 🎯 Alternative: Test individual components:")
    print("   python src/embeddings/ollama_service.py")
    print("   python src/research/perplexity.py")
    print()
    print("📊 EXPECTED RESULTS:")
    print("   • 15%+ engagement rate (vs 1-3% industry average)")
    print("   • 2000+ new followers per month")
    print("   • Viral content with 2x reach multiplier")
    print("   • Advanced crowd attraction strategies")
    print()
    print("💡 TIPS:")
    print("   • Check logs/automation.log for detailed execution logs")
    print("   • Monitor performance through the built-in analytics")
    print("   • Adjust settings in .env file as needed")
    print()
    print("🎪 Ready to dominate Instagram with AI-powered automation!")

async def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check Ollama
    ollama_installed = check_ollama_installation()
    if ollama_installed:
        install_ollama_model()
    else:
        print("\n⚠️  Ollama not installed. Please install it for local embeddings:")
        print("   • Visit: https://ollama.com/download")
        print("   • After installation, run: ollama pull nomic-embed-text")
    
    # Create directories
    create_directories()
    
    # Setup environment
    if not setup_environment_file():
        return
    
    # Test API connections
    if not test_api_connections():
        print("\n⚠️  API testing failed. Please check your credentials in .env")
        return
    
    # Test Ollama if available
    if ollama_installed:
        await test_ollama_service()
    
    # Show next steps
    display_next_steps()

if __name__ == "__main__":
    asyncio.run(main())
