const { app, BrowserWindow, ipcMain } = require('electron');
const isDev = require('electron-is-dev');
const path = require('node:path')

async function handleVideoStart() {
    console.log('received request to start video from renderer');
    return 'here is a video stream!';
}

function createWindow() {
    // Create the browser window.
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
        },
    });

    win.maximize();

    // and load the index.html of the app.
    // win.loadFile("index.html");
    win.loadURL(
    isDev
        ? 'http://localhost:3000'
        : `file://${path.join(__dirname, '../build/index.html')}`
    );
    // Open the DevTools.
    if (isDev) {
        win.webContents.openDevTools({ mode: 'detach' });
    }


    // LISTEN FOR APP STUFF
    win.webContents.send('ipc', 'hello from main.js (to renderer)')
    ipcMain.on('ipc', (event, value) => {
        console.log('Received message: ' + value)
    })

}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    ipcMain.handle('video:start', handleVideoStart)
    createWindow()
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});





// Start Python subprocess

// const express = require('express')
// const {spawn} = require('child_process');
// const exp = express()
// const port = 2000

// exp.get('/', (req, res) => {
 
//     var dataToSend;
//     // spawn new child process to call the python script
//     const python = spawn('python3', ['../test.py']);
//     // collect data from script
//     python.stdout.on('data', function (data) {
//         console.log('Pipe data from python script ...');
//         dataToSend = data.toString();
//     });
//     // in close event we are sure that stream from child process is closed
//     python.on('close', (code) => {
//         console.log(`child process close all stdio with code ${code}`);
//         // send data to browser
//         res.send(dataToSend)
//     });
    
// })

// exp.listen(port, () => console.log(`Example app listening on port ${port}!`))