import { useState, useCallback, useEffect } from "react";
import { FiMenu } from "react-icons/fi";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import UploadBox from "../components/UploadBox";
import ChatBox from "../components/ChatBox";
import InputBox from "../components/InputBox";
import Toast from "../components/Toast";
import { uploadPDF, askQuestion, fetchDocuments, resetAll } from "../services/api";

const now = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const WELCOME = `👋 Welcome to OpsPilot AI!

I can help you:
📄 Summarize documents
🔍 Find keywords & count occurrences
📚 Answer questions from your PDFs
📊 Extract and analyze information
💻 List skills, projects, education

Upload your first PDF to begin.`;

function Home() {

    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadStatus, setUploadStatus] = useState("");
    const [uploadMessage, setUploadMessage] = useState("");
    const [totalChunks, setTotalChunks] = useState(0);
    const [totalPages, setTotalPages] = useState(0);

    const [messages, setMessages] = useState([
        { role: "assistant", content: WELCOME, time: now() }
    ]);
    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(false);

    const [toast, setToast] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const showToast = (message, type) => setToast({ message, type });
    const closeToast = useCallback(() => setToast(null), []);

    const addAIMessage = (content, sources = null) => {
        setMessages(prev => [...prev, { role: "assistant", content, sources, time: now() }]);
    };

    useEffect(() => {
        fetchDocuments()
            .then(data => { if (data.documents?.length > 0) setUploadedFiles(data.documents); })
            .catch(() => {});
    }, []);

    const handleUpload = async () => {

        if (!selectedFile) return;

        setUploading(true);
        setUploadProgress(0);
        setUploadStatus("");
        setUploadMessage("");

        const interval = setInterval(() => {
            setUploadProgress(prev => {
                if (prev < 30) return prev + 15;   // fast: uploading
                if (prev < 60) return prev + 8;    // medium: extracting
                if (prev < 80) return prev + 4;    // slower: chunking
                if (prev < 95) return prev + 1;    // very slow: embedding
                return prev;                        // hold at 95 until done
            });
        }, 400);

        try {

            const res = await uploadPDF(selectedFile);
            clearInterval(interval);
            setUploadProgress(100);

            if (!uploadedFiles.includes(res.filename)) {
                setUploadedFiles(prev => [...prev, res.filename]);
            }

            setTotalChunks(res.total_chunks);
            setTotalPages(res.total_pages);
            setUploadStatus("success");
            setUploadMessage(res.filename);

            addAIMessage(
                `✅ **${res.filename}** has been successfully indexed.\n\n📃 ${res.total_pages} page(s) • 🧠 ${res.total_chunks} AI chunks\n\nYou can now ask questions. Try:\n• Summarize this document\n• What are the key points?\n• List all skills\n• Find keyword...`
            );

            setTimeout(() => {
                setSelectedFile(null);
                setUploadStatus("");
                setUploadMessage("");
                setUploadProgress(0);
            }, 3000);

        } catch (err) {

            clearInterval(interval);
            setUploadProgress(0);

            if (err.response?.status === 409) {
                setUploadStatus("");
                addAIMessage(
                    `ℹ️ **${selectedFile.name}** is already in your document library. You can start asking questions or upload another PDF.`
                );
                setSelectedFile(null);
            } else {
                const msg = err.response?.data?.detail || "Upload failed. Please try again.";
                setUploadStatus("error");
                setUploadMessage(msg);
                showToast(`❌ ${msg}`, "error");
            }

        } finally {
            setUploading(false);
        }

    };

    const handleSuggest = (q) => {
        setQuestion(q);
    };

    const sendQuestion = async () => {

        if (question.trim() === "") return;

        if (uploadedFiles.length === 0) {
            showToast("⚠ Please upload a PDF first.", "error");
            return;
        }

        const userMessage = { role: "user", content: question, time: now() };
        setMessages(prev => [...prev, userMessage]);
        setQuestion("");
        setLoading(true);

        try {

            const response = await askQuestion(question);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: response.answer,
                sources: response.sources,
                time: now()
            }]);

        } catch (error) {

            const msg = error.response?.status === 500
                ? "I encountered an error processing your question. Please try again."
                : error.response?.data?.detail || "Something went wrong.";
            addAIMessage(msg);

        }

        setLoading(false);

    };

    const handleClearChat = () => {
        setMessages([{ role: "assistant", content: WELCOME, time: now() }]);
        setSidebarOpen(false);
        showToast("Chat cleared.", "success");
    };

    const handleReset = async () => {
        try {
            await resetAll();
            setUploadedFiles([]);
            setMessages([{ role: "assistant", content: WELCOME, time: now() }]);
            showToast("All documents cleared.", "success");
        } catch {
            showToast("Failed to reset.", "error");
        }
        setSidebarOpen(false);
    };

    return (
        <div className="app-layout">

            <Sidebar
                uploadedFiles={uploadedFiles}
                onClearChat={handleClearChat}
                onReset={handleReset}
                open={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
            />

            <main className="main-content">

                <button className="hamburger" onClick={() => setSidebarOpen(true)}>
                    <FiMenu />
                </button>

                <Header />

                <UploadBox
                    selectedFile={selectedFile}
                    setSelectedFile={setSelectedFile}
                    onUpload={handleUpload}
                    uploading={uploading}
                    uploadProgress={uploadProgress}
                    uploadStatus={uploadStatus}
                    uploadMessage={uploadMessage}
                    uploadedFiles={uploadedFiles}
                    totalChunks={totalChunks}
                    totalPages={totalPages}
                    onSuggest={handleSuggest}
                />

                <ChatBox
                    messages={messages}
                    loading={loading}
                    hasDocuments={uploadedFiles.length > 0}
                />

                <InputBox
                    question={question}
                    setQuestion={setQuestion}
                    sendQuestion={sendQuestion}
                    loading={loading}
                    disabled={uploadedFiles.length === 0}
                />

                {uploadedFiles.length === 0 && (
                    <p className="upload-hint-text">⬆ Upload a PDF to enable chat</p>
                )}

            </main>

            {toast && <Toast message={toast.message} type={toast.type} onClose={closeToast} />}

        </div>
    );

}

export default Home;
