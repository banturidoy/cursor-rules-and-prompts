# Mermaid SVG Generation

Automatically generates SVG files from Mermaid (`.mmd`) diagram files. Scans all directories and generates/updates SVG files as needed.

## Setup

### Prerequisites

1. **Install mermaid-cli:**
   ```bash
   brew install mermaid-cli
   ```
   Or via npm:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

2. **Install Chrome (one of the following):**
   
   **Option 1: System Chrome (Recommended)**
   ```bash
   brew install --cask google-chrome
   ```
   
   **Option 2: Puppeteer Chrome**
   ```bash
   npx puppeteer browsers install chrome-headless-shell
   ```

   The script automatically detects and uses either installation method.

3. **Install VS Code Extension (for auto-generation):**
   
   Install the [Run on Save extension](https://open-vsx.org/extension/nburnet1/RunOnSave) by nburnet1.
   
   In VS Code:
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
   - Search for "Run on Save"
   - Install the extension by nburnet1

### Usage

**Manual:**
```bash
python3 scripts/mermaid/generate-svgs.py
```

**Automatic (VS Code):**
Configure VS Code to run the script automatically when you save `.mmd` files (see VS Code Configuration below).

## VS Code Configuration

### 1. Extensions Configuration

Add this to your `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "emeraldwalk.RunOnSave",
    "bierner.markdown-mermaid"
  ]
}
```

### 2. Settings Configuration

Add this to your `.vscode/settings.json`:

```json
{
  "files.associations": {
    "*.mmd": "mermaid"
  },
  "emeraldwalk.runonsave": {
    "commands": [
      {
        "match": "\\.mmd$",
        "cmd": "python3 ${workspaceFolder}/scripts/mermaid/generate-svgs.py",
        "message": "Generating SVG from Mermaid...",
        "messageAfter": "SVG generated successfully!",
        "showElapsed": true,
        "isAsync": true
      }
    ]
  }
}
```

**Important:** The configuration key must be `"emeraldwalk.runonsave"` (not `"runonsave"`). This is the correct key for the Run on Save extension.

**Required Extensions:**
- [Run on Save extension](https://open-vsx.org/extension/nburnet1/RunOnSave) by nburnet1 (emeraldwalk.RunOnSave)
- Markdown Mermaid by bierner (bierner.markdown-mermaid) - for Mermaid syntax highlighting

## How It Works

- Scans all directories recursively for `.mmd` files
- Generates corresponding `.svg` files next to each `.mmd` file
- Only generates/updates SVGs when:
  - SVG file doesn't exist, or
  - `.mmd` file is newer than the `.svg` file
- Automatically detects Chrome installation (system or puppeteer)

## Context

This script is used in the project to automatically generate SVG images from Mermaid diagram source files. The SVG files are then referenced in markdown documentation for display on GitHub and other markdown viewers.

When you edit a `.mmd` file and save it, the corresponding `.svg` file is automatically regenerated, keeping your diagrams up-to-date.
