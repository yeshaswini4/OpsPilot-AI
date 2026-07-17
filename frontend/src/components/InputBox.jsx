import { FiSend } from "react-icons/fi";

function InputBox({ question, setQuestion, sendQuestion, loading, disabled }) {

    const handleKey = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendQuestion();
        }
    };

    return (
        <div className="input-wrapper">
            <input
                className="chat-input"
                type="text"
                placeholder="Ask anything about your documents..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKey}
                disabled={disabled || loading}
            />
            <button
                className="send-btn"
                onClick={sendQuestion}
                disabled={disabled || loading || !question.trim()}
            >
                <FiSend />
            </button>
        </div>
    );

}

export default InputBox;
