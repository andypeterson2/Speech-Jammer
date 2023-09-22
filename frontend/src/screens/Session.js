import { useEffect, useState, useRef } from "react";
import {useNavigate, useLocation} from "react-router-dom";
import Header from "../components/Header";

import { closeSession } from "../util/Auth";

import '../css/Session.css';

export default function Session(props) {

    const location = useLocation();
    const code = location.pathname.slice(-8);

    const startedSession = useRef(false);
    const [selfSrc, setSelfSrc] = useState(null);
    const videoRef = useRef(null);
    
    async function startHost() {
        console.log('Sending Request to start Host');
        let connection = await window.electronAPI.startHost();
        console.log('Response: ' + connection);
    }

    async function startClient() {
        console.log('Sending Request to start Client');
        let connection = await window.electronAPI.startClient();
        console.log('Response: ' + connection);
    }

    const navigate = useNavigate();

    const handleQuit = async () => {
        await closeSession();
        navigate('/');
    }

    // Attempt to start python Client
    useEffect(() => {
        if(!startedSession.current) {
            if(props.host) startHost();
            else if(props.client) startClient();
        }

        return () => startedSession.current = true;
    }, []);

    // Start incoming video feed from my camera
    useEffect(() =>{
        async function getOutStream() {
            const outStream = await navigator.mediaDevices.getUserMedia({video: true})

            setSelfSrc(outStream)
            let video = videoRef.current;
            if (video) {
                video.srcObject = outStream;
                video.play();
            }
        }
        getOutStream()
    }, [videoRef])

    return (
        <>
            <Header />


            <div className="session-content">
                { code ? <h3 className="code">Code: {code}</h3> : null}

                <div className="left">
                    <div className="video-stream" id="incoming-video"></div>
                    <div className="info">
                        <div id="key-accumulation">
                            <span>Accumulated Secret Key</span>
                        </div>
                        <div id="key-rate">
                            <span>Key Rate</span>
                        </div>
                        <div id="error-rate">
                            <span>Error Rate</span>
                        </div>
                    </div>
                </div>
                <div className="right">
                    {/* Video Stream element is a temp placeholder */}
                    <div className="video-stream" id="outgoing-video">
                        { selfSrc ? <video ref={videoRef} autoPlay={true} playsInline={true} id="outgoing-video-stream" /> : null}
                    </div>
                    <div className="chat">
                        <div className="messages">
                            <div className="message" id="incoming-message">
                                <span>text from client 2 words words words words </span>
                            </div>
                            <div className="message" id="outgoing-message">
                                <span>text from client 1</span>
                            </div>
                        </div>
                        <form className="typing">
                            <input type="text" name="Message" id="text" placeholder="Message"/>
                            <input type="submit" value="Send" id="send"/>
                        </form>
                    </div>

                    <button id="quit" onClick={handleQuit}>End Session</button>
                </div>
            </div>
        </>
    )
}