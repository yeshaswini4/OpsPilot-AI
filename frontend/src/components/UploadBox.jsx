import { useRef, useState } from "react";
import { FiUploadCloud, FiFile, FiCheckCircle, FiAlertCircle } from "react-icons/fi";

const MAX_SIZE = 20 * 1024 * 1024;

const SUGGESTED = [
    "Summarize this document",
    "List all skills",
    "What projects are mentioned?",
    "Education details",
    "Contact information",
    "Find keyword...",
];

function UploadBox({
    selectedFile,
    setSelectedFile,
    onUpload,
    uploading,
    uploadStatus,
    uploadMessage,
    uploadedFiles = [],
    totalChunks,
    totalPages,
    uploadProgress,
    onSuggest
}) {

    const inputRef = useRef();
    const [dragging, setDragging] = useState(false);
    const [validationError, setValidationError] = useState("");

    const validate = (file) => {
        if (!file) return "No file selected.";
        if (!file.name.toLowerCase().endsWith(".pdf")) return "Only PDF files are allowed.";
        if (file.size > MAX_SIZE) return "File size exceeds 20 MB.";
        if (file.size === 0) return "File is empty.";
        return "";
    };

    const handleSelect = (file) => {
        const error = validate(file);
        if (error) { setValidationError(error); setSelectedFile(null); }
        else { setValidationError(""); setSelectedFile(file); }
    };

    const onDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        handleSelect(e.dataTransfer.files[0]);
    };

    return (
        <div className="upload-card">

            <div
                className={`drop-zone ${dragging ? "dragging" : ""}`}
                onClick={() => inputRef.current.click()}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
            >
                <FiUploadCloud size={48} className="upload-icon" />
                <h3>Drag & Drop PDF Here</h3>
                <p className="or-text">OR</p>
                <button className="browse-btn" onClick={(e) => { e.stopPropagation(); inputRef.current.click(); }}>
                    Browse Files
                </button>
                <p className="upload-hint">PDF Only • Max 20 MB</p>
                <input ref={inputRef} type="file" accept=".pdf" style={{ display: "none" }}
                    onChange={(e) => handleSelect(e.target.files[0])} />
            </div>

            {validationError && (
                <div className="validation-error"><FiAlertCircle /> {validationError}</div>
            )}

            {selectedFile && (
                <div className="selected-file">
                    <FiFile className="file-icon" />
                    <div className="file-info">
                        <span className="file-name">{selectedFile.name}</span>
                        <span className="file-size">{(selectedFile.size / 1024).toFixed(1)} KB</span>
                    </div>
                </div>
            )}

            {uploading && (
                <div className="progress-bar-wrap">
                    <div className="progress-bar-track">
                        <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }} />
                    </div>
                    <span className="progress-label">
                        {uploadProgress < 30 ? "📤 Uploading..." :
                         uploadProgress < 60 ? "📄 Extracting text..." :
                         uploadProgress < 80 ? "✂️ Chunking..." :
                         uploadProgress < 95 ? "🧠 Generating embeddings..." :
                         "✅ Finalizing..."} {uploadProgress}%
                    </span>
                </div>
            )}

            {selectedFile && !uploading && (
                <button className="upload-btn" onClick={onUpload} disabled={uploading}>
                    Upload PDF
                </button>
            )}

            {uploadStatus === "success" && (
                <div className="upload-success-card">
                    <div className="upload-success-header">
                        <FiCheckCircle className="success-icon-lg" />
                        <div>
                            <div className="success-title">Document Ready</div>
                            <div className="success-filename">📄 {uploadMessage}</div>
                        </div>
                    </div>
                    <div className="upload-success-stats">
                        <span className="stat-chip">📃 {totalPages} Page{totalPages !== 1 ? "s" : ""}</span>
                        <span className="stat-chip">🧠 {totalChunks} AI Chunks</span>
                        <span className="stat-chip ready-chip">✅ Ready for Search</span>
                    </div>
                </div>
            )}

            {uploadStatus === "error" && (
                <div className="status-error">❌ {uploadMessage}</div>
            )}

            {uploadedFiles.length > 0 && (
                <div className="uploaded-files-list">
                    {uploadedFiles.map((f, i) => (
                        <div key={i} className="uploaded-file-badge">
                            <FiCheckCircle className="badge-icon" />
                            <span>{f}</span>
                        </div>
                    ))}
                </div>
            )}

            {uploadedFiles.length > 0 && onSuggest && (
                <div className="suggest-section">
                    <p className="suggest-label">💡 Try asking:</p>
                    <div className="suggest-chips">
                        {SUGGESTED.map((q, i) => (
                            <button key={i} className="suggest-chip" onClick={() => onSuggest(q)}>
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            )}

        </div>
    );
}

export default UploadBox;
