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

    context.subscriptions.push(initProjectDisposable, runOrchestrationDisposable);
}

export function deactivate() {}
