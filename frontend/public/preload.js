const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  startVideo: () => ipcRenderer.invoke('video:start')
})