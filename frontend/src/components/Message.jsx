function renderMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/^#{1,3} (.+)/gm, "<strong>$1</strong>")
        .replace(/^• (.+)/gm, "<li>$1</li>")
        .replace(/^- (.+)/gm, "<li>$1</li>")
        .replace(/^(\d+)\. (.+)/gm, "<li>$2</li>")
        .replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>")
        .replace(/\n/g, "<br/>");
}

// Detect intent from content to show right badge + icon
function detectIntent(content, isUser) {
    if (isUser) return null;
    const c = content.toLowerCase();
    if (c.includes("keyword search result") || c.includes("appears") && c.includes("time(s)") || c.includes("was found")) return { label: "🔍 Keyword Search", cls: "badge-search" };
    if (c.includes("summarize") || c.includes("summary") || c.includes("overview") || c.startsWith("this document")) return { label: "📄 Document Summary", cls: "badge-summary" };
    if (c.includes("skill") || c.includes("technolog") || c.includes("framework") || c.includes("programming language")) return { label: "💻 Technical Skills", cls: "badge-skills" };
    if (c.includes("project")) return { label: "🚀 Projects", cls: "badge-projects" };
    if (c.includes("education") || c.includes("degree") || c.includes("qualification") || c.includes("university")) return { label: "🎓 Education", cls: "badge-education" };
    if (c.includes("experience") || c.includes("internship") || c.includes("work")) return { label: "💼 Experience", cls: "badge-experience" };
    if (c.includes("email") || c.includes("phone") || c.includes("contact") || c.includes("linkedin") || c.includes("github")) return { label: "📞 Contact Details", cls: "badge-contact" };
    if (c.includes("analysis") || c.includes("strength") || c.includes("improvement") || c.includes("rating") || c.includes("rate")) return { label: "📊 Analysis", cls: "badge-analysis" };
    if (c.includes("couldn't find") || c.includes("not found") || c.includes("no information")) return { label: "❌ Not Found", cls: "badge-notfound" };
    if (c.includes("indexed") || c.includes("uploaded") || c.includes("already in your")) return { label: "✅ Upload Status", cls: "badge-upload" };
    return { label: "🤖 AI Response", cls: "badge-default" };
}

// Group sources by filename
function groupSources(sources) {
    const map = {};
    for (const s of sources) {
        if (!map[s.filename]) map[s.filename] = [];
        if (s.page && !map[s.filename].includes(s.page)) {
            map[s.filename].push(s.page);
        }
    }
    return map;
}

function Message({ role, content, sources, time }) {
    const isUser = role === "user";
    const intent = detectIntent(content, isUser);
    const grouped = sources?.length > 0 ? groupSources(sources) : null;

    return (
        <div className={`message-row ${isUser ? "user-row" : "ai-row"} msg-fadein`}>

            <div className="avatar">
                {isUser ? "🙂" : (intent?.label?.split(" ")[0] || "🤖")}
            </div>

            <div className={`bubble ${isUser ? "user-bubble" : "ai-bubble"}`}>

                {!isUser && intent && (
                    <span className={`intent-badge ${intent.cls}`}>{intent.label}</span>
                )}

                <p
                    className="msg-text"
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
                />

                {grouped && (
                    <div className="source-card">
                        <span className="source-card-label">📎 Sources</span>
                        {Object.entries(grouped).map(([filename, pages]) => (
                            <div key={filename} className="source-file-group">
                                <span className="source-filename">📄 {filename}</span>
                                {pages.length > 0 && (
                                    <div className="source-pages">
                                        {pages.sort((a, b) => a - b).map(p => (
                                            <span key={p} className="source-page-chip">Page {p}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {time && <span className="timestamp">{time}</span>}

            </div>

        </div>
    );
}

export default Message;
