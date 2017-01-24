/**
 * This runs in the main Electron process. It creates a browser window to run the Slither.io client
 * and injects a script into the page to start a local server for interacting with the game. If you
 * provide `-v` and `-w`, you will get verbose logs and a visible window; the port can be specified
 * using `-p PORT_NUM` and multiple instances can run in parallel.
 */

var fs = require("fs");
var electron = require("electron");
var commandLineArgs = require('command-line-args')

var options = commandLineArgs([
    { name: 'port', alias: 'p', type: Number, defaultValue: 3000 },
    { name: 'window', alias: 'w', type: Boolean, defaultValue: false },
    { name: 'verbose', alias: 'v', type: Boolean, defaultValue: false }
])

var win = null;
function createWindow() {
    electron.app.log("Loading slither.io...")
    var win = new electron.BrowserWindow({
        x: parseInt(1500 * Math.random()),
        y: parseInt(600 * Math.random()),
        width: 480,
        height: 480,
        show: options.window
    });
    win.loadURL("http://www.slither.io/");

    win.webContents.on("did-finish-load", function () {
        electron.app.log("Injecting script...")
        var inject = fs.readFileSync(__dirname + "/inject.js", "utf8");
        win.webContents.executeJavaScript("PORT_NUM = " + options.port);
        win.webContents.executeJavaScript(inject);
    });
}

electron.app.log = function (msg) {
    if (!options.verbose) return;
    console.log("[" + (new Date()).toLocaleString() + "] " + msg);
}
electron.app.commandLine.appendSwitch("disable-renderer-backgrounding")
electron.app.on("ready", createWindow)
electron.app.on("window-all-closed", function () {
    electron.app.quit()
});
