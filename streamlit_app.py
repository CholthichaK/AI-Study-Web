import json
import requests
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import io
import networkx as nx
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Study & Code Assistant",
    page_icon="AI",
    layout="wide",
)
st.markdown("""
<style>
/* ── Mint Gradient Theme ── */
:root {
    --mint-950: #073d31;
    --mint-900: #0b5b49;
    --mint-800: #117a61;
    --mint-700: #159a78;
    --mint-600: #21b98d;
    --mint-500: #35d1a2;
    --mint-300: #8ee6c9;
    --mint-200: #c9f3e5;
    --mint-100: #e8faf3;
    --mint-50: #f4fdf9;
    --panel: rgba(237, 252, 246, 0.78);
    --panel-strong: rgba(232, 250, 243, 0.94);
    --line: rgba(53, 209, 162, 0.36);
    --shadow: 0 18px 48px rgba(7, 61, 49, 0.16);
}

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    height: 100%;
    overflow: hidden;
    font-size: 14px;
}

/* Main app background */
.stApp {
    background:
        radial-gradient(circle at 12% 14%, rgba(244, 253, 249, 0.92) 0, rgba(244, 253, 249, 0) 28%),
        radial-gradient(circle at 82% 8%, rgba(142, 230, 201, 0.55) 0, rgba(142, 230, 201, 0) 30%),
        linear-gradient(135deg, #e9fbf5 0%, #d0f5e8 35%, #b5ecd9 68%, #ddf8ef 100%);
    background-attachment: fixed;
}
[data-testid="stMainBlockContainer"] {
    height: 100vh;
    max-width: min(1880px, 96vw);
    overflow: hidden;
    padding: 3.25rem 2rem 0.8rem;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    height: 100%;
    min-height: 0;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] {
    min-height: 0;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {
    align-items: stretch;
    gap: 0.85rem;
    height: calc(100vh - 9.25rem);
    min-height: 0;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    background: var(--panel);
    border: 1px solid rgba(255, 255, 255, 0.62);
    border-radius: 12px;
    box-shadow: var(--shadow);
    height: 100%;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1rem 1rem 1.1rem;
    scrollbar-color: var(--mint-500) transparent;
    scrollbar-width: thin;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]::-webkit-scrollbar {
    width: 8px;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]::-webkit-scrollbar-thumb {
    background: rgba(33, 185, 141, 0.6);
    border-radius: 999px;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
    min-height: 100%;
    gap: 0.52rem;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) > [data-testid="stVerticalBlock"] {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] {
    flex: 1 1 auto;
    height: auto !important;
    min-height: 0;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
    height: 100% !important;
    min-height: 0;
    overflow-y: auto;
    padding-bottom: 0.85rem;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stElementContainer"]:has([data-testid="stChatInput"]) {
    flex: 0 0 auto;
    padding-top: 0.65rem;
    padding-bottom: 0.25rem;
}
/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #b2edd8 0%, #88d8b8 100%);
}
/* Top header bar */
[data-testid="stHeader"] {
    background: linear-gradient(90deg, #3ecfa0 0%, #2bb889 100%);
}
/* Main title */
h1 {
    color: #1a7a5e !important;
    font-size: clamp(1.55rem, 2vw, 2.05rem) !important;
    letter-spacing: 0 !important;
    line-height: 1.05 !important;
    margin-bottom: 0.35rem !important;
    text-shadow: 0 1px 3px rgba(62, 207, 160, 0.25);
}
/* Subheaders */
h2, h3 {
    color: #1e9470 !important;
    letter-spacing: 0 !important;
    font-size: clamp(1.15rem, 1.55vw, 1.45rem) !important;
    line-height: 1.12 !important;
    margin-bottom: 0.35rem !important;
}
[data-testid="stHeadingWithActionElements"] a {
    display: none !important;
}
/* Markdown text */
.stMarkdown p, .stMarkdown li {
    color: #1b4d3e;
}
/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3ecfa0 0%, #27b589 100%);
    color: #0d3d2e !important;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.88rem !important;
    min-height: 2.22rem;
    transition: all 0.2s ease;
    box-shadow: 0 8px 18px rgba(39, 181, 137, 0.24);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1aaf7a 0%, #148a5e 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(20, 138, 94, 0.55) !important;
    transform: translateY(-1px);
}
.stButton > button:disabled {
    background: #8ecfb8 !important;
    color: #2d6e55 !important;
    box-shadow: none;
    transform: none;
    opacity: 0.75;
}
/* Input/selectbox/textarea labels */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stFileUploader label,
.stNumberInput label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #1e9470 !important;
    font-weight: 600 !important;
}
/* Text inputs & text areas */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: rgba(244, 253, 249, 0.95);
    border: 1.5px solid #7dd9b8;
    border-radius: 10px;
    color: #1b4d3e !important;
    caret-color: #21b98d !important;
    font-size: 0.88rem !important;
    -webkit-text-fill-color: #1b4d3e !important;
}
.stTextArea textarea[aria-label="Paste code here"] {
    height: 7.35rem !important;
    min-height: 7.35rem !important;
    max-height: 7.35rem !important;
    line-height: 1.45 !important;
    overflow-y: auto !important;
    resize: none !important;
}
[data-testid="stElementContainer"]:has(textarea[aria-label="Paste code here"]),
[data-testid="stTextArea"]:has(textarea[aria-label="Paste code here"]),
[data-testid="stTextAreaRootElement"]:has(textarea[aria-label="Paste code here"]) {
    height: auto !important;
    min-height: 7.65rem !important;
    overflow: visible !important;
}
[data-testid="stElementContainer"]:has(textarea[aria-label="Paste code here"]) {
    margin-bottom: 0.8rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    background-color: #f4fdf9 !important;
    border-color: #21b98d !important;
    box-shadow: 0 0 0 3px rgba(33, 185, 141, 0.22) !important;
    caret-color: #21b98d !important;
    color: #1b4d3e !important;
    outline: none !important;
    -webkit-text-fill-color: #1b4d3e !important;
}
/* Selectbox */
.stSelectbox > div > div {
    background-color: rgba(244, 253, 249, 0.95);
    border: 1.5px solid #7dd9b8;
    border-radius: 10px;
    color: #1b4d3e !important;
    font-size: 0.88rem !important;
}
.stSelectbox > div > div:focus-within {
    background-color: #f4fdf9 !important;
    border-color: #21b98d !important;
    box-shadow: 0 0 0 3px rgba(33, 185, 141, 0.22) !important;
}
input,
textarea,
[contenteditable="true"] {
    caret-color: #21b98d !important;
    color: #1b4d3e !important;
    -webkit-text-fill-color: #1b4d3e !important;
}
input:focus,
textarea:focus,
[contenteditable="true"]:focus {
    caret-color: #21b98d !important;
    color: #1b4d3e !important;
    outline-color: #21b98d !important;
    -webkit-text-fill-color: #1b4d3e !important;
}
/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #e8faf3;
    border: 2px dashed #3ecfa0;
    border-radius: 10px;
    padding: 6px;
}
/* File uploader inner dark button */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] button {
    background-color: #c8f0e0 !important;
    background: #c8f0e0 !important;
    color: #0d3d2e !important;
    border-color: #3ecfa0 !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p {
    color: #1b4d3e !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: rgba(244, 253, 249, 0.9);
    border: 1px solid rgba(53, 209, 162, 0.28);
    border-radius: 12px;
    border-left: 4px solid #3ecfa0;
    box-shadow: 0 10px 24px rgba(7, 61, 49, 0.08);
    margin-bottom: 0.55rem;
}
[data-testid="stChatMessageContent"] {
    color: var(--mint-950);
    line-height: 1.55;
}
/* Chat input — force mint on every layer */
[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] * {
    background-color: #f4fdf9 !important;
    background: #f4fdf9 !important;
    color: #1b4d3e !important;
    caret-color: #27b589 !important;
}
[data-testid="stChatInput"],
[data-testid="stChatInputContainer"] {
    position: sticky !important;
    bottom: 0.45rem !important;
    z-index: 25 !important;
    border: 1.5px solid #7dd9b8 !important;
    border-radius: 12px !important;
    box-shadow: 0 -10px 22px rgba(210, 246, 234, 0.9), 0 10px 24px rgba(7, 61, 49, 0.1) !important;
    height: 3rem !important;
    min-height: 3rem !important;
    max-height: 3rem !important;
    margin-top: 0.7rem !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputContainer"] textarea {
    border: none !important;
    border-radius: 12px !important;
    height: 2.5rem !important;
    min-height: 2.5rem !important;
    max-height: 2.5rem !important;
    line-height: 1.4 !important;
    overflow-y: hidden !important;
    resize: none !important;
    white-space: nowrap !important;
}
/* Info / success / warning / error boxes */
[data-testid="stAlert"] {
    background: linear-gradient(135deg, rgba(231, 250, 240, 0.98), rgba(203, 244, 226, 0.98)) !important;
    border: 1.5px solid rgba(53, 209, 162, 0.48) !important;
    border-left: 4px solid #21b98d !important;
    border-radius: 9px;
    box-shadow: 0 10px 22px rgba(7, 61, 49, 0.08);
    min-height: 0 !important;
    padding: 0.55rem 0.65rem !important;
}
[data-testid="stAlert"] *,
[data-testid="stAlert"] p {
    color: #0b5b49 !important;
    font-weight: 700 !important;
}
.stSuccess {
    background-color: #d4f5e9 !important;
    border-left-color: #27b589 !important;
    color: #1a7a5e !important;
}
.stInfo {
    background-color: #dff6f0 !important;
    border-left-color: #3ecfa0 !important;
    color: #1b4d3e !important;
}
/* Radio buttons */
.stRadio > label {
    color: #1b4d3e;
}
/* Checkboxes */
.stCheckbox > label {
    color: #1b4d3e;
}
/* Captions */
.stCaption {
    color: #3a8a6e !important;
}
/* Horizontal rule */
hr {
    border-color: #a8e6d4;
    margin: 0.5rem 0 0.7rem !important;
}
/* Spinner */
.stSpinner > div {
    border-top-color: #3ecfa0 !important;
}
.busy-card {
    align-items: center;
    background: linear-gradient(135deg, rgba(244, 253, 249, 0.98), rgba(206, 245, 231, 0.96));
    border: 1.5px solid rgba(53, 209, 162, 0.5);
    border-radius: 10px;
    box-shadow: 0 14px 34px rgba(7, 61, 49, 0.16);
    color: var(--mint-950);
    display: flex;
    font-weight: 700;
    gap: 0.8rem;
    margin: 0.6rem 0;
    padding: 0.7rem 0.85rem;
}
.busy-spinner {
    animation: mint-spin 0.9s linear infinite;
    border: 3px solid rgba(53, 209, 162, 0.22);
    border-radius: 999px;
    border-top-color: var(--mint-600);
    display: inline-block;
    height: 1.2rem;
    width: 1.2rem;
}
@keyframes mint-spin {
    to {
        transform: rotate(360deg);
    }
}
/* Study tool modal */
div[data-testid="stDialog"] {
    background-color: rgba(0, 0, 0, 0.30) !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
}
div[data-testid="stDialog"] div[role="dialog"] {
    background: linear-gradient(135deg, rgba(244, 253, 249, 0.76) 0%, rgba(199, 242, 226, 0.62) 100%) !important;
    backdrop-filter: blur(24px) saturate(1.28);
    -webkit-backdrop-filter: blur(24px) saturate(1.28);
    border: 1.5px solid rgba(231, 255, 247, 0.82) !important;
    border-radius: 24px !important;
    box-shadow: 0 30px 90px rgba(5, 45, 34, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.72) !important;
    color: #1b4d3e !important;
    max-height: 88vh !important;
    overflow: auto !important;
}
div[data-testid="stDialog"] h2,
div[data-testid="stDialog"] h3,
div[data-testid="stDialog"] p,
div[data-testid="stDialog"] li,
div[data-testid="stDialog"] label {
    color: #1b4d3e !important;
}
div[data-testid="stDialog"] textarea {
    background-color: rgba(244, 253, 249, 0.82) !important;
}
.mindmap-graph-frame {
    width: 100%;
}
.mindmap-graph-frame + div,
.mindmap-graph-frame + div iframe {
    width: 100% !important;
    max-width: 100% !important;
}
.modal-title {
    color: #1a7a5e;
    font-size: 1.2rem;
    font-weight: 800;
    margin: 0.25rem 0 0.5rem;
}
.code-result-card {
    background: rgba(232, 250, 243, 0.92);
    border: 1.5px solid #7dd9b8;
    border-left: 4px solid #27b589;
    border-radius: 9px;
    box-shadow: 0 8px 22px rgba(39, 181, 137, 0.14);
    margin-top: 0.65rem;
    margin-bottom: 0.45rem;
    padding: 0.55rem 0.7rem;
}
.code-result-card h4 {
    color: #1a7a5e;
    font-size: 0.95rem !important;
    line-height: 1.2 !important;
    margin: 0 !important;
}
.code-result-card p {
    color: #5d8877;
    font-size: 0.74rem;
    margin: 0.18rem 0 0 !important;
}
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(244, 253, 249, 0.72) !important;
    border: 1.5px solid rgba(125, 217, 184, 0.75) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.54);
}
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] .stMarkdown {
    font-size: 0.84rem !important;
    line-height: 1.48 !important;
}
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] h1,
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] h2,
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] h3 {
    font-size: 0.98rem !important;
    line-height: 1.25 !important;
    margin: 0.2rem 0 0.45rem !important;
}
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] li {
    font-size: 0.84rem !important;
    line-height: 1.48 !important;
}
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] pre,
[data-testid="stVerticalBlock"]:has(.code-result-card) [data-testid="stVerticalBlockBorderWrapper"] code {
    white-space: pre-wrap !important;
    word-break: break-word !important;
}
@media (max-width: 900px) {
    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        height: auto;
        overflow: auto;
    }
    [data-testid="stMainBlockContainer"] {
        height: auto;
        overflow: visible;
        padding: 4.6rem 1rem 1rem;
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {
        height: auto;
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        height: auto;
        max-height: none;
        overflow: visible;
        padding: 0.9rem;
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {
        order: 2;
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
        order: 1;
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {
        order: 3;
    }
    [data-testid="stChatInput"],
    [data-testid="stChatInputContainer"] {
        bottom: 0.6rem !important;
    }
}
</style>
""", unsafe_allow_html=True)
st.title("AI Study & Code Assistant")
left, middle, right = st.columns([1.25, 2.2, 1.45])

