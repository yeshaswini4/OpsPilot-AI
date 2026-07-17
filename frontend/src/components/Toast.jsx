import { useEffect } from "react";
import { FiCheckCircle, FiAlertCircle, FiX } from "react-icons/fi";

function Toast({ message, type, onClose }) {

    useEffect(() => {
        const timer = setTimeout(onClose, 3500);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className={`toast toast-${type}`}>
            <span className="toast-icon">
                {type === "success" ? <FiCheckCircle /> : <FiAlertCircle />}
            </span>
            <span className="toast-message">{message}</span>
            <button className="toast-close" onClick={onClose}>
                <FiX />
            </button>
        </div>
    );

}

export default Toast;
