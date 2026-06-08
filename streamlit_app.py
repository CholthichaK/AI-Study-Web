import requests
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Study & Code Assistant",
    page_icon="AI",
    layout="wide",
)

st.title("AI Study & Code Assistant")

left, middle, right = st.columns([1.25, 2.2, 1.45])


# -----------------------------
# Session State
# -----------------------------
defaults = {
    "uploaded_text_preview": "",
    "chat_history": [],
    "code_text": "",
    "right_mode": "tools",
    "quiz_data": [],
    "quiz_index": 0,
    "quiz_score": 0,
    "quiz_checked": False,
    "quiz_selected": None,
    "flashcards_data": [],
    "flashcard_index": 0,
    "flashcard_show_answer": False,
    "mindmap_data": None,
    "files": [],
    "selected_file_ids": [],
    "active_preview_file": None,
    "rag_stats": None,
    "folders": ["Default"],
    "selected_upload_folder": "Default",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# API Helpers
# -----------------------------
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


# -----------------------------
# Chat Helpers
# -----------------------------
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


# -----------------------------
# Tool Helpers
# -----------------------------
def reset_quiz_state():
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_checked = False
    st.session_state.quiz_selected = None


def load_quiz():
    add_user_message("Generate a quiz from my selected notes.")

    with st.spinner("Generating quiz..."):
        response = requests.post(
            f"{API_URL}/quiz-json",
            json=get_selected_payload(),
        )
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
    reset_quiz_state()
    st.session_state.right_mode = "quiz"


def load_flashcards():
    add_user_message("Generate flashcards from my selected notes.")

    with st.spinner("Generating flashcards..."):
        response = requests.post(
            f"{API_URL}/flashcards-json",
            json=get_selected_payload(),
        )
        data = response.json()
        result = data.get("result", data)

    if isinstance(result, dict) and "error" in result:
        add_assistant_text(result.get("error", "Could not generate flashcards."))
        return

    st.session_state.rag_stats = {
        "selected_files": data.get("selected_files", selected_file_count()),
        "total_chunks": data.get("total_chunks", 0),
        "chunks_used": data.get("chunks_used", 0),
        "rag_mode": data.get("rag_mode", "selected document context"),
    }

    st.session_state.flashcards_data = result
    st.session_state.flashcard_index = 0
    st.session_state.flashcard_show_answer = False
    st.session_state.right_mode = "flashcards"


def load_mindmap():
    add_user_message("Generate a mind map from my selected notes.")

    with st.spinner("Generating mind map..."):
        response = requests.post(
            f"{API_URL}/mindmap-json",
            json=get_selected_payload(),
        )
        data = response.json()
        result = data.get("result", data)

    if isinstance(result, dict) and "error" in result:
        add_assistant_text(result.get("error", "Could not generate mind map."))
        return

    st.session_state.rag_stats = {
        "selected_files": data.get("selected_files", selected_file_count()),
        "total_chunks": data.get("total_chunks", 0),
        "chunks_used": data.get("chunks_used", 0),
        "rag_mode": data.get("rag_mode", "selected document context"),
    }

    st.session_state.mindmap_data = result
    st.session_state.right_mode = "mindmap"


def close_tool():
    st.session_state.right_mode = "tools"


# -----------------------------
# Right Panel Renderers
# -----------------------------
def render_quiz_panel():
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
                    st.success("Correct.")
                else:
                    st.error(f"Incorrect. Correct answer: {correct_answer}")

                st.info(explanation)

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

    def add_node(node, parent_id=None, counter=[0]):
        counter[0] += 1
        node_id = f"node_{counter[0]}"

        title = node.get("title", "Untitled")
        details = node.get("details", "")

        nodes.append(
            Node(
                id=node_id,
                label=title,
                size=24,
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
            add_node(child, node_id, counter)

        return node_id

    root_id = "root"

    nodes.append(
        Node(
            id=root_id,
            label=mindmap.get("title", "Mind Map"),
            size=32,
        )
    )

    details_map[root_id] = {
        "title": mindmap.get("title", "Mind Map"),
        "details": mindmap.get("summary", ""),
    }

    for node in mindmap.get("nodes", []):
        add_node(node, root_id)

    return nodes, edges, details_map


def render_mindmap_panel():
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

    nodes, edges, details_map = build_graph_from_mindmap(mindmap)

    config = Config(
        width=480,
        height=520,
        directed=False,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=True,
    )

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
        st.caption("Click a node to view details.")

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
        height=200,
    )

    st.session_state.code_text = code_input

    c1, c2, c3 = st.columns(3)

    if c1.button("Explain", disabled=not code_input.strip()):
        add_user_message("Explain this code.")
        with st.spinner("Analyzing code..."):
            response = requests.post(
                f"{API_URL}/code/explain",
                json={"code": code_input},
            )
            result = response.json().get("result", "")
            add_assistant_text(result)
        st.rerun()

    if c2.button("Bugs", disabled=not code_input.strip()):
        add_user_message("Find bugs in this code.")
        with st.spinner("Checking code..."):
            response = requests.post(
                f"{API_URL}/code/bugs",
                json={"code": code_input},
            )
            result = response.json().get("result", "")
            add_assistant_text(result)
        st.rerun()

    if c3.button("Optimize", disabled=not code_input.strip()):
        add_user_message("Optimize this code.")
        with st.spinner("Optimizing code..."):
            response = requests.post(
                f"{API_URL}/code/optimize",
                json={"code": code_input},
            )
            result = response.json().get("result", "")
            add_assistant_text(result)
        st.rerun()


# -----------------------------
# Left Panel
# -----------------------------
with left:
    st.subheader("Sources")

    new_folder = st.text_input("Create folder", placeholder="Example: OOP Notes")

    if st.button("Add Folder", use_container_width=True):
        folder_name = new_folder.strip()

        if folder_name and folder_name not in st.session_state.folders:
            st.session_state.folders.append(folder_name)
            st.session_state.selected_upload_folder = folder_name
            st.success(f"Folder created: {folder_name}")
            st.rerun()

    selected_folder = st.selectbox(
        "Upload to folder",
        st.session_state.folders,
        index=st.session_state.folders.index(st.session_state.selected_upload_folder)
        if st.session_state.selected_upload_folder in st.session_state.folders
        else 0,
    )

    st.session_state.selected_upload_folder = selected_folder

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

            with st.spinner("Extracting files..."):
                    response = requests.post(
                        f"{API_URL}/upload-multiple",
                        data={
                            "folder": st.session_state.selected_upload_folder
                        },
                        files=files_payload,
                    )

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
                    st.rerun()

    st.markdown("### Selected")

    st.caption(f"{selected_file_count()} file(s) selected")

    st.markdown("### Preview")

    if st.session_state.active_preview_file:
        st.caption(st.session_state.active_preview_file)

    if st.session_state.uploaded_text_preview:
        st.text_area(
            "Extracted text",
            st.session_state.uploaded_text_preview,
            height=230,
        )
    else:
        st.info("Select Preview on a file to see extracted text.")


# -----------------------------
# Middle Panel
# -----------------------------
with middle:
    st.subheader("Chat With Your Notes")

    for msg in st.session_state.chat_history:
        render_chat_message(msg)

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
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": question,
                        "file_ids": st.session_state.selected_file_ids,
                    },
                )
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

    render_rag_stats()


# -----------------------------
# Right Panel
# -----------------------------
with right:
    if st.session_state.right_mode == "quiz":
        render_quiz_panel()

    elif st.session_state.right_mode == "flashcards":
        render_flashcards_panel()

    elif st.session_state.right_mode == "mindmap":
        render_mindmap_panel()

    else:
        render_tools_panel()