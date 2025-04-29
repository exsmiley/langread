#!/usr/bin/env python3
"""
This script updates all Python scripts in the scripts directory to use the path_helper.
Run this once to ensure all scripts can be run from any directory and still find their modules.
"""

import os
import re
import sys

def update_script(script_path):
    """Update a script to use the path_helper."""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated or doesn't need update (no sys.path modifications or src imports)
    if 'from path_helper import setup_path' in content:
        print(f"Script already updated: {script_path}")
        return False
    
    if 'sys.path.append' not in content and 'from src.' not in content and 'import src.' not in content:
        print(f"Script doesn't need update: {script_path}")
        return False
    
    # Find where imports begin
    import_pattern = re.compile(r'^(?:import|from)\s+', re.MULTILINE)
    first_import_match = import_pattern.search(content)
    
    if not first_import_match:
        print(f"Could not find imports in {script_path}, skipping")
        return False
    
    first_import_pos = first_import_match.start()
    
    # Find any sys.path modifications and remove them
    sys_path_pattern = re.compile(r'# Add .*?\n?^.*?sys\.path\.append.*?\n', re.MULTILINE | re.DOTALL)
    content = re.sub(sys_path_pattern, '', content)
    
    # Insert our path helper import
    helper_import = 'from path_helper import setup_path\n# Add project root to Python path\nsetup_path()\n\n'
    content = content[:first_import_pos] + helper_import + content[first_import_pos:]
    
    # Write the updated content back to the file
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated script: {script_path}")
    return True

def main():
    """Update all Python scripts in the scripts directory."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    updated_count = 0
    skipped_count = 0
    
    # Skip this script itself
    this_script = os.path.basename(__file__)
    path_helper = 'path_helper.py'
    
    # Update all Python scripts in the directory
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != this_script and filename != path_helper:
            script_path = os.path.join(script_dir, filename)
            if update_script(script_path):
                updated_count += 1
            else:
                skipped_count += 1
    
    print(f"\nScript update complete: {updated_count} updated, {skipped_count} skipped")

if __name__ == "__main__":
    main()
