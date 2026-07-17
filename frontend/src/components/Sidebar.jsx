import { FiMessageSquare, FiX, FiTrash2 } from "react-icons/fi";
import DocumentCard from "./DocumentCard";

function Sidebar({ uploadedFiles, onClearChat, onReset, open, onClose }) {

    return (
        <>
            {open && <div className="sidebar-overlay" onClick={onClose} />}

            <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>

                <div className="logo">
                    <div className="sidebar-logo-row">
                        <h2>OpsPilot <span>AI</span></h2>
                        <button className="sidebar-close-btn" onClick={onClose}>
                            <FiX />
                        </button>
                    </div>
                </div>

                <div className="documents">
                    <h4>Uploaded Documents</h4>

                    {uploadedFiles.length === 0 ? (
                        <p className="empty-doc">No documents yet</p>
                    ) : (
                        <div className="doc-list">
                            {uploadedFiles.map((file, i) => (
                                <DocumentCard key={i} filename={file} />
                            ))}
                        </div>
                    )}
                </div>

                <div className="sidebar-actions">
                    <button className="new-chat-btn" onClick={() => { onClearChat(); onClose(); }}>
                        <FiMessageSquare />
                        New Chat
                    </button>

                    {uploadedFiles.length > 0 && (
                        <button className="reset-btn" onClick={() => { onReset(); onClose(); }}>
                            <FiTrash2 />
                            Clear All Docs
                        </button>
                    )}
                </div>

            </aside>
        </>
    );

}

export default Sidebar;
