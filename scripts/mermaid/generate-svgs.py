#!/usr/bin/env python3
"""
Script to generate SVG files from Mermaid (.mmd) files.
Scans all directories and generates/updates SVG files as needed.
Can be run manually or via VS Code "Run on Save" extension.

Installation:
  macOS: brew install mermaid-cli
  Other: npm install -g @mermaid-js/mermaid-cli

Chrome:
  Automatically detects:
  - System Chrome (e.g., brew install --cask google-chrome)
  - Puppeteer Chrome (npx puppeteer browsers install chrome-headless-shell)
"""

import os
import subprocess
import sys


def check_mmdc():
    """Check if mermaid-cli (mmdc) is installed."""
    try:
        subprocess.run(['mmdc', '--version'], 
                      capture_output=True, 
                      check=True,
                      text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def find_mmd_files(root_dir='.'):
    """Find all .mmd files in the repository."""
    mmd_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '.venv', '__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.mmd'):
                mmd_files.append(os.path.join(root, file))
    
    return sorted(mmd_files)


def needs_generation(mmd_file):
    """Check if SVG needs to be generated or updated."""
    svg_file = mmd_file.replace('.mmd', '.svg')
    
    # If SVG doesn't exist, needs generation
    if not os.path.exists(svg_file):
        return True, 'missing'
    
    # If mmd is newer than svg, needs update
    mmd_mtime = os.path.getmtime(mmd_file)
    svg_mtime = os.path.getmtime(svg_file)
    
    if mmd_mtime > svg_mtime:
        return True, 'outdated'
    
    return False, 'up_to_date'


def find_chrome_path():
    """Find Chrome executable path - checks system Chrome first, then puppeteer Chrome."""
    import glob
    
    # First, try system Chrome locations (macOS)
    system_chrome_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium',
    ]
    
    for path in system_chrome_paths:
        if os.path.exists(path):
            return path
    
    # If system Chrome not found, try puppeteer's Chrome installation
    home_dir = os.path.expanduser('~')
    puppeteer_cache_paths = [
        os.path.join(home_dir, '.cache', 'puppeteer', 'chrome', '*', 'chrome-mac-arm64', 'Google Chrome.app', 'Contents', 'MacOS', 'Google Chrome'),
        os.path.join(home_dir, '.cache', 'puppeteer', 'chrome', '*', 'chrome-mac-x64', 'Google Chrome.app', 'Contents', 'MacOS', 'Google Chrome'),
        os.path.join(home_dir, '.cache', 'puppeteer', 'chrome', '*', 'chrome-headless-shell-mac-arm64', 'chrome-headless-shell'),
        os.path.join(home_dir, '.cache', 'puppeteer', 'chrome', '*', 'chrome-headless-shell-mac-x64', 'chrome-headless-shell'),
        os.path.join(home_dir, '.cache', 'puppeteer', 'chrome', '*', 'chrome-headless-shell', 'chrome-headless-shell'),
    ]
    
    # Try to find puppeteer Chrome using glob patterns
    for pattern in puppeteer_cache_paths:
        matches = glob.glob(pattern)
        if matches:
            # Return the first match (usually the latest version)
            return sorted(matches)[-1]
    
    # Also check common puppeteer locations without version wildcard
    puppeteer_direct_paths = [
        os.path.join(home_dir, '.cache', 'puppeteer', 'chrome'),
    ]
    
    for base_path in puppeteer_direct_paths:
        if os.path.exists(base_path):
            # Look for chrome-headless-shell first (preferred)
            for root, dirs, files in os.walk(base_path):
                if 'chrome-headless-shell' in files:
                    return os.path.join(root, 'chrome-headless-shell')
                if 'chrome' in files and 'headless' not in root:
                    return os.path.join(root, 'chrome')
    
    return None


def generate_svg(mmd_file):
    """Generate SVG file from Mermaid file."""
    svg_file = mmd_file.replace('.mmd', '.svg')
    
    # Try to use system Chrome if available
    chrome_path = find_chrome_path()
    env = os.environ.copy()
    
    if chrome_path:
        # Set puppeteer to use system Chrome
        env['PUPPETEER_EXECUTABLE_PATH'] = chrome_path
        env['CHROME_PATH'] = chrome_path
    
    try:
        result = subprocess.run(
            ['mmdc', '-i', mmd_file, '-o', svg_file],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def main():
    """Main function."""
    # Check if mmdc is available
    if not check_mmdc():
        print("Error: mermaid-cli (mmdc) not found.")
        print("Install it with:")
        print("  macOS: brew install mermaid-cli")
        print("  Other: npm install -g @mermaid-js/mermaid-cli")
        print("")
        print("Note: mermaid-cli requires Chrome/Chromium. After installation, run:")
        print("  npx puppeteer browsers install chrome-headless-shell")
        sys.exit(1)
    
    # Find all .mmd files
    mmd_files = find_mmd_files()
    
    if not mmd_files:
        print("No .mmd files found.")
        sys.exit(0)
    
    print("Scanning for Mermaid files (.mmd)...")
    print(f"Found {len(mmd_files)} file(s)\n")
    
    # Process each file
    generated = 0
    updated = 0
    skipped = 0
    errors = []
    
    for mmd_file in mmd_files:
        needs_gen, status = needs_generation(mmd_file)
        
        if not needs_gen:
            skipped += 1
            continue
        
        svg_file = mmd_file.replace('.mmd', '.svg')
        
        if status == 'missing':
            print(f"Generating: {svg_file}")
            success, error = generate_svg(mmd_file)
            if success:
                generated += 1
            else:
                errors.append((mmd_file, error))
        elif status == 'outdated':
            print(f"Updating: {svg_file} (source is newer)")
            success, error = generate_svg(mmd_file)
            if success:
                updated += 1
            else:
                errors.append((mmd_file, error))
    
    # Summary
    print(f"\nSummary: Generated: {generated}, Updated: {updated}, Skipped: {skipped}, Errors: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for mmd_file, error in errors:
            print(f"  {mmd_file}:")
            # Show first few lines of error
            error_lines = str(error).strip().split('\n')
            for line in error_lines[:3]:
                print(f"    {line}")
            if len(error_lines) > 3:
                print(f"    ... ({len(error_lines) - 3} more lines)")
        
        # Check if it's a Chrome/puppeteer error
        chrome_error = any("Chrome" in str(e) or "puppeteer" in str(e).lower() for _, e in errors)
        
        if chrome_error:
            print("\nNote: Chrome/Chromium is required for mermaid-cli.")
            print("Install it with: npx puppeteer browsers install chrome-headless-shell")
            sys.exit(1)
        
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
