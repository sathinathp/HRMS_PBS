import os
import re
from pathlib import Path

def fix_template_spacing(file_path):
    """Fix Django template tag spacing issues in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match {% if variable==value %} and replace with {% if variable == value %}
        # This pattern looks for template tags with == but no spaces around it
        patterns = [
            # Match {% if var==value %}
            (r'{%\s+if\s+(\w+)==(\w+)\s+%}', r'{% if \1 == \2 %}'),
            (r'{%\s+if\s+(\w+)==(\d+)\s+%}', r'{% if \1 == \2 %}'),
            (r'{%\s+if\s+(\w+\.\w+)==(\w+\.\w+)\s+%}', r'{% if \1 == \2 %}'),
            (r'{%\s+if\s+(\w+\.\w+)==(\w+)\s+%}', r'{% if \1 == \2 %}'),
            (r'{%\s+if\s+(\w+)==(\w+\.\w+)\s+%}', r'{% if \1 == \2 %}'),
            # Match {% elif var==value %}
            (r'{%\s+elif\s+(\w+)==(\w+)\s+%}', r'{% elif \1 == \2 %}'),
            (r'{%\s+elif\s+(\w+)==(\d+)\s+%}', r'{% elif \1 == \2 %}'),
            (r'{%\s+elif\s+(\w+\.\w+)==(\w+\.\w+)\s+%}', r'{% elif \1 == \2 %}'),
            (r'{%\s+elif\s+(\w+\.\w+)==(\w+)\s+%}', r'{% elif \1 == \2 %}'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, file_path
        return False, None
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, None

def main():
    """Find and fix all Django template files with spacing issues."""
    base_dir = Path(r"c:\Users\sathi\Downloads\hrms-pbs-main")
    
    fixed_files = []
    
    # Find all HTML files
    for html_file in base_dir.rglob("*.html"):
        was_fixed, file_path = fix_template_spacing(html_file)
        if was_fixed:
            fixed_files.append(file_path)
            print(f"Fixed: {file_path}")
    
    print(f"\n{'='*60}")
    print(f"Total files fixed: {len(fixed_files)}")
    print(f"{'='*60}")
    
    if fixed_files:
        print("\nFixed files:")
        for f in fixed_files:
            print(f"  - {f}")
    else:
        print("\nNo files needed fixing!")

if __name__ == "__main__":
    main()
