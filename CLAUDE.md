# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static HTML/CSS/JS demo site — no build system, no package manager, no framework. Two AI-powered educational demos for Edukultur, deployed via GitHub Pages.

## Running Locally

**General (Hanzi demo, homepage):** Open `index.html` directly in browser. File-protocol works fine.

**English Spelling demo:** Requires HTTPS for microphone (Web Speech API). Use the included dev server:
```bash
cd "english alphabet spelling"
python https_server.py
# Access at https://localhost:8443
```
On first run, auto-generates `server.crt` + `server.key`. Requires `cryptography` pip package (auto-installs if missing). Accept browser security warning for self-signed cert.

## Architecture

### Entry Point
- `index.html` — landing page with cards linking to both demos

### English Spelling Demo (`english alphabet spelling/`)
- `english-spelling.html` — self-contained single-file app
- Uses **Web Speech API** (`webkitSpeechRecognition`) for voice input
- Distinguishes letter-by-letter input from full word input (rejects complete word attempts)
- No external API calls — recognition is browser-native

### Hanzi Handwriting Demo (`hanzi/`)
- `hanzi-handwriting.html` — self-contained single-file app
- `hanzilookup.min.js` — offline handwriting recognition library (11 modules bundled)
- `mmah.json` — character database (~827KB, base64-encoded substroke data, ~3000 chars)

**HanziLookup data flow:**
```
User draws on 256×256 canvas
→ Raw [x,y] strokes
→ AnalyzedCharacter (pivot detection, substroke extraction)
→ Matcher (dynamic programming vs mmah.json DB)
→ MatchCollector (top 3 results by score)
→ Display
```
`mmah.json` loads via XHR — works on GitHub Pages but **fails on `file://` protocol** (CORS). Serve with any HTTP server for local testing.

### Shared Design System
Both demos and the homepage share a CSS custom property system defined in each file's `:root`:
- Dark theme default, light theme via `[data-theme="light"]`
- Theme persisted to `localStorage`
- Fonts: `Space Grotesk` (headings), `Inter` (body) from Google Fonts
- Accent: `#6366f1` (indigo) + `#06b6d4` (cyan) gradient

## Deployment

GitHub Pages from `main` branch root. `index.html` must stay at repo root.

Files excluded from GitHub Pages (local dev only, not needed for deployed site):
- `english alphabet spelling/https_server.py`
- `english alphabet spelling/server.crt`
- `english alphabet spelling/server.key`
- `english alphabet spelling/start_https_server.bat`
- `hanzi/hanzilookup-analysis.md`
