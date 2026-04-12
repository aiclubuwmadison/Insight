import * as vscode from "vscode";

type AnalyzeSuccessResponse = {
  explanation: string;
  time_complexity?: string;
  space_complexity?: string;
  model?: string;
  status: string;
};

type AnalyzeErrorResponse = {
  error: string;
  status: string;
};

const AUTO_ANALYZE_MIN_CHARS = 60;
const AUTO_ANALYZE_DEBOUNCE_MS = 800;

let autoAnalyzeTimer: NodeJS.Timeout | undefined;
let activeDecorationType: vscode.TextEditorDecorationType | undefined;

export function activate(context: vscode.ExtensionContext) {
  const analyzeSelectionCommand = vscode.commands.registerCommand(
    "insight.analyzeSelection",
    async () => {
      const editor = vscode.window.activeTextEditor;

      if (!editor) {
        vscode.window.showErrorMessage("No active editor found.");
        return;
      }

      const selection = editor.selection;
      let code = editor.document.getText(selection).trim();
      let range: vscode.Range | undefined;

      if (!code) {
        code = editor.document.getText().trim();
        range = new vscode.Range(
          editor.document.positionAt(0),
          editor.document.positionAt(editor.document.getText().length)
        );
      } else {
        range = new vscode.Range(selection.start, selection.end);
      }

      if (!code) {
        vscode.window.showErrorMessage("No code selected or found in the current file.");
        return;
      }

      const language = editor.document.languageId || "unknown";
      await analyzeAndShow(editor, code, language, "manual", range);
    }
  );

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

    const looksLikePaste =
      insertedText.length >= AUTO_ANALYZE_MIN_CHARS &&
      (insertedText.includes("\n") || insertedText.includes("    ") || insertedText.includes("\t"));

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
      const end = editor.document.positionAt(
        editor.document.offsetAt(start) + insertedText.length
      );
      const pastedRange = new vscode.Range(start, end);

      await analyzeAndShow(editor, code, language, "auto", pastedRange);
    }, AUTO_ANALYZE_DEBOUNCE_MS);
  });

  context.subscriptions.push(analyzeSelectionCommand, pasteListener);
}

async function analyzeAndShow(
  editor: vscode.TextEditor,
  code: string,
  language: string,
  source: string,
  range?: vscode.Range
) {
  const panel = vscode.window.createWebviewPanel(
    "insightAnalysis",
    "Insight Analysis",
    vscode.ViewColumn.Beside,
    {
      enableScripts: false,
      retainContextWhenHidden: true,
    }
  );

  panel.webview.html = getLoadingHtml(language, source);

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title:
        source === "auto"
          ? "Insight auto-analyzing pasted code..."
          : "Insight is analyzing code...",
      cancellable: false,
    },
    async () => {
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

        const data = (await response.json()) as AnalyzeSuccessResponse | AnalyzeErrorResponse;

        if (!response.ok) {
          const message =
            "error" in data ? data.error : `Request failed with status ${response.status}`;

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

        panel.webview.html = getWebviewHtml(
          code,
          language,
          data.explanation,
          data.time_complexity ?? "Unknown",
          data.space_complexity ?? "Unknown",
          source
        );

        if (range) {
          applyInlineAnnotations(
            editor,
            range,
            data.explanation,
            data.time_complexity ?? "Unknown",
            data.space_complexity ?? "Unknown"
          );
        }

        if (source === "manual") {
          vscode.window.showInformationMessage("Insight analysis complete.");
        }
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Unknown error contacting backend.";

        panel.webview.html = getErrorHtml(`Insight request failed: ${message}`);
        vscode.window.showErrorMessage(`Insight request failed: ${message}`);
      }
    }
  );
}

function applyInlineAnnotations(
  editor: vscode.TextEditor,
  range: vscode.Range,
  explanation: string,
  timeComplexity: string,
  spaceComplexity: string
) {
  if (activeDecorationType) {
    activeDecorationType.dispose();
  }

  activeDecorationType = vscode.window.createTextEditorDecorationType({
    backgroundColor: "rgba(123, 97, 255, 0.10)",
    borderRadius: "4px",
    isWholeLine: false,
    overviewRulerColor: "rgba(123, 97, 255, 0.8)",
    overviewRulerLane: vscode.OverviewRulerLane.Right,
  });

  const shortExplanation = getShortExplanation(explanation);

  const decoration: vscode.DecorationOptions = {
    range,
    hoverMessage: new vscode.MarkdownString(
      [
        `**Insight Summary**`,
        ``,
        shortExplanation,
        ``,
        `**Time Complexity:** ${escapeMarkdown(timeComplexity)}`,
        `**Space Complexity:** ${escapeMarkdown(spaceComplexity)}`,
      ].join("\n")
    ),
  };

  editor.setDecorations(activeDecorationType, [decoration]);
}

function getShortExplanation(explanation: string): string {
  const cleaned = explanation.replace(/\n/g, " ").trim();
  if (cleaned.length <= 220) {
    return cleaned;
  }
  return `${cleaned.slice(0, 217)}...`;
}

