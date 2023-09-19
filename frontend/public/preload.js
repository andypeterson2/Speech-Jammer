const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    startHost: () => ipcRenderer.invoke('session:host'),
    startClient: () => ipcRenderer.invoke('session:client')
})