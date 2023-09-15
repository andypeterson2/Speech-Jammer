import { useEffect, useState, useRef } from "react";
import {useNavigate, useLocation} from "react-router-dom";
import Header from "../components/Header";

import { closeSession } from "../util/Auth";

import '../css/Session.css';

export default function Session() {

    const location = useLocation();
    const code = location.pathname.slice(-8);

    const [hasVideo, setHasVideo] = useState(false);
    const [outSrc, setOutSrc] = useState(null);
    const videoRef = useRef(null);

    async function startVideo() {
        if (hasVideo) return;
        setHasVideo(true);
        let videoStream = await window.electronAPI.startVideo();
        console.log(videoStream);
    }

    // Request start of incoming video feed
    useEffect(() => {
        startVideo();
    }, []);

    // Start incoming video feed from my camera
    useEffect(() =>{
        async function getOutStream() {
            const outStream = await navigator.mediaDevices.getUserMedia({video: true})

            // setOutSrc(window.URL.createObjectURL(outStream))
            setOutSrc(outStream)
            let video = videoRef.current;
            if (video) {
                video.srcObject = outStream;
                video.play();
            }
        }
        getOutStream()
    }, [videoRef])

    const navigate = useNavigate();

    const handleQuit = async () => {
        await closeSession();
        navigate('/');
    }

    return (
        <>
            <Header />


            <div className="session-content">
                { code ? <h3 class="code">Code: {code}</h3> : null}

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
                        { outSrc ? <video ref={videoRef} autoPlay={true} playsInline={true} id="outgoing-video-stream" /> : null}
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