function escapeMarkdown(text: string): string {
  return text.replace(/([\\`*_{}[\]()#+\-.!|>])/g, "\\$1");
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatExplanation(text: string): string {
  const lines = text.split("\n");

  const paragraphs: string[] = [];
  const bullets: string[] = [];

  for (const line of lines) {
    const trimmed = line.trim();

    if (!trimmed) {
      continue;
    }

    if (trimmed.startsWith("-")) {
      bullets.push(trimmed.replace(/^-+\s*/, ""));
    } else {
      paragraphs.push(trimmed);
    }
  }

  const paragraphHtml =
    paragraphs.length > 0
      ? `<p>${paragraphs.map((p) => escapeHtml(p)).join(" ")}</p>`
      : "";

  const bulletHtml =
    bullets.length > 0
      ? `<div class="bullet-spacer"></div><ul>${bullets
          .map((b) => `<li>${escapeHtml(b)}</li>`)
          .join("")}</ul>`
      : "";

  return `${paragraphHtml}${bulletHtml}`;
}

function getLanguageColor(language: string): string {
  const map: Record<string, string> = {
    python: "linear-gradient(135deg, #3572A5, #4B8BBE)",
    javascript: "linear-gradient(135deg, #f7df1e, #e6c200)",
    typescript: "linear-gradient(135deg, #3178c6, #255a96)",
    java: "linear-gradient(135deg, #b07219, #8a5a12)",
    cpp: "linear-gradient(135deg, #00599c, #007acc)",
    c: "linear-gradient(135deg, #555555, #777777)",
    go: "linear-gradient(135deg, #00ADD8, #007d9c)",
    rust: "linear-gradient(135deg, #b7410e, #8b2f08)",
  };

  return map[language.toLowerCase()] || "linear-gradient(135deg, #0e639c, #1177bb)";
}

function getSourceBadgeHtml(source: string): string {
  if (source !== "auto") {
    return "";
  }

  return `
    <div class="source-badge-row">
      <span class="source-badge">Auto-analyzed paste</span>
    </div>
  `;
}

function getBaseStyles(): string {
  return `
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      padding: 20px;
      line-height: 1.6;
      background: #1e1e1e;
      color: #d4d4d4;
    }

    .card {
      border: 1px solid #333;
      border-top: 1px solid #2f2f2f;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
      background: #252526;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .card + .card {
      margin-top: 20px;
    }

    .label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #888;
      margin-bottom: 8px;
    }

    h1 {
      font-size: 22px;
      margin-bottom: 12px;
      color: #ffffff;
      letter-spacing: -0.5px;
    }

    p {
      margin-top: 0;
      margin-bottom: 16px;
      line-height: 1.7;
    }

    ul {
      margin: 0;
      padding-left: 20px;
    }

    li {
      margin-bottom: 10px;
      line-height: 1.5;
    }

    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
      background: #111111;
      color: #e6e6e6;
      padding: 14px;
      border-radius: 8px;
      overflow-x: auto;
      border: 1px solid #2d2d2d;
      font-family: "SFMono-Regular", Consolas, monospace;
      font-size: 13px;
    }

    .language-pill,
    .complexity-pill {
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      color: white;
      font-size: 12px;
      font-weight: 600;
    }

    .complexity-pill {
      background: linear-gradient(135deg, #5a3fc0, #7b61ff);
      margin-right: 8px;
      margin-bottom: 8px;
    }

    details {
      margin-top: 8px;
    }

    summary {
      cursor: pointer;
      color: #4fc1ff;
      font-weight: 600;
      margin-bottom: 12px;
      outline: none;
      transition: opacity 0.2s ease;
    }

    summary:hover {
      opacity: 0.8;
    }

    .status {
      font-size: 14px;
      color: #bbbbbb;
    }

    .error-text {
      color: #ff7b72;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .footer-note {
      margin-top: 14px;
      font-size: 12px;
      color: #888;
    }

    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .bullet-spacer {
      height: 8px;
    }

    .source-badge-row {
      margin-bottom: 14px;
    }

    .source-badge {
      display: inline-block;
      font-size: 12px;
      padding: 4px 8px;
      border-radius: 6px;
      background: #2d2d2d;
      color: #aaa;
      border: 1px solid #3a3a3a;
    }
  `;
}

function getLoadingHtml(language: string, source: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Insight Analysis</title>
  <style>${getBaseStyles()}</style>
</head>
<body>
  <h1>Insight Analysis</h1>
  ${getSourceBadgeHtml(source)}

  <div class="card">
    <div class="label">Language</div>
    <span class="language-pill" style="background: ${getLanguageColor(language)};">
      ${escapeHtml(language)}
    </span>
  </div>

  <div class="card">
    <div class="label">Status</div>
    <p class="status">Analyzing your code...</p>
  </div>
</body>
</html>`;
}

function getErrorHtml(message: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Insight Analysis Error</title>
  <style>${getBaseStyles()}</style>
</head>
<body>
  <h1>Insight Analysis</h1>

  <div class="card">
    <div class="label">Status</div>
    <p class="error-text">${escapeHtml(message)}</p>
  </div>
</body>
</html>`;
}

function getWebviewHtml(
  code: string,
  language: string,
  explanation: string,
  timeComplexity: string,
  spaceComplexity: string,
  source: string
): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Insight Analysis</title>
  <style>${getBaseStyles()}</style>
</head>
<body>
  <h1>Insight Analysis</h1>
  ${getSourceBadgeHtml(source)}

  <div class="card">
    <div class="label">Language</div>
    <span class="language-pill" style="background: ${getLanguageColor(language)};">
      ${escapeHtml(language)}
    </span>
  </div>

  <div class="card">
    <div class="label">Estimated Complexity</div>
    <div class="pill-row">
      <span class="complexity-pill">Time: ${escapeHtml(timeComplexity)}</span>
      <span class="complexity-pill">Space: ${escapeHtml(spaceComplexity)}</span>
    </div>
  </div>

  <div class="card">
    <div class="label">AI Explanation</div>
    ${formatExplanation(explanation)}
    <p class="footer-note">Generated by AI • Results may vary</p>
  </div>

  <div class="card">
    <div class="label">Submitted Code</div>
    <details>
      <summary>Show code</summary>
      <pre>${escapeHtml(code)}</pre>
    </details>
  </div>
</body>
</html>`;
}

export function deactivate() {
  if (activeDecorationType) {
    activeDecorationType.dispose();
  }
}