# tabmark

Lightweight browser bookmark exporter that syncs to a local markdown file.

---

## Installation

```bash
pip install tabmark
```

## Usage

Export your browser bookmarks to a markdown file:

```bash
tabmark export --browser chrome --output bookmarks.md
```

Watch for changes and sync automatically:

```bash
tabmark watch --output ~/notes/bookmarks.md
```

Example output in `bookmarks.md`:

```markdown
## Development
- [GitHub](https://github.com) — Code hosting platform
- [MDN Web Docs](https://developer.mozilla.org) — Web documentation

## Reading
- [Hacker News](https://news.ycombinator.com) — Tech news and discussion
```

### Supported Browsers

| Browser | Platform |
|---------|----------|
| Chrome  | macOS, Windows, Linux |
| Firefox | macOS, Windows, Linux |
| Safari  | macOS |

### Options

| Flag | Description |
|------|-------------|
| `--browser` | Target browser (default: `chrome`) |
| `--output`  | Output file path (default: `bookmarks.md`) |
| `--watch`   | Re-sync on bookmark changes |
| `--flat`    | Flatten folder structure |

## License

MIT © 2024 tabmark contributors