# Session State
defaults = {
    "uploaded_text_preview": "",
    "chat_history": [],
    "code_text": "",
    "code_result": "",
    "code_result_title": "",
    "modal_mode": None,
    "right_mode": "tools",
    "quiz_data": [],
    "quiz_index": 0,
    "quiz_score": 0,
    "quiz_checked": False,
    "quiz_selected": None,
    "quiz_history": [],
    "flashcards_data": [],
    "flashcard_index": 0,
    "flashcard_show_answer": False,
    "flashcard_history": [],
    "mindmap_data": None,
    "mindmap_history": [],
    "files": [],
    "selected_file_ids": [],
    "active_preview_file": None,
    "preview_modal_open": False,
    "rag_stats": None,
    "folders": ["Default"],
    "selected_upload_folder": "Default",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# API Helpers
def get_selected_payload():
    return {
        "file_ids": st.session_state.selected_file_ids
    }

def refresh_files():
    try:
        response = requests.get(f"{API_URL}/files")
        if response.status_code == 200:
            files = response.json().get("files", [])
            st.session_state.files = files

            existing_ids = [file["id"] for file in files]

            if not st.session_state.selected_file_ids:
                st.session_state.selected_file_ids = existing_ids
            else:
                st.session_state.selected_file_ids = [
                    file_id
                    for file_id in st.session_state.selected_file_ids
                    if file_id in existing_ids
                ]
    except Exception:
        pass

def selected_file_count():
    return len(st.session_state.selected_file_ids)

# Chat Helpers
def add_user_message(content):
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": content,
        }
    )
