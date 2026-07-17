import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "",
    timeout: 120000,
});

export const uploadPDF = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
};

export const askQuestion = async (question) => {
    const res = await api.post("/chat", { question });
    return res.data;
};

export const fetchDocuments = async () => {
    const res = await api.get("/documents");
    return res.data;
};

export const healthCheck = async () => {
    const res = await api.get("/health");
    return res.data;
};

export const resetAll = async () => {
    const res = await api.post("/reset");
    return res.data;
};

export default api;
