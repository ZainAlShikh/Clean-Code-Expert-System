const vscode = require('vscode');
const https = require('https');
const http = require('http');
const path = require('path');

const API_HOSTNAME = '127.0.0.1';
const API_PORT = 5000;
const API_USE_HTTPS = false;

let diagnosticCollection;

function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('cleanCode');
    context.subscriptions.push(diagnosticCollection);

    let disposable = vscode.commands.registerCommand('cleanCode.analyzeFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active file to analyze.');
            return;
        }

        const document = editor.document;
        if (document.languageId !== 'javascript' && document.languageId !== 'javascriptreact') {
            vscode.window.showWarningMessage('Clean Code Expert System currently supports JavaScript only.');
            return;
        }

        const filePath = document.fileName;
        vscode.window.showInformationMessage(`Analyzing: ${path.basename(filePath)} via API...`);

        try {
            const data = await analyzeFile(filePath, document.getText());
            if (data.recommendations) {
                updateDiagnostics(document, data.recommendations);
                vscode.window.showInformationMessage(`Analysis complete! Score: ${data.clean_code_score}/100. Found ${data.recommendations.length} issues.`);
                showDashboardWebview(context, data, editor);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Analysis failed: ${error.message || 'Server not reachable'}`);
        }
    });

    context.subscriptions.push(disposable);
}

function analyzeFile(filePath, sourceCode) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({ path: filePath, code: sourceCode });

        const options = {
            hostname: API_HOSTNAME,
            port: API_PORT,
            path: '/api/analyze',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const transport = API_USE_HTTPS ? https : http;
        const req = transport.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    const parsedData = JSON.parse(data);
                    resolve(parsedData);
                } catch (e) {
                    reject(new Error('Invalid JSON response from server'));
                }
            });
        });

        req.on('error', (e) => {
            reject(e);
        });

        req.write(postData);
        req.end();
    });
}


function updateDiagnostics(document, recommendations) {
    diagnosticCollection.clear();
    const diagnostics = [];

    recommendations.forEach(rec => {
        let line = 0;
        const range = new vscode.Range(line, 0, line, 100);
        const diagnostic = new vscode.Diagnostic(
            range,
            `[${rec.severity}] ${rec.rule_name}: ${rec.description}\nStrategy: ${rec.strategy}`,
            rec.severity === 'HIGH' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning
        );
        diagnostic.code = "clean-code";
        diagnostics.push(diagnostic);
    });

    diagnosticCollection.set(document.uri, diagnostics);
}

function showDashboardWebview(context, data, editor) {
    const panel = vscode.window.createWebviewPanel(
        'cleanCodeDashboard',
        'Clean Code Dashboard',
        vscode.ViewColumn.Two,
        { enableScripts: true }
    );

    panel.webview.html = getWebviewContent(data);

    panel.webview.onDidReceiveMessage(
        async message => {
            switch (message.command) {
                case 'applyCode':
                    if (data.refactored_preview && data.refactored_preview.refactored_code) {
                        const document = editor.document;
                        const fullRange = new vscode.Range(
                            document.positionAt(0),
                            document.positionAt(document.getText().length)
                        );
                        editor.edit(editBuilder => {
                            editBuilder.replace(fullRange, data.refactored_preview.refactored_code);
                        });
                        vscode.window.showInformationMessage('Clean Code Applied Successfully!');
                    }
                    return;

            }
        },
        undefined,
        context.subscriptions
    );
}

function getWebviewContent(data) {
    const radarDataJSON = data.radar_data ? JSON.stringify(data.radar_data) : 'null';

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clean Code Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-editor-foreground); background-color: var(--vscode-editor-background); }
        h1, h2, h3 { color: var(--vscode-editor-foreground); }
        .score { font-size: 48px; font-weight: bold; color: #4CAF50; text-align: center; }
        .card { border: 1px solid var(--vscode-widget-border); padding: 20px; border-radius: 8px; margin-bottom: 20px; background: var(--vscode-editorWidget-background); }
        .issue { margin-bottom: 10px; padding: 10px; border-left: 4px solid #f44336; background: var(--vscode-textBlockQuote-background); }
        .issue.MEDIUM { border-left-color: #ff9800; }
        .issue.LOW { border-left-color: #2196f3; }
        .btn { background: #007acc; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; font-size: 14px; margin-top: 10px; }
        .btn:hover { background: #005f9e; }
        .btn-success { background: #4CAF50; }
        .btn-success:hover { background: #45a049; }
        pre { background: var(--vscode-textCodeBlock-background); padding: 15px; border-radius: 5px; overflow-x: auto; }
        .chart-container { position: relative; height: 300px; width: 100%; display: flex; justify-content: center; }
    </style>
</head>
<body>
    <h1>Clean Code Expert System</h1>

    <div class="card" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2>Overall Score</h2>
            <div class="score">${data.clean_code_score} / 100</div>
        </div>
    </div>

    ${data.radar_data ? `
    <div class="card">
        <h2>Code Quality Analysis</h2>
        <div class="chart-container">
            <canvas id="radarChart"></canvas>
        </div>
    </div>
    ` : ''}

    <div class="card">
        <h2>AI Refactored Preview</h2>
        <p>This is the suggested clean code generated by Gemini AI.</p>
        <button class="btn btn-success" onclick="applyCode()">Apply Clean Code to File</button>
        <pre><code>${data.refactored_preview && data.refactored_preview.refactored_code ? data.refactored_preview.refactored_code.replace(/</g, '&lt;').replace(/>/g, '&gt;') : 'No refactored code available.'}</code></pre>
    </div>

    <div class="card">
        <h2>Detected Issues (${data.recommendations.length})</h2>
        ${data.recommendations.map(r => `
            <div class="issue ${r.severity}">
                <strong>[${r.severity}] ${r.rule_name}</strong>
                <p>${r.description}</p>
                <p><em>Strategy:</em> ${r.strategy}</p>
            </div>
        `).join('')}
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function applyCode() {
            vscode.postMessage({ command: 'applyCode' });
        }

        const radarData = ${radarDataJSON};
        if (radarData) {
            const ctx = document.getElementById('radarChart').getContext('2d');
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: radarData.labels,
                    datasets: [{
                        label: 'Code Quality',
                        data: radarData.values,
                        backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        borderColor: '#4CAF50',
                        pointBackgroundColor: '#4CAF50',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: '#4CAF50'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255, 255, 255, 0.2)' },
                            grid: { color: 'rgba(255, 255, 255, 0.2)' },
                            pointLabels: { color: 'rgba(255, 255, 255, 0.8)', font: { size: 14 } },
                            ticks: { display: false, min: 0, max: 100 }
                        }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }
    </script>
</body>
</html>`;
}

function deactivate() { }

module.exports = { activate, deactivate };
