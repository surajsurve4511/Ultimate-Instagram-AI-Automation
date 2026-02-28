"""
Master Test Suite Runner
Runs all component tests sequentially and provides detailed reporting
"""
import subprocess
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_section(text):
    """Print a formatted section"""
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80 + "\n")

def run_test(test_name, test_file):
    """Run a single test file and capture results"""
    print_section(f"Running {test_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per test
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print(f"❌ Test TIMEOUT after 2 minutes")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Test FAILED with exception: {str(e)}")
        return False, "", str(e)

def main():
    """Run all tests and generate summary"""
    print_header("🚀 INSTAGRAM AI AUTOMATION - COMPREHENSIVE TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define test order and descriptions
    tests = [
        ("Environment Setup", "test_environment.py", "Verify all packages and modules are installed"),
        ("Ollama Embeddings", "test_ollama.py", "Test local embedding generation with nomic-embed-text"),
        ("Perplexity Research", "test_perplexity.py", "Test AI-powered research and trend analysis"),
        ("Viral Content Generator", "test_viral_content.py", "Test 5 viral content strategies"),
        ("Content Curator", "test_content_curator.py", "Test multi-source content curation"),
        ("Vector Store", "test_vector_store.py", "Test ChromaDB + Ollama deduplication"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    # Run each test
    for name, file, description in tests:
        print(f"📋 Test: {name}")
        print(f"   Description: {description}")
        print(f"   File: {file}\n")
        
        success, stdout, stderr = run_test(name, file)
        results.append((name, success, stdout, stderr))
        
        if success:
            passed += 1
            print(f"\n✅ {name} - PASSED\n")
        else:
            failed += 1
            print(f"\n❌ {name} - FAILED\n")
    
    # Print summary
    print_header("� TEST SUMMARY")
    
    total = len(tests)
    print(f"Total Tests:  {total}")
    print(f"✅ Passed:    {passed}")
    print(f"❌ Failed:    {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")
    
    # Detailed results
    print_section("Detailed Results")
    for name, success, stdout, stderr in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
    
    print(f"\n\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    if failed > 0:
        print("\n⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Your system is ready for production!")
        sys.exit(0)

if __name__ == "__main__":
    main()
    """Print test summary"""
    print("\n" * 2)
    print("=" * 80)
    print(" " * 30 + "TEST SUMMARY")
    print("=" * 80)
    print()
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"📊 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/total*100):.1f}%")
    print()
    
    print("📋 Detailed Results:")
    print("-" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print("=" * 80)
    
    if all(results.values()):
        print("🎉 ALL TESTS PASSED! System is ready for production!")
        print()
        print("Next Steps:")
        print("1. ✅ All components are working correctly")
        print("2. 🚀 Ready to run integrated system")
        print("3. 💡 Execute: python run_ultimate_automation.py")
    else:
        print("⚠️  SOME TESTS FAILED - Please fix issues before proceeding")
        print()
        print("Failed Components:")
        for test_name, passed in results.items():
            if not passed:
                print(f"   • {test_name}")
    
    print("=" * 80)
    print()

async def main():
    """Run all component tests"""
    
    print_header()
    
    # Define test sequence
    tests = [
        ("test_environment.py", "Environment Setup"),
        ("test_ollama.py", "Ollama Embeddings Service"),
        ("test_perplexity.py", "Perplexity Research Service"),
        ("test_viral_content.py", "Viral Content Generator"),
        ("test_content_curator.py", "Content Curator"),
        ("test_vector_store.py", "Vector Store & Deduplication"),
    ]
    
    results = {}
    
    print("🔄 Running Component Tests...")
    print("=" * 80)
    print()
    
    for test_file, test_name in tests:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            results[test_name] = False
            continue
        
        print(f"▶️  Starting: {test_name}")
        success = run_test(test_file, test_name)
        results[test_name] = success
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    print("\n")
    print("🚀 Starting Comprehensive Component Testing...")
    print()
    print("💡 This will test each component individually:")
    print("   1. Environment configuration")
    print("   2. Ollama local embeddings")
    print("   3. Perplexity research API")
    print("   4. Viral content generation")
    print("   5. Content curation pipeline")
    print("   6. Vector store & deduplication")
    print()
    input("Press Enter to begin testing... ")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
