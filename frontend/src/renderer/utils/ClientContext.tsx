import type { IpcMainEvent } from "electron";
import { useState, createContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import services from './services';

// TODO: Remove placeholder when chat is properly implemented
const initMessages = [
    {
        time: "ti:me",
        name: "Client 1",
        body: "text from client 1",
    },
    {
        time: "ti:me",
        name: "Client 2",
        body: "text from client 2",
    },
]

const initClientContext = {
    selfId: '',
    peerId: '',
    joinPeer: (peer_id: string) => {},
    video: {
        onFrame: () => {},
    },
    chat: {
        messages: initMessages,
        sendMessage: services.chat.sendMessage,
    },
    quitSession: () => {},
}

export const ClientContext = createContext(initClientContext);

export function ClientContextProvider({ children } ) {
    const [selfId, _setSelfId] = useState(initClientContext.selfId);
    const [peerId, _setPeerId] = useState(initClientContext.peerId);
    const [onFrame, _setOnFrame] = useState(initClientContext.video.onFrame);
    const [messages, _setMessages] = useState(initClientContext.chat.messages);

    const navigate = useNavigate();

    const joinPeer = (peer_id) => {
        console.log(`(renderer): Setting peer_id ${peer_id} from user input.`);
        _setPeerId(peer_id);
        services.joinPeer(peer_id)
    }

    const quitSession = () => {
        services.quitSession();
        navigate('/');
    }

    // Establish middleware listeners on initial render
    useEffect(() => {
        console.log(`ClientContext useEffect`);

        // Event emitted when Python subprocess to ready to proceed with chatting
        window.electronAPI.ipcListen('ready', (e: IpcMainEvent, id: string) => {
            console.log(`(renderer): Python backend readied.`)

            // Navigate away from Splash page after receiving self_id
            if(window.location.pathname === '/splash') {
                console.log('(renderer): Closing Splash page.')
                navigate('/');
            }
        })

        window.electronAPI.ipcListen('message', (e: IpcMainEvent, messageData: Object) => {
            console.log(`(renderer): Received chat message with Object structure ${JSON.stringify(messageData)}`)
            _setMessages([...messages, messageData]);
        })

        window.electronAPI.ipcListen('frame',
        (
            event: IpcMainEvent,
            canvasData: {
                frame: Uint8Array;
                height: number;
                width: number
            }
        ) => {
            onFrame(canvasData);
        });

        // Inform main process that ClientContext is ready for IPC communication
        console.log('(renderer): Renderer Ready');
        window.electronAPI.rendererReady();
    }, []);

    return (
        <ClientContext.Provider value={{
            selfId: selfId,
            peerId: peerId,
            joinPeer: joinPeer,
            video: {
                onFrame: onFrame
            },
            chat: {
                messages: messages,
                sendMessage: services.chat.sendMessage
            },
            quitSession: quitSession
        }}>
            {children}
        </ClientContext.Provider>
    )
}