def add_assistant_text(content):
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": content,
        }
    )
def detect_chat_intent(message):
    text = message.lower()

    if "quiz" in text or "test me" in text or "mcq" in text:
        return "quiz"

    if "flashcard" in text or "flash card" in text:
        return "flashcards"

    if "mindmap" in text or "mind map" in text or "concept map" in text:
        return "mindmap"

    return "chat"

def render_chat_message(msg):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def render_rag_stats():
    stats = st.session_state.rag_stats

    if not stats:
        return

    st.caption(
        f"Selected files: {stats.get('selected_files', 0)} | "
        f"Total chunks: {stats.get('total_chunks', 0)} | "
        f"Chunks used: {stats.get('chunks_used', 0)} | "
        f"Mode: {stats.get('rag_mode', 'lightweight retrieval')}"
    )

def show_busy(message):
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div class="busy-card">
            <span class="busy-spinner"></span>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder

# Tool Helpers
def reset_quiz_state():
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_checked = False
    st.session_state.quiz_selected = None

def load_quiz():
    busy = show_busy("Building a fresh quiz from your selected notes...")
    response = requests.post(
        f"{API_URL}/quiz-json",
        json={
            **get_selected_payload(),
            "previous_questions": st.session_state.quiz_history,
        },
    )
    busy.empty()
    data = response.json()
    result = data.get("result", data)

    if isinstance(result, dict) and "error" in result:
        add_assistant_text(result.get("error", "Could not generate quiz."))
        return

    st.session_state.rag_stats = {
        "selected_files": data.get("selected_files", selected_file_count()),
        "total_chunks": data.get("total_chunks", 0),
        "chunks_used": data.get("chunks_used", 0),
        "rag_mode": data.get("rag_mode", "selected document context"),
    }
    st.session_state.quiz_data = result
    for item in result:
        question = item.get("question")

        if (
            question
            and question not in st.session_state.quiz_history
        ):
                st.session_state.quiz_history.append(question)
    reset_quiz_state()
    st.session_state.modal_mode = "quiz"
    st.session_state.preview_modal_open = False
    st.session_state.right_mode = "tools"

