"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
const AUTO_ANALYZE_MIN_CHARS = 100;
const AUTO_ANALYZE_DEBOUNCE_MS = 400;
let autoAnalyzeTimer;
let activeDecorationType;
let insightPanel;
function activate(context) {
    const analyzeSelectionCommand = vscode.commands.registerCommand("insight.analyzeSelection", async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("No active editor found.");
            return;
        }
        const selection = editor.selection;
        let code = editor.document.getText(selection).trim();
        let range;
        if (!code) {
            code = editor.document.getText().trim();
            range = new vscode.Range(editor.document.positionAt(0), editor.document.positionAt(editor.document.getText().length));
        }
        else {
            range = new vscode.Range(selection.start, selection.end);
        }
        if (!code) {
            vscode.window.showErrorMessage("No code selected or found in the current file.");
            return;
        }
        const language = editor.document.languageId || "unknown";
        await analyzeAndShow(editor, code, language, "manual", range);
    });
    const pasteListener = vscode.workspace.onDidChangeTextDocument(async (event) => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || event.document !== editor.document) {
            return;
        }
        if (!event.contentChanges.length) {
            return;
        }
        const change = event.contentChanges[0];
        const insertedText = change.text;
        const looksLikePaste = insertedText.length >= AUTO_ANALYZE_MIN_CHARS &&
            insertedText.includes("\n");
        if (!looksLikePaste) {
            return;
        }
        if (autoAnalyzeTimer) {
            clearTimeout(autoAnalyzeTimer);
        }
        autoAnalyzeTimer = setTimeout(async () => {
            const code = insertedText.trim();
            if (!code) {
                return;
            }
            const language = editor.document.languageId || "unknown";
            const start = change.range.start;
            const end = editor.document.positionAt(editor.document.offsetAt(start) + insertedText.length);
            const pastedRange = new vscode.Range(start, end);
            await analyzeAndShow(editor, code, language, "auto", pastedRange);
        }, AUTO_ANALYZE_DEBOUNCE_MS);
    });
    context.subscriptions.push(analyzeSelectionCommand, pasteListener);
}
async function analyzeAndShow(editor, code, language, source, range) {
    const panel = getOrCreatePanel();
    panel.webview.html = getLoadingHtml(language, source);
    panel.reveal(vscode.ViewColumn.Beside, true);
    const showProgressNotification = source === "manual";
    const runRequest = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    code,
                    language,
                    source,
                }),
            });
            const data = (await response.json());
            if (!response.ok) {
                const message = "error" in data ? data.error : `Request failed with status ${response.status}`;
                panel.webview.html = getErrorHtml(message);
                vscode.window.showErrorMessage(message);
                return;
            }
            if (!("explanation" in data)) {
                const message = "Backend returned an invalid response.";
                panel.webview.html = getErrorHtml(message);
                vscode.window.showErrorMessage(message);
                return;
            }
            panel.webview.html = getWebviewHtml(code, language, data.explanation, data.time_complexity ?? "Unknown", data.space_complexity ?? "Unknown", source);
            if (range) {
                applyInlineAnnotations(editor, range, data.explanation, data.time_complexity ?? "Unknown", data.space_complexity ?? "Unknown");
            }
            if (source === "manual") {
                vscode.window.showInformationMessage("Insight analysis complete.");
            }
        }
        catch (error) {
            const message = error instanceof Error ? error.message : "Unknown error contacting backend.";
            panel.webview.html = getErrorHtml(`Insight request failed: ${message}`);
            vscode.window.showErrorMessage(`Insight request failed: ${message}`);
        }
    };
    if (showProgressNotification) {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Insight is analyzing code...",
            cancellable: false,
        }, async () => {
            await runRequest();
        });
    }
    else {
        await runRequest();
    }
}
function getOrCreatePanel() {
    if (insightPanel) {
        return insightPanel;
    }
    insightPanel = vscode.window.createWebviewPanel("insightAnalysis", "Insight Analysis", vscode.ViewColumn.Beside, {
        enableScripts: false,
        retainContextWhenHidden: true,
    });
    insightPanel.onDidDispose(() => {
        insightPanel = undefined;
    });
    return insightPanel;
}
function applyInlineAnnotations(editor, range, explanation, timeComplexity, spaceComplexity) {
    if (activeDecorationType) {
        activeDecorationType.dispose();
    }
    activeDecorationType = vscode.window.createTextEditorDecorationType({
        backgroundColor: "rgba(227, 170, 107, 0.10)",
        borderRadius: "4px",
        isWholeLine: false,
        overviewRulerColor: "rgba(227, 170, 107, 0.85)",
        overviewRulerLane: vscode.OverviewRulerLane.Right,
    });
    const shortExplanation = getShortExplanation(explanation);
    const decoration = {
        range,
        hoverMessage: new vscode.MarkdownString([
            `**Insight Summary**`,
            ``,
            shortExplanation,
            ``,
            `**Time Complexity:** ${escapeMarkdown(timeComplexity)}`,
            `**Space Complexity:** ${escapeMarkdown(spaceComplexity)}`,
        ].join("\n")),
    };
    editor.setDecorations(activeDecorationType, [decoration]);
}
function getShortExplanation(explanation) {
    const cleaned = explanation.replace(/\n/g, " ").trim();
    if (cleaned.length <= 220) {
        return cleaned;
    }
    return `${cleaned.slice(0, 217)}...`;
}
function escapeMarkdown(text) {
    return text.replace(/([\\`*_{}[\]()#+\-.!|>])/g, "\\$1");
}
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}
function formatExplanation(text) {
    const lines = text.split("\n");
    const paragraphs = [];
    const bullets = [];
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) {
            continue;
        }
        if (trimmed.startsWith("-")) {
            bullets.push(trimmed.replace(/^-+\s*/, ""));
        }
        else {
            paragraphs.push(trimmed);
        }
    }
    const paragraphHtml = paragraphs.length > 0
        ? `<p>${paragraphs.map((p) => escapeHtml(p)).join(" ")}</p>`
        : "";
    const bulletHtml = bullets.length > 0
        ? `<div class="bullet-spacer"></div><ul>${bullets
            .map((b) => `<li>${escapeHtml(b)}</li>`)
            .join("")}</ul>`
        : "";
    return `${paragraphHtml}${bulletHtml}`;
}
function getLanguageColor(language) {
    const map = {
        python: "#5a9fd4",
        javascript: "#e6c54e",
        typescript: "#4f9cf0",
        java: "#c7782f",
        cpp: "#5fa8d3",
        c: "#9aa0a8",
        go: "#4dd0c4",
        rust: "#d97742",
    };
    return map[language.toLowerCase()] || "#e3aa6b";
}
function getSourceBadgeHtml(source) {
    if (source !== "auto") {
        return "";
    }
    return `
    <div class="source-badge-row">
      <span class="source-badge">Auto-analyzed paste</span>
    </div>
  `;
}
function getBaseStyles() {
    return `
    :root {
      --bg: #131418;
      --bg-deep: #0e0f12;
      --surface: #191b20;
      --surface-2: #1f2127;
      --border: rgba(255, 255, 255, 0.07);
      --border-bright: rgba(255, 255, 255, 0.13);
      --text: #e7e4dc;
      --text-dim: #9c9ca6;
      --text-faint: #696a73;
      --accent: #e3aa6b;
      --accent-dim: #b9854f;
      --accent-soft: rgba(227, 170, 107, 0.12);
      --danger: #e8806e;
      --mono: "JetBrains Mono", "SF Mono", SFMono-Regular, "Cascadia Code",
        "Fira Code", ui-monospace, Menlo, Consolas, monospace;
      --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua",
        Georgia, "Times New Roman", serif;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 32px 26px 44px;
      font-family: var(--serif);
      font-size: 15px;
      line-height: 1.65;
      color: var(--text);
      background:
        radial-gradient(120% 80% at 50% -8%, #1c1e24 0%, rgba(28, 30, 36, 0) 62%),
        var(--bg);
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
    }

    .wrap {
      max-width: 660px;
      margin: 0 auto;
    }

    ::selection {
      background: var(--accent-soft);
      color: var(--text);
    }

    ::-webkit-scrollbar {
      width: 10px;
      height: 10px;
    }

    ::-webkit-scrollbar-thumb {
      background: #2a2c33;
      border-radius: 6px;
      border: 2px solid var(--bg);
    }

    ::-webkit-scrollbar-thumb:hover {
      background: #34363e;
    }

    .masthead {
      margin-bottom: 24px;
      animation: rise 0.5s cubic-bezier(0.2, 0.7, 0.2, 1) both;
    }

    .eyebrow {
      font-family: var(--mono);
      font-size: 10.5px;
      letter-spacing: 0.34em;
      text-transform: uppercase;
      color: var(--accent);
      margin: 0 0 11px;
    }

    h1 {
      font-family: var(--mono);
      font-size: 25px;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: #f4f1ea;
      margin: 0 0 16px;
    }

    .rule {
      height: 1px;
      background: linear-gradient(
        90deg,
        var(--accent-dim),
        rgba(185, 133, 79, 0) 72%
      );
    }

    .card {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px 20px;
      margin-top: 16px;
      background: var(--surface);
      animation: rise 0.5s cubic-bezier(0.2, 0.7, 0.2, 1) both;
    }

    .card:nth-of-type(1) { animation-delay: 0.04s; }
    .card:nth-of-type(2) { animation-delay: 0.1s; }
    .card:nth-of-type(3) { animation-delay: 0.16s; }
    .card:nth-of-type(4) { animation-delay: 0.22s; }

    .label {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      color: var(--text-faint);
      margin-bottom: 14px;
    }

    .lang {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      font-family: var(--mono);
      font-size: 13px;
      color: var(--text);
      padding: 7px 13px 7px 11px;
      border: 1px solid var(--border-bright);
      border-radius: 8px;
      background: var(--surface-2);
    }

    .lang-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.04);
    }

    .readout {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      column-gap: 22px;
    }

    .metric {
      min-width: 0;
    }

    .metric-label {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--text-faint);
      margin-bottom: 9px;
    }

    .metric-value {
      font-family: var(--mono);
      font-size: 26px;
      font-weight: 600;
      color: var(--accent);
      letter-spacing: -0.01em;
      line-height: 1.1;
      word-break: break-word;
    }

    .readout-divider {
      width: 1px;
      height: 44px;
      background: var(--border-bright);
    }

    .prose p {
      margin: 0 0 14px;
      color: var(--text);
    }

    .prose p:last-child {
      margin-bottom: 0;
    }

    .prose ul {
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .prose li {
      position: relative;
      padding-left: 20px;
      margin-bottom: 11px;
      line-height: 1.6;
      color: var(--text);
    }

    .prose li:last-child {
      margin-bottom: 0;
    }

    .prose li::before {
      content: "";
      position: absolute;
      left: 2px;
      top: 0.6em;
      width: 6px;
      height: 6px;
      background: var(--accent);
      border-radius: 1px;
      transform: rotate(45deg);
    }

    .bullet-spacer {
      height: 10px;
    }

    .footer-note {
      font-family: var(--mono);
      font-size: 10.5px;
      letter-spacing: 0.04em;
      color: var(--text-faint);
      margin: 18px 0 0;
    }

    pre {
      margin: 4px 0 0;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: var(--mono);
      font-size: 12.5px;
      line-height: 1.6;
      color: #d7d4cc;
      background: var(--bg-deep);
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow-x: auto;
    }

    details {
      margin-top: 2px;
    }

    summary {
      list-style: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      font-family: var(--mono);
      font-size: 11px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--accent);
      user-select: none;
      transition: color 0.15s ease;
      margin-bottom: 12px;
    }

    summary::-webkit-details-marker {
      display: none;
    }

    summary::before {
      content: "+";
      font-size: 14px;
      line-height: 1;
      color: var(--accent-dim);
    }

    details[open] > summary::before {
      content: "\u2212";
    }

    summary:hover {
      color: #f0c88e;
    }

    summary:focus-visible {
      outline: 1px solid var(--accent-dim);
      outline-offset: 3px;
      border-radius: 3px;
    }

    .status {
      font-family: var(--serif);
      font-size: 14.5px;
      color: var(--text-dim);
      margin: 0;
    }

    .scan {
      position: relative;
      height: 2px;
      margin-top: 18px;
      background: var(--border);
      border-radius: 2px;
      overflow: hidden;
    }

    .scan::after {
      content: "";
      position: absolute;
      inset: 0;
      width: 36%;
      border-radius: 2px;
      background: linear-gradient(
        90deg,
        transparent,
        var(--accent),
        transparent
      );
      animation: sweep 1.25s ease-in-out infinite;
    }

    .error {
      display: flex;
      gap: 14px;
    }

    .error-bar {
      flex: 0 0 3px;
      background: var(--danger);
      border-radius: 2px;
    }

    .error-text {
      margin: 0;
      color: #f0b6ab;
      font-family: var(--mono);
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .source-badge-row {
      margin: 16px 0 0;
    }

    .source-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--text-dim);
      padding: 5px 12px;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: var(--surface-2);
    }

    .source-badge::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--accent);
    }

    @keyframes rise {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes sweep {
      0% {
        transform: translateX(-120%);
      }
      100% {
        transform: translateX(360%);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .masthead,
      .card {
        animation: none;
      }
      .scan::after {
        animation: none;
        width: 100%;
        opacity: 0.5;
      }
    }
  `;
}
function getLoadingHtml(language, source) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Insight Analysis</title>
  <style>${getBaseStyles()}</style>
</head>
<body>
  <div class="wrap">
    <header class="masthead">
      <p class="eyebrow">Code Analysis</p>
      <h1>Insight Analysis</h1>
      <div class="rule"></div>
    </header>

    ${getSourceBadgeHtml(source)}

    <section class="card">
      <div class="label">Language</div>
      <span class="lang">
        <span class="lang-dot" style="background: ${getLanguageColor(language)};"></span>
        ${escapeHtml(language)}
      </span>
    </section>

    <section class="card">
      <div class="label">Status</div>
      <p class="status">Reading your code and estimating complexity</p>
      <div class="scan"></div>
    </section>
  </div>
</body>
</html>`;
}
function getErrorHtml(message) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Insight Analysis Error</title>
  <style>${getBaseStyles()}</style>
</head>
<body>
  <div class="wrap">
    <header class="masthead">
      <p class="eyebrow">Code Analysis</p>
      <h1>Insight Analysis</h1>
      <div class="rule"></div>
    </header>

    <section class="card">
      <div class="label">Status</div>
      <div class="error">
        <div class="error-bar"></div>
        <p class="error-text">${escapeHtml(message)}</p>
      </div>
    </section>
  </div>
</body>
</html>`;
}
function getWebviewHtml(code, language, explanation, timeComplexity, spaceComplexity, source) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Insight Analysis</title>
  <style>${getBaseStyles()}</style>
</head>
<body>
  <div class="wrap">
    <header class="masthead">
      <p class="eyebrow">Code Analysis</p>
      <h1>Insight Analysis</h1>
      <div class="rule"></div>
    </header>

    ${getSourceBadgeHtml(source)}

    <section class="card">
      <div class="label">Language</div>
      <span class="lang">
        <span class="lang-dot" style="background: ${getLanguageColor(language)};"></span>
        ${escapeHtml(language)}
      </span>
    </section>

    <section class="card">
      <div class="label">Estimated Complexity</div>
      <div class="readout">
        <div class="metric">
          <div class="metric-label">Time</div>
          <div class="metric-value">${escapeHtml(timeComplexity)}</div>
        </div>
        <div class="readout-divider"></div>
        <div class="metric">
          <div class="metric-label">Space</div>
          <div class="metric-value">${escapeHtml(spaceComplexity)}</div>
        </div>
      </div>
    </section>

    <section class="card">
      <div class="label">Explanation</div>
      <div class="prose">${formatExplanation(explanation)}</div>
      <p class="footer-note">Generated by AI &mdash; results may vary</p>
    </section>

    <section class="card">
      <div class="label">Submitted Code</div>
      <details>
        <summary>Show code</summary>
        <pre>${escapeHtml(code)}</pre>
      </details>
    </section>
  </div>
</body>
</html>`;
}
function deactivate() {
    if (activeDecorationType) {
        activeDecorationType.dispose();
    }
    if (insightPanel) {
        insightPanel.dispose();
        insightPanel = undefined;
    }
}
//# sourceMappingURL=extension.js.map