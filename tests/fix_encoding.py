"""
Fix Unicode encoding issues in test files for Windows
Replaces emojis with ASCII-compatible alternatives
"""
import os
import re

def fix_file(filepath):
    """Remove or replace emojis in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace common emojis with ASCII equivalents
    replacements = {
        '🧪': '[TEST]',
        '🚀': '[START]',
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '📊': '[STATS]',
        '⚠️': '[WARN]',
        '🎉': '[SUCCESS]',
        '📋': '[INFO]',
        '🔍': '[CHECK]',
        '💾': '[SAVE]',
        '🌐': '[WEB]',
        '📈': '[GROWTH]',
        '🔥': '[HOT]',
        '💡': '[IDEA]',
        '⚡': '[FAST]',
        '🎯': '[TARGET]',
        '🐍': '[PYTHON]',
        '📁': '[FOLDER]',
        '📅': '[DATE]',
        '\U0001f680': '[START]',
        '\U0001f9ea': '[TEST]',
    }
    
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    # Remove any remaining Unicode emojis
    content = re.sub(r'[^\x00-\x7F]+', '', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed: {filepath}")

def main():
    """Fix all test files"""
    test_files = [
        'test_environment.py',
        'test_ollama.py',
        'test_perplexity.py',
        'test_viral_content.py',
        'test_content_curator.py',
        'test_vector_store.py',
        'run_all_tests.py'
    ]
    
    for filename in test_files:
        if os.path.exists(filename):
            fix_file(filename)
    
    print("\n[SUCCESS] All files fixed!")

if __name__ == "__main__":
    main()
