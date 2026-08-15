import streamlit as st
import subprocess
import sys
from pathlib import Path
import re


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

VECTOR_STORE_SCRIPT = "vector_store.py"
GENERATE_SCRIPT = "generate.py"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 Financial RAG Assistant")

st.write(
    "Ask questions about quarterly financial reports "
    "using ChromaDB and Ollama."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📁 Document Management")

    uploaded_files = st.file_uploader(
        "Upload financial reports",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:

        st.write(
            f"**{len(uploaded_files)} PDF(s) selected**"
        )

        for file in uploaded_files:
            st.caption(f"📄 {file.name}")

    st.divider()

    index_button = st.button(
        "🚀 Index Documents",
        use_container_width=True,
    )


# ============================================================
# INDEX DOCUMENTS
# ============================================================

if index_button:

    if not uploaded_files:

        st.warning(
            "Please upload at least one PDF before indexing."
        )

    else:

        # Save PDFs into data/
        for uploaded_file in uploaded_files:

            file_path = DATA_DIR / uploaded_file.name

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        st.info(
            "📥 Documents uploaded successfully."
        )

        st.info(
            "🔄 Indexing documents..."
        )

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    VECTOR_STORE_SCRIPT
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
            )

            if result.returncode == 0:

                st.success(
                    "✅ Documents indexed successfully!"
                )

                output = result.stdout

                # Extract indexing statistics

                pages_match = re.search(
                    r"Pages with text:\s*(\d+)",
                    output,
                )

                chunks_match = re.search(
                    r"Total chunks:\s*(\d+)",
                    output,
                )

                documents_match = re.search(
                    r"Documents stored:\s*(\d+)",
                    output,
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    if pages_match:
                        st.metric(
                            "Pages",
                            pages_match.group(1),
                        )

                with col2:

                    if chunks_match:
                        st.metric(
                            "Chunks",
                            chunks_match.group(1),
                        )

                with col3:

                    if documents_match:
                        st.metric(
                            "Documents",
                            documents_match.group(1),
                        )

            else:

                st.error(
                    "❌ Document indexing failed."
                )

                if result.stderr:
                    st.code(result.stderr)

        except subprocess.TimeoutExpired:

            st.error(
                "⏱️ Indexing took too long."
            )

        except Exception as e:

            st.error(
                f"❌ Error while indexing: {e}"
            )


# ============================================================
# QUESTION SECTION
# ============================================================

st.header("💬 Ask a Question")

question = st.text_input(
    "Enter your question",
    placeholder=(
        "Example: What was Jio Platforms EBITDA in Q4 FY26?"
    ),
)

ask_button = st.button(
    "🔍 Ask",
    type="primary",
)


# ============================================================
# GENERATE ANSWER
# ============================================================

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "🔎 Searching financial reports..."
        ):

            try:

                # Run generate.py using the current .venv
                result = subprocess.run(
                    [
                        sys.executable,
                        GENERATE_SCRIPT
                    ],
                    input=question + "\n",
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=600,
                )

                # ==================================================
                # GENERATION ERROR
                # ==================================================

                if result.returncode != 0:

                    st.error(
                        "❌ Unable to generate an answer."
                    )

                    if result.stderr:
                        st.code(result.stderr)

                else:

                    # ==================================================
                    # IMPORTANT:
                    # output is created HERE
                    # ==================================================

                    output = result.stdout


                    # ==================================================
                    # EXTRACT ANSWER
                    # ==================================================

                    answer = ""

                    if "ANSWER" in output:

                        answer_section = output.split(
                            "ANSWER",
                            1
                        )[1]

                        if "SOURCES" in answer_section:

                            answer = answer_section.split(
                                "SOURCES",
                                1
                            )[0]

                        else:

                            answer = answer_section


                        # Remove separator lines
                        answer_lines = []

                        for line in answer.splitlines():

                            stripped = line.strip()

                            if not stripped:
                                continue

                            # Ignore lines made only of "="
                            if set(stripped) <= {"="}:
                                continue

                            answer_lines.append(line)


                        answer = "\n".join(
                            answer_lines
                        ).strip()


                    # ==================================================
                    # DISPLAY ANSWER
                    # ==================================================

                    st.divider()

                    st.subheader("🧠 Answer")

                    if answer:

                        st.markdown(answer)

                    else:

                        st.warning(
                            "No answer was generated."
                        )


                    # ==================================================
                    # EXTRACT SOURCES
                    # ==================================================

                    if "SOURCES" in output:

                        sources_section = output.split(
                            "SOURCES",
                            1
                        )[1]

                        source_lines = (
                            sources_section
                            .strip()
                            .splitlines()
                        )


                        st.subheader("📚 Sources")


                        # Avoid duplicate sources
                        seen_sources = set()


                        for line in source_lines:

                            line = line.strip()

                            if not line.startswith("-"):
                                continue

                            source_text = line[1:].strip()

                            if not source_text:
                                continue

                            if source_text in seen_sources:
                                continue

                            seen_sources.add(
                                source_text
                            )

                            st.write(
                                f"📄 {source_text}"
                            )


            except subprocess.TimeoutExpired:

                st.error(
                    "⏱️ The model took too long to respond."
                )

            except Exception as e:

                st.error(
                    f"❌ Error while generating the answer: {e}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Financial RAG Assistant • "
    "ChromaDB + Ollama • "
    "embeddinggemma + llama3.2:3b"
)