def load_flashcards():
    busy = show_busy("Preparing flashcards for active recall...")

    response = requests.post(
        f"{API_URL}/flashcards-json",
        json={
            **get_selected_payload(),
            "previous_flashcards": st.session_state.flashcard_history,
        },
    )

    busy.empty()

    data = response.json()
    result = data.get("result", data)

    if isinstance(result, dict) and "error" in result:
        add_assistant_text(
            result.get(
                "error",
                "Could not generate flashcards."
            )
        )
        return

    st.session_state.rag_stats = {
        "selected_files": data.get(
            "selected_files",
            selected_file_count(),
        ),
        "total_chunks": data.get(
            "total_chunks",
            0,
        ),
        "chunks_used": data.get(
            "chunks_used",
            0,
        ),
        "rag_mode": data.get(
            "rag_mode",
            "selected document context",
        ),
    }

    st.session_state.flashcards_data = result

    # Save generated flashcards so future sets avoid repetition
    for card in result:

        front = card.get("front", "")

        if (
            front
            and front not in st.session_state.flashcard_history
        ):
            st.session_state.flashcard_history.append(front)

    st.session_state.flashcard_index = 0
    st.session_state.flashcard_show_answer = False

    st.session_state.modal_mode = "flashcards"
    st.session_state.preview_modal_open = False
    st.session_state.right_mode = "tools"

