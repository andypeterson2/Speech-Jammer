import Logo from "../assets/Logo.png";
// import Waveforms from "../assets/Waveforms.png";

import "../css/Header.css";

/* 
 * props.status: str
 *      - waiting: establishing connection
 *      - good: communicatons secure
 *      - bad:  eavesdropper detected
 */
export default function Header(props) {

    function getStatusText(status) {
        switch(status) {
            case "waiting":
                return "Establishing Connection ..."

            case "good":
                return "Communcations Secure"

            case "bad":
                return "Eavesdropper Detected"

            default:
                return ""
        }
    }

    return(
        <div className="header">
            <img src={Logo} alt="UCSD Logo" id="logo" />
            <h1>QKD Video Chat</h1>
            <div class={`status ${(props.status)}`}>{getStatusText(props.status)}</div>
        </div>
    );
}