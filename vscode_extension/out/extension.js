"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
// vscode_extension/src/extension.ts
const vscode = require("vscode");
function activate(context) {
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
    // Create and register task status tree view
    const taskStatusProvider = new TaskStatusProvider();
    vscode.window.registerTreeDataProvider('taskStatus', taskStatusProvider);
    context.subscriptions.push(initProjectDisposable, runOrchestrationDisposable, showProjectPlanDisposable);
}
function deactivate() { }
class TaskStatusProvider {
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            // Root level - return main categories
            return Promise.resolve([
                new TaskItem('Current Task', 'The task currently being executed', vscode.TreeItemCollapsibleState.None),
                new TaskItem('Pending Tasks', 'Tasks waiting to be executed', vscode.TreeItemCollapsibleState.Collapsed),
                new TaskItem('Completed Tasks', 'Tasks that have been completed', vscode.TreeItemCollapsibleState.Collapsed)
            ]);
        }
        else {
            // TODO: Fetch actual task data from MCP server
            if (element.label === 'Pending Tasks') {
                return Promise.resolve([
                    new TaskItem('GK1.1', 'Gatekeeper task 1.1', vscode.TreeItemCollapsibleState.None),
                    new TaskItem('CA1.1', 'Coding agent task 1.1', vscode.TreeItemCollapsibleState.None)
                ]);
            }
            else if (element.label === 'Completed Tasks') {
                return Promise.resolve([
                    new TaskItem('GK1.0', 'Completed gatekeeper task', vscode.TreeItemCollapsibleState.None)
                ]);
            }
            return Promise.resolve([]);
        }
    }
}
class TaskItem extends vscode.TreeItem {
    constructor(label, tooltip, collapsibleState) {
        super(label, collapsibleState);
        this.label = label;
        this.tooltip = tooltip;
        this.collapsibleState = collapsibleState;
        this.tooltip = tooltip;
        this.description = '';
    }
}
class ProjectPlanPanel {
    static createOrShow(extensionUri) {
        const column = vscode.window.activeTextEditor
            ? vscode.ViewColumn.Beside
            : undefined;
        if (ProjectPlanPanel.currentPanel) {
            ProjectPlanPanel.currentPanel._panel.reveal(column);
            return;
        }
        const panel = vscode.window.createWebviewPanel(ProjectPlanPanel.viewType, 'Project Plan', column || vscode.ViewColumn.One, {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
        });
        ProjectPlanPanel.currentPanel = new ProjectPlanPanel(panel, extensionUri);
    }
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._update();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }
    dispose() {
        ProjectPlanPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
    _update() {
        const webview = this._panel.webview;
        this._panel.title = 'Project Plan';
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }
    _getHtmlForWebview(webview) {
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
ProjectPlanPanel.viewType = 'projectPlan';
//# sourceMappingURL=extension.js.map