def load_mindmap():
    busy = show_busy("Organizing your notes into a mind map...")

    response = requests.post(
        f"{API_URL}/mindmap-json",
        json={
            **get_selected_payload(),
            "previous_mindmaps": st.session_state.mindmap_history,
        },
    )

    busy.empty()

    data = response.json()
    result = data.get("result", data)

    if isinstance(result, dict) and "error" in result:
        add_assistant_text(
            result.get(
                "error",
                "Could not generate mind map."
            )
        )
        return

    st.session_state.rag_stats = {
        "selected_files": data.get(
            "selected_files",
            selected_file_count(),
        ),
        "total_chunks": data.get(
            "total_chunks",
            0,
        ),
        "chunks_used": data.get(
            "chunks_used",
            0,
        ),
        "rag_mode": data.get(
            "rag_mode",
            "selected document context",
        ),
    }

    st.session_state.mindmap_data = result

    # Save previous mind map structure
    if isinstance(result, dict):

        title = result.get("title", "")

        if (
            title
            and title not in st.session_state.mindmap_history
        ):
            st.session_state.mindmap_history.append(title)

        for node in result.get("nodes", []):

            node_title = node.get("title", "")

            if (
                node_title
                and node_title not in st.session_state.mindmap_history
            ):
                st.session_state.mindmap_history.append(node_title)

    st.session_state.modal_mode = "mindmap"
    st.session_state.preview_modal_open = False
    st.session_state.right_mode = "tools"

def close_tool():
    st.session_state.modal_mode = None
    st.session_state.right_mode = "tools"

def render_modal_close_button(mode):
    spacer, close_col = st.columns([0.92, 0.08], vertical_alignment="center")

    with spacer:
        st.write("")

    with close_col:
        if st.button("X", key=f"close_{mode}_modal"):
            close_tool()
            st.rerun()

@st.dialog("Interactive Quiz", width="large", dismissible=False)
def render_quiz_modal():
    render_modal_close_button("quiz")
    render_quiz_panel()

@st.dialog("Flashcards", width="large", dismissible=False)
def render_flashcards_modal():
    render_modal_close_button("flashcards")
    render_flashcards_panel()

@st.dialog("Mind Map", width="large", dismissible=False)
def render_mindmap_modal():
    render_modal_close_button("mindmap")
    render_mindmap_panel()

@st.dialog("File Preview", width="large", dismissible=False)
def render_file_preview_modal():
    title_col, close_col = st.columns([0.92, 0.08], vertical_alignment="center")

    with title_col:
        if st.session_state.active_preview_file:
            st.markdown(f"**{st.session_state.active_preview_file}**")

    with close_col:
        if st.button("X", key="close_file_preview_modal"):
            st.session_state.preview_modal_open = False
            st.rerun()

    preview_text = st.session_state.uploaded_text_preview or "No preview text available."

    st.text_area(
        "Extracted text",
        preview_text,
        height=440,
        disabled=True,
        key="file_preview_modal_text",
    )

# Right Panel Renderers
def render_quiz_panel():
    if st.session_state.modal_mode != "quiz":
        st.subheader("Interactive Quiz")
        render_rag_stats()

    quiz_data = st.session_state.quiz_data

    if not quiz_data:
        st.info("No quiz loaded.")
        if st.button("Back to Tools", use_container_width=True):
            close_tool()
            st.rerun()
        return

    total = len(quiz_data)
    current_index = st.session_state.quiz_index

    if current_index >= total:
        st.success(f"Quiz complete. Score: {st.session_state.quiz_score}/{total}")

        if st.button("Generate Another Set", use_container_width=True):
            load_quiz()
            st.rerun()

        if st.button("Close Quiz", use_container_width=True):
            close_tool()
            st.rerun()

        return

    item = quiz_data[current_index]
    question = item.get("question", "Question")
    options = item.get("options", [])
    correct_answer = item.get("correct_answer", "")
    explanation = item.get("explanation", "")

    st.caption(f"Question {current_index + 1} of {total}")
    st.markdown(f"**{question}**")

    selected = st.radio(
        "Choose your answer:",
        options,
        index=None,
        key=f"quiz_radio_{current_index}",
    )

    if selected is not None:
        st.session_state.quiz_selected = selected

    if not st.session_state.quiz_checked:
        if st.button("Check Answer", use_container_width=True):
            if st.session_state.quiz_selected is None:
                st.warning("Please select an answer first.")
            else:
                st.session_state.quiz_checked = True

                if st.session_state.quiz_selected == correct_answer:
                    st.session_state.quiz_score += 1
                    st.rerun()
                #     st.success("Correct.")
                # else:
                #     st.error(f"Incorrect. Correct answer: {correct_answer}")

                # st.info(explanation)
                # st.rerun()

    else:
        if st.session_state.quiz_selected == correct_answer:
            st.success("Correct.")
        else:
            st.error(f"Incorrect. Correct answer: {correct_answer}")

        st.info(explanation)

        if st.button("Next Question", use_container_width=True):
            st.session_state.quiz_index += 1
            st.session_state.quiz_checked = False
            st.session_state.quiz_selected = None
            st.rerun()

    st.markdown("---")

    if st.button("Close Quiz", use_container_width=True):
        close_tool()
        st.rerun()

