import '../../css/Message.css';

export default function Message(props) {

    if(!props.time || !props.name) return;

    return (
        <div class="message">
            {`[${props.time}]<${props.name}> ${props.children}`}
        </div>
    )
}