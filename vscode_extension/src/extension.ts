// vscode_extension/src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Miss_TaskMaster extension is now active!');

    // Register commands
    let disposable = vscode.commands.registerCommand('missTaskmaster.initProject', () => {
        vscode.window.showInformationMessage('Initializing Miss_TaskMaster project...');
        // TODO: Implement project initialization
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