def render_flashcards_panel():
    if st.session_state.modal_mode != "flashcards":
        st.subheader("Flashcards")
        render_rag_stats()

    cards = st.session_state.flashcards_data

    if not cards:
        st.info("No flashcards loaded.")
        if st.button("Back to Tools", use_container_width=True):
            close_tool()
            st.rerun()
        return

    total = len(cards)
    index = st.session_state.flashcard_index
    card = cards[index]

    st.caption(f"Card {index + 1} of {total}")

    st.markdown("**Front**")
    st.info(card.get("front", ""))

    if st.session_state.flashcard_show_answer:
        st.markdown("**Back**")
        st.success(card.get("back", ""))

    if st.button(
        "Hide Answer" if st.session_state.flashcard_show_answer else "Show Answer",
        use_container_width=True,
    ):
        st.session_state.flashcard_show_answer = not st.session_state.flashcard_show_answer
        st.rerun()

    c1, c2 = st.columns(2)

    if c1.button("Previous", use_container_width=True):
        if st.session_state.flashcard_index > 0:
            st.session_state.flashcard_index -= 1
            st.session_state.flashcard_show_answer = False
            st.rerun()

    if c2.button("Next", use_container_width=True):
        if st.session_state.flashcard_index < total - 1:
            st.session_state.flashcard_index += 1
            st.session_state.flashcard_show_answer = False
            st.rerun()

    st.markdown("---")

    if st.button("Generate Another Set", use_container_width=True):
        load_flashcards()
        st.rerun()

    if st.button("Close Flashcards", use_container_width=True):
        close_tool()
        st.rerun()

def build_graph_from_mindmap(mindmap):
    nodes = []
    edges = []
    details_map = {}

    def add_node(node, parent_id=None, level=1, counter=[0]):
        counter[0] += 1
        node_id = f"node_{counter[0]}"

        title = node.get("title", "Untitled")
        details = node.get("details", "")

        if level == 1:
            size = 28
            color = "#3ECFA0"
        elif level == 2:
            size = 22
            color = "#7DD9B8"
        else:
            size = 18
            color = "#BFEFE0"

        nodes.append(
            Node(
                id=node_id,
                label=title,
                size=size,
                color=color,
            )
        )

        details_map[node_id] = {
            "title": title,
            "details": details,
        }

        if parent_id:
            edges.append(
                Edge(
                    source=parent_id,
                    target=node_id,
                )
            )

        for child in node.get("children", []):
            add_node(child, node_id, level + 1, counter)

        return node_id

    root_id = "root"

    nodes.append(
        Node(
            id=root_id,
            label=mindmap.get("title", "Mind Map"),
            size=36,
            color="#1A7A5E",
        )
    )

    details_map[root_id] = {
        "title": mindmap.get("title", "Mind Map"),
        "details": mindmap.get("summary", ""),
    }

    for node in mindmap.get("nodes", []):
        add_node(node, root_id, level=1)

    return nodes, edges, details_map
def create_mindmap_png(mindmap):
    import io
    import textwrap
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    labels = {}
    levels = {}

    counter = {"value": 0}

    def new_id():
        counter["value"] += 1
        return f"node_{counter['value']}"

    root_id = "root"
    root_title = mindmap.get("title", "Mind Map")

    G.add_node(root_id)
    labels[root_id] = textwrap.fill(root_title, 18)
    levels[root_id] = 0

    def add_nodes(parent_id, children, level):
        for child in children:
            node_id = new_id()
            title = child.get("title", "Node")

            G.add_node(node_id)
            G.add_edge(parent_id, node_id)

            labels[node_id] = textwrap.fill(title, 18)
            levels[node_id] = level

            add_nodes(
                node_id,
                child.get("children", []),
                level + 1,
            )

    for node in mindmap.get("nodes", []):
        node_id = new_id()
        title = node.get("title", "Node")

        G.add_node(node_id)
        G.add_edge(root_id, node_id)

        labels[node_id] = textwrap.fill(title, 18)
        levels[node_id] = 1

        add_nodes(
            node_id,
            node.get("children", []),
            2,
        )

    def hierarchy_pos(graph, root):
        pos = {}

        level_groups = {}

        for node, level in levels.items():
            level_groups.setdefault(level, []).append(node)

        max_level = max(level_groups.keys()) if level_groups else 0

        for level, nodes_at_level in level_groups.items():
            count = len(nodes_at_level)

            for i, node in enumerate(nodes_at_level):
                x = (i + 1) / (count + 1)
                y = 1 - (level / (max_level + 1))
                pos[node] = (x, y)

        return pos

    pos = hierarchy_pos(G, root_id)

    plt.figure(figsize=(20, 12))

    node_sizes = []
    for node in G.nodes():
        level = levels.get(node, 1)

        if level == 0:
            node_sizes.append(5200)
        elif level == 1:
            node_sizes.append(4300)
        else:
            node_sizes.append(3400)

    nx.draw(
        G,
        pos,
        labels=labels,
        with_labels=True,
        node_size=node_sizes,
        font_size=7,
        arrows=False,
        linewidths=1,
    )

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
        dpi=220,
    )

    plt.close()
    buffer.seek(0)

    return buffer


