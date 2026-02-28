"""
Windows-Compatible Test Suite Runner
Runs all component tests without Unicode issues
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
    
    # Set UTF-8 encoding for subprocess
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters
        )
        
        print(result.stdout)
        if result.stderr and 'Traceback' in result.stderr:
            print("ERRORS:", result.stderr)
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print("[FAIL] Test TIMEOUT after 2 minutes")
        return False, "", "Timeout"
    except Exception as e:
        print(f"[FAIL] Test FAILED with exception: {str(e)}")
        return False, "", str(e)

def main():
    """Run all tests and generate summary"""
    print_header("INSTAGRAM AI AUTOMATION - COMPREHENSIVE TEST SUITE")
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
    skipped = 0
    
    # Run each test
    for name, file, description in tests:
        print(f"[TEST] {name}")
        print(f"       Description: {description}")
        print(f"       File: {file}\n")
        
        # Check if file exists
        if not os.path.exists(file):
            print(f"[SKIP] File not found: {file}\n")
            skipped += 1
            results.append((name, None, "", f"File not found: {file}"))
            continue
        
        success, stdout, stderr = run_test(name, file)
        results.append((name, success, stdout, stderr))
        
        if success:
            passed += 1
            print(f"\n[PASS] {name} - PASSED\n")
        else:
            failed += 1
            print(f"\n[FAIL] {name} - FAILED\n")
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total = len(tests)
    print(f"Total Tests:  {total}")
    print(f"[PASS] Passed:    {passed}")
    print(f"[FAIL] Failed:    {failed}")
    if skipped > 0:
        print(f"[SKIP] Skipped:   {skipped}")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")
    
    # Detailed results
    print_section("Detailed Results")
    for name, success, stdout, stderr in results:
        if success is None:
            status = "[SKIP] SKIPPED"
        elif success:
            status = "[PASS] PASSED"
        else:
            status = "[FAIL] FAILED"
        print(f"{status} - {name}")
    
    print(f"\n\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    if failed > 0:
        print("\n[WARN] Some tests failed. Please review the output above.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All tests passed! Your system is ready for production!")
        sys.exit(0)

if __name__ == "__main__":
    main()
