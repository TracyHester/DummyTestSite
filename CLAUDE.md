# CLAUDE.md

## Project Overview

This is a **static website** for the **Environmental Appellate Advocacy Institute**, an educational site related to environmental law coursework. It is deployed via **GitHub Pages** with a custom domain (`tracyhester.stevenhester.com`).

The codebase is intentionally minimal — plain HTML and CSS with no build tools, frameworks, or dependencies.

## Repository Structure

```
/
├── CNAME              # GitHub Pages custom domain config
├── index.html         # Main institute landing page (hero layout, navbar)
├── WelcomePage.html   # Course welcome/portal page (links to roster, upload, info)
├── styles.css         # Shared stylesheet (used by WelcomePage.html)
└── CLAUDE.md          # This file
```

**Total files:** 4 source files (~130 lines of code)

## Technology Stack

- **HTML5** — semantic markup, no templating
- **CSS** — plain CSS, no preprocessors (Sass/Less)
- **No JavaScript** — `main.js` is referenced in `index.html` but does not exist
- **No build system** — no package.json, bundler, or transpiler
- **No dependencies** — no npm/yarn packages

## Deployment

- **Platform:** GitHub Pages
- **Custom domain:** `tracyhester.stevenhester.com` (configured in `CNAME`)
- **No CI/CD pipeline** — no GitHub Actions or other automation

## Development Workflow

Since this is a static site with no build tools:

1. Edit HTML/CSS files directly
2. Open files in a browser to preview (or use a local server like `python3 -m http.server`)
3. Commit and push to deploy via GitHub Pages

There are **no build commands, test suites, or linting tools** configured.

## Known Issues and Gaps

### Missing Assets
- `index.html` references `/css/style.css`, `/img/favicon.png`, `/img/th-logo.png`, and `/js/main.js` — none of these exist in the repo
- The actual stylesheet is `styles.css` in the project root (only linked from `WelcomePage.html`)

### Broken Internal Links
- `WelcomePage.html` links to `roster.html`, `upload.html`, and `info.html` — none exist yet

### Typos in index.html
- "Advoacy" should be "Advocacy" (line 41)
- "Chainging" should be "Changing" (line 42)

### Inconsistencies
- `index.html` uses `/css/style.css` while `WelcomePage.html` uses `styles.css` — different paths and filenames
- Copyright in `index.html` says "Somnolence Software"; `WelcomePage.html` says "Environmental Appellate Advocacy Course"
- Logo alt text says "Stellar Sprouts Logo" which doesn't match the institute name

## File Details

### index.html
Main landing page for the Environmental Appellate Advocacy Institute. Features a navbar with hamburger menu markup, hero section with overlay, and footer. References external assets that are not yet in the repo.

### WelcomePage.html
Course portal page with navigation to class roster, brief upload, and class info sections. Simpler structure than index.html. Uses `styles.css` from the root directory.

### styles.css
Basic stylesheet providing:
- Green header (`#4CAF50`), dark footer (`#333`)
- Arial sans-serif font stack
- Inline navigation, fixed-bottom footer
- Minimal responsive considerations

### CNAME
Single-line file: `tracyhester.stevenhester.com`

## Conventions for AI Assistants

- **No build/test/lint commands exist** — do not attempt to run them
- **Keep it simple** — this project uses no frameworks; avoid introducing unnecessary complexity
- **Preserve the static site approach** unless the user explicitly requests a framework or build system
- **Be aware of missing resources** — many referenced files (images, JS, CSS paths) do not exist yet; creating them may be part of planned work
- When adding new pages, follow the pattern in `WelcomePage.html` (links to `styles.css`, basic semantic HTML structure)