def render_mindmap_panel():
    if st.session_state.modal_mode != "mindmap":
        st.subheader("Mind Map")
        render_rag_stats()

    mindmap = st.session_state.mindmap_data

    if not mindmap:
        st.info("No mind map loaded.")
        if st.button("Back to Tools", use_container_width=True):
            close_tool()
            st.rerun()
        return

    if isinstance(mindmap, dict) and "error" in mindmap:
        st.error(mindmap.get("error"))
        st.write(mindmap.get("raw", ""))
        return

    st.markdown(f"**{mindmap.get('title', 'Mind Map')}**")

    png_file = create_mindmap_png(mindmap)

    st.download_button(
        label="Download Mind Map PNG",
        data=png_file,
        file_name="mindmap.png",
        mime="image/png",
        use_container_width=True,
    )
    if mindmap.get("summary"):
        st.caption(mindmap.get("summary"))
        
#         st.download_button(
#     label="Download Mind Map JSON",
#     data=json.dumps(mindmap, indent=2),
#     file_name="mindmap.json",
#     mime="application/json",
#     use_container_width=True,
# )

    nodes, edges, details_map = build_graph_from_mindmap(mindmap)

    is_modal = st.session_state.modal_mode == "mindmap"
    config = Config(
        width=960 if is_modal else 520,
        height=620 if is_modal else 560,
        directed=False,
        physics=False,
        hierarchical=True,
        levelSeparation=170 if is_modal else 150,
        nodeSpacing=145 if is_modal else 100,
        treeSpacing=260 if is_modal else 200,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
    )
    if is_modal:
        config.width = "100%"

    st.markdown('<div class="mindmap-graph-frame"></div>', unsafe_allow_html=True)
    selected_node = agraph(
        nodes=nodes,
        edges=edges,
        config=config,
    )

    st.markdown("---")

    if selected_node:
        details = details_map.get(selected_node)

        if details:
            st.markdown(f"**{details['title']}**")
            st.write(details.get("details") or "No details available.")
    else:
        st.caption("Click a node to view study details.")

    st.markdown("---")

    if st.button("Generate Another Mind Map", use_container_width=True):
        load_mindmap()
        st.rerun()

    if st.button("Close Mind Map", use_container_width=True):
        close_tool()
        st.rerun()

