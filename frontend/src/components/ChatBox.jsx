import { useEffect, useRef } from "react";
import Message from "./Message";
import Loader from "./Loader";

function ChatBox({ messages, loading, hasDocuments }) {

    const bottomRef = useRef();

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    if (!hasDocuments && messages.length <= 1) {
        return (
            <div className="chat-box empty-state">
                <div className="empty-content">
                    <p className="empty-icon">👋</p>
                    <h3>Welcome to OpsPilot AI</h3>
                    <p>Upload a PDF → Ask Questions → Get Instant AI Answers</p>
                </div>
            </div>
        );
    }

    return (
        <div className="chat-box">

            {messages.map((msg, i) => (
                <Message
                    key={i}
                    role={msg.role}
                    content={msg.content}
                    sources={msg.sources}
                    time={msg.time}
                />
            ))}

            {loading && <Loader />}

            <div ref={bottomRef} />

        </div>
    );

}

export default ChatBox;
