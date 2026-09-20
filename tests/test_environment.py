"""
Test script to verify all required packages are installed correctly.
Run this to confirm your environment is set up properly.
"""
import sys

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing package imports...")
    print("=" * 60)
    
    packages_to_test = [
        ('google.generativeai', 'Gemini AI'),
        ('aiohttp', 'Async HTTP'),
        ('chromadb', 'ChromaDB'),
        ('instagrapi', 'Instagram API'),
        ('beautifulsoup4', 'BeautifulSoup'),
        ('selenium', 'Selenium'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('sklearn', 'Scikit-learn'),
        ('prefect', 'Prefect'),
        ('pytrends', 'Google Trends'),
        ('textstat', 'Textstat'),
        ('tweepy', 'Tweepy'),
        ('yfinance', 'Yahoo Finance'),
        ('textblob', 'TextBlob'),
        ('flask', 'Flask'),
    ]
    
    results = []
    for package_name, display_name in packages_to_test:
        try:
            if package_name == 'beautifulsoup4':
                import bs4
                status = '✅'
            elif package_name == 'sklearn':
                import sklearn
                status = '✅'
            else:
                __import__(package_name)
                status = '✅'
            
            print(f"{status} {display_name:<25} - Installed")
            results.append(True)
            
        except ImportError as e:
            print(f"❌ {display_name:<25} - NOT FOUND")
            results.append(False)
    
    print("=" * 60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Results: {success_count}/{total_count} packages successfully imported")
    
    if success_count == total_count:
        print("🎉 All packages are installed correctly!")
        return True
    else:
        print("⚠️  Some packages are missing. Please run: pip install -r requirements.txt")
        return False

def test_custom_modules():
    """Test custom module imports"""
    print("\n🧪 Testing custom modules...")
    print("=" * 60)
    
    modules_to_test = [
        ('src.config.settings', 'Settings'),
        ('src.embeddings.ollama_service', 'Ollama Embeddings'),
        ('src.research.perplexity', 'Perplexity Research'),
        ('src.content.content_curator', 'Content Curator'),
        ('src.posting.instagram_poster', 'Instagram Poster'),
        ('src.database.vector_store', 'Vector Store'),
        ('src.viral.content_strategies', 'Viral Strategies'),
        ('src.trends.trend_detector', 'Trend Detector'),
        ('src.creative.advanced_content', 'Creative Content'),
        ('src.creative.future_ai', 'Future AI'),
        ('src.crowd.revolutionary_attraction', 'Crowd Magnet'),
        ('src.analytics.engagement_optimizer', 'Analytics'),
        ('src.orchestration.ultimate_master', 'Ultimate Master'),
    ]
    
    results = []
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name:<25} - OK")
            results.append(True)
            
        except ImportError as e:
            print(f"❌ {display_name:<25} - FAILED: {str(e)}")
            results.append(False)
    
    print("=" * 60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Results: {success_count}/{total_count} custom modules successfully imported")
    
    if success_count == total_count:
        print("🎉 All custom modules are working correctly!")
        return True
    else:
        print("⚠️  Some custom modules have issues.")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🧪 Testing environment configuration...")
    print("=" * 60)
    
    import os
    from pathlib import Path
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found")
        
        # Check for required variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'GEMINI_API_KEY',
            'PERPLEXITY_API_KEY',
            'INSTAGRAM_USERNAME',
            'INSTAGRAM_PASSWORD'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value and value != f'your_{var.lower().replace("_", "_")}':
                print(f"✅ {var:<30} - Configured")
            else:
                print(f"⚠️  {var:<30} - Not configured")
    else:
        print("❌ .env file not found")
    
    print("=" * 60)

def main():
    """Run all tests"""
    print("\n🚀 ULTIMATE INSTAGRAM AUTOMATION SYSTEM")
    print("🧪 Environment Test Suite")
    print("=" * 60)
    print()
    
    # Test package imports
    packages_ok = test_imports()
    
    # Test custom modules
    modules_ok = test_custom_modules()
    
    # Test environment
    test_environment()
    
    print("\n" + "=" * 60)
    if packages_ok and modules_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your environment is ready to run the automation system!")
        print("\n💡 Next steps:")
        print("   1. Configure your API keys in .env file")
        print("   2. Start Ollama: ollama serve")
        print("   3. Run: python run_ultimate_automation.py")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("💡 Please fix the issues above before running the system")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
