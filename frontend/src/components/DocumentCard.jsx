import { FiFileText } from "react-icons/fi";

function DocumentCard({ filename }) {

    return (
        <div className="doc-card">
            <FiFileText className="doc-icon" />
            <span title={filename}>{filename}</span>
        </div>
    );

}

export default DocumentCard;