def render_tools_panel():
    st.subheader("AI Tools")

    if selected_file_count() == 0:
        st.warning("Select at least one file to use study tools.")

    if st.button("Generate Quiz", use_container_width=True, disabled=selected_file_count() == 0):
        load_quiz()
        st.rerun()

    if st.button("Generate Flashcards", use_container_width=True, disabled=selected_file_count() == 0):
        load_flashcards()
        st.rerun()

    if st.button("Generate Mind Map", use_container_width=True, disabled=selected_file_count() == 0):
        load_mindmap()
        st.rerun()

    st.markdown("---")
    st.subheader("Code Analyzer")

    code_input = st.text_area(
        "Paste code here",
        value=st.session_state.code_text,
        height=118,
    )
    st.session_state.code_text = code_input

    c1, c2, c3 = st.columns(3)

    if c1.button("Explain", disabled=not code_input.strip()):
        busy = show_busy("Reading the code and preparing an explanation...")
        response = requests.post(
            f"{API_URL}/code/explain",
            json={"code": code_input},
        )
        busy.empty()
        result = response.json().get("result", "")
        st.session_state.code_result_title = "Code Explanation"
        st.session_state.code_result = result
        st.rerun()

    if c2.button("Bugs", disabled=not code_input.strip()):
        busy = show_busy("Reviewing the code for bugs and risks...")
        response = requests.post(
            f"{API_URL}/code/bugs",
            json={"code": code_input},
        )
        busy.empty()
        result = response.json().get("result", "")
        st.session_state.code_result_title = "Bug Analysis"
        st.session_state.code_result = result
        st.rerun()

    if c3.button("Optimize", disabled=not code_input.strip()):
        busy = show_busy("Finding cleaner and faster ways to write it...")
        response = requests.post(
            f"{API_URL}/code/optimize",
            json={"code": code_input},
        )
        busy.empty()
        result = response.json().get("result", "")
        st.session_state.code_result_title = "Optimization Suggestions"
        st.session_state.code_result = result
        st.rerun()

    if st.session_state.code_result:
        st.markdown(
            f"""
            <div class="code-result-card">
                <h4>{st.session_state.code_result_title}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(height=260, border=True):
            st.markdown(st.session_state.code_result)

# Left Panel
with left:
    st.subheader("Sources")

    # new_folder = st.text_input("Create folder", placeholder="Example: OOP Notes")

    # if st.button("Add Folder", use_container_width=True):
    #     folder_name = new_folder.strip()

    #     if folder_name and folder_name not in st.session_state.folders:
    #         st.session_state.folders.append(folder_name)
    #         st.session_state.selected_upload_folder = folder_name
    #         st.success(f"Folder created: {folder_name}")
    #         st.rerun()

    # selected_folder = st.selectbox(
    #     "Upload to folder",
    #     st.session_state.folders,
    #     index=st.session_state.folders.index(st.session_state.selected_upload_folder)
    #     if st.session_state.selected_upload_folder in st.session_state.folders
    #     else 0,
    # )
    # st.session_state.selected_upload_folder = selected_folder

    uploaded_files = st.file_uploader(
        "Drag and drop files here",
        type=["pdf", "docx", "txt", "py", "java", "js", "cpp", "html", "css"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        if st.button("Process Files", use_container_width=True):
            files_payload = []

            for uploaded_file in uploaded_files:
                files_payload.append(
                    (
                        "files",
                        (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        ),
                    )
                )
            busy = show_busy("Extracting text and indexing your sources...")
            response = requests.post(
                f"{API_URL}/upload-multiple",
                data={
                    "folder": st.session_state.selected_upload_folder
                },
                files=files_payload,
            )
            busy.empty()
            if response.status_code == 200:
                data = response.json()
                uploaded = data.get("uploaded", [])

                refresh_files()

                uploaded_names = [
                    item.get("filename", "file")
                    for item in uploaded
                ]
                add_assistant_text(
                    "Files uploaded successfully: "
                    + ", ".join(uploaded_names)
                    + ". Select files from the source list before chatting or generating study tools."
                )
                if uploaded:
                    st.session_state.uploaded_text_preview = uploaded[0].get("preview", "")
                    st.session_state.active_preview_file = uploaded[0].get("filename", "")

                st.success(f"Uploaded {len(uploaded)} file(s).")
                st.rerun()
            else:
                st.error("Upload failed.")

    st.markdown("### File Library")
    refresh_files()
    files = st.session_state.files

    if not files:
        st.info("No files uploaded yet.")
    else:
        grouped = {}

        for file in files:
            folder = file.get("folder", "Default")
            grouped.setdefault(folder, []).append(file)

        for folder, folder_files in grouped.items():
            st.markdown(f"**{folder}**")

            for file in folder_files:
                file_id = file["id"]
                checked = file_id in st.session_state.selected_file_ids

                new_checked = st.checkbox(
                    f"{file['filename']} ({file.get('chunks', 0)} chunks)",
                    value=checked,
                    key=f"file_checkbox_{file_id}",
                )
                if new_checked and file_id not in st.session_state.selected_file_ids:
                    st.session_state.selected_file_ids.append(file_id)

                if not new_checked and file_id in st.session_state.selected_file_ids:
                    st.session_state.selected_file_ids.remove(file_id)

                if st.button("Preview", key=f"preview_{file_id}", use_container_width=True):
                    st.session_state.uploaded_text_preview = file.get("preview", "")
                    st.session_state.active_preview_file = file["filename"]
                    st.session_state.modal_mode = None
                    st.session_state.preview_modal_open = True
                    st.rerun()

    st.markdown("### Selected")
    st.caption(f"{selected_file_count()} file(s) selected")
    st.markdown("### Preview")

    if st.session_state.active_preview_file:
        st.caption(st.session_state.active_preview_file)

    if st.session_state.uploaded_text_preview:
        st.success("Preview is ready.")

        if st.button("Open Preview", use_container_width=True):
            st.session_state.modal_mode = None
            st.session_state.preview_modal_open = True
            st.rerun()
    else:
        st.info("Select Preview on a file to see extracted text.")

# Middle Panel
with middle:
    st.subheader("Chat With Your Notes")

    chat_box = st.container(height=300, border=True)

    with chat_box:
        for msg in st.session_state.chat_history:
            render_chat_message(msg)

    render_rag_stats()
    question = st.chat_input("Ask about your selected notes...")

    if question:
        add_user_message(question)

        intent = detect_chat_intent(question)

        if intent == "quiz":
            load_quiz()

        elif intent == "flashcards":
            load_flashcards()

        elif intent == "mindmap":
            load_mindmap()

        else:
            with chat_box:
                render_chat_message({"role": "user", "content": question})
                busy = show_busy("Searching your selected notes and drafting an answer...")

            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "question": question,
                    "file_ids": st.session_state.selected_file_ids,

                    # Send previous chat messages to backend
                    "history": st.session_state.chat_history[-20:],
                },
            )
            busy.empty()
            data = response.json()
            answer = data.get("answer", "No response.")

            st.session_state.rag_stats = {
                "selected_files": data.get("selected_files", selected_file_count()),
                "total_chunks": data.get("total_chunks", 0),
                "chunks_used": data.get("chunks_used", 0),
                "rag_mode": data.get("rag_mode", "lightweight retrieval"),
            }
            add_assistant_text(answer)

        st.rerun()

# Right Panel
with right:
    render_tools_panel()

if st.session_state.modal_mode == "quiz":
    render_quiz_modal()

elif st.session_state.modal_mode == "flashcards":
    render_flashcards_modal()

elif st.session_state.modal_mode == "mindmap":
    render_mindmap_modal()

if st.session_state.preview_modal_open:
    render_file_preview_modal()
