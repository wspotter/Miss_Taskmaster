// vscode_extension/src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Miss_TaskMaster extension is now active!');

    // Register commands
    let initProjectDisposable = vscode.commands.registerCommand('missTaskmaster.initProject', () => {
        vscode.window.showInformationMessage('Initializing Miss_TaskMaster project...');
        // TODO: Implement project initialization by calling MCP server
    });

    let runOrchestrationDisposable = vscode.commands.registerCommand('missTaskmaster.runOrchestration', () => {
        vscode.window.showInformationMessage('Running orchestration...');
        // TODO: Call MCP server to run orchestration
    });

    let showProjectPlanDisposable = vscode.commands.registerCommand('missTaskmaster.showProjectPlan', () => {
        ProjectPlanPanel.createOrShow(context.extensionUri);
    });

    context.subscriptions.push(initProjectDisposable, runOrchestrationDisposable, showProjectPlanDisposable);
}

export function deactivate() {}

class ProjectPlanPanel {
    public static currentPanel: ProjectPlanPanel | undefined;
    public static readonly viewType = 'projectPlan';

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.ViewColumn.Beside
            : undefined;

        if (ProjectPlanPanel.currentPanel) {
            ProjectPlanPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            ProjectPlanPanel.viewType,
            'Project Plan',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        ProjectPlanPanel.currentPanel = new ProjectPlanPanel(panel, extensionUri);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this._update();

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }

    public dispose() {
        ProjectPlanPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.title = 'Project Plan';
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Project Plan</title>
        </head>
        <body>
            <h1>Miss_TaskMaster Project Plan</h1>
            <p>Project plan visualization will be implemented here.</p>
            <div id="plan"></div>
            <script>
                // TODO: Load and display project plan from MCP server
                document.getElementById('plan').innerHTML = '<p>Loading...</p>';
            </script>
        </body>
        </html>`;
    }
}
