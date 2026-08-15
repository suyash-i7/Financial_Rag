# 📊 Financial RAG Assistant

A local Retrieval-Augmented Generation (RAG) application for asking questions about quarterly financial reports.

The application allows users to upload financial reports, index them into a vector database, and ask natural-language questions about the uploaded documents.

The system retrieves relevant sections from the financial reports and uses locally running Ollama models to generate grounded answers with document and page-level source information.

---

## 🎯 Project Objective

Financial reports contain large amounts of information distributed across many pages and multiple quarterly documents.

Finding a specific financial figure manually can be time-consuming and can lead to confusion between:

- Different quarters
- Different financial metrics
- Different business segments
- Quarterly and annual figures

This project provides a simple RAG-based financial research assistant that allows users to ask questions directly about uploaded financial reports.

The system retrieves relevant document chunks and generates answers using only the retrieved context.

---

# 🏗️ System Architecture

```text
                Financial Reports
                       │
                       ▼
                PDF Text Extraction
                       │
                       ▼
                Recursive Chunking
                 1200 characters
                 150 overlap
                       │
                       ▼
             Ollama Embedding Model
                embeddinggemma
                       │
                       ▼
                   ChromaDB
                 Vector Database
                       │
                       │
                 User Question
                       │
                       ▼
                 Query Parser
                       │
                       ▼
              Question Embedding
                       │
                       ▼
                Similarity Search
                       │
                       ▼
              Relevant Text Chunks
                       │
                       ▼
               Ollama LLM
               llama3.2:3b
                       │
                       ▼
              Grounded Answer
                       │
                       ▼
             Answer + Sources
                       │
                       ▼
                 Streamlit UI
```

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| Ollama | Local AI model execution |
| embeddinggemma | Text embeddings |
| llama3.2:3b | Answer generation |
| ChromaDB | Vector database |
| pypdf | PDF text extraction |
| LangChain Text Splitters | Text chunking |
| Requests | Communication with Ollama |

---

# 📂 Project Structure

```text
Financial_rag/
│
├── app.py
│       Streamlit user interface
│
├── vector_store.py
│       PDF extraction, chunking,
│       embedding and ChromaDB indexing
│
├── retrieve.py
│       Retrieval testing
│
├── generate.py
│       Question processing, retrieval
│       and answer generation
│
├── query_parser.py
│       Entity, quarter, metric and
│       intent detection
│
├── test_embedding.py
│       Embedding model testing
│
├── requirements.txt
│       Python dependencies
│
├── README.md
│       Project documentation
│
├── .gitignore
│
└── data/
        Uploaded financial reports
```

The `chroma_db/` directory is created automatically when documents are indexed.

---

# 💻 Requirements

Before running the project, make sure the following are installed:

- Python 3.10 or newer
- Git
- Ollama

A computer with enough RAM to run the selected local LLM is also required.

---

# 🚀 Installation

## 1. Clone the repository

Replace `YOUR_GITHUB_REPOSITORY_URL` with the URL of this repository.

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Move into the project directory:

```bash
cd Financial_rag
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you can use:

```powershell
.venv\Scripts\activate.bat
```

---

## 3. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

---

# 🤖 Ollama Setup

This project uses Ollama to run the AI models locally.

After installing Ollama, verify the installation:

```powershell
ollama --version
```

---

## 4. Download the embedding model

```powershell
ollama pull embeddinggemma
```

Verify:

```powershell
ollama list
```

---

## 5. Download the language model

```powershell
ollama pull llama3.2:3b
```

Verify:

```powershell
ollama list
```

The list should contain:

```text
embeddinggemma
llama3.2:3b
```

Make sure Ollama is running before using the application.

---

# 📄 Adding Financial Reports

The application supports PDF financial reports.

Financial reports do not need to be manually added to the GitHub repository.

Start the Streamlit application:

```powershell
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

Use the **Upload Financial Reports** section to select one or more PDF files.

---

# 📚 Indexing Documents

After uploading the financial reports:

1. Select one or more PDF files.
2. Click:

```text
🚀 Index Documents
```

The application will:

```text
PDF
 ↓
Extract text
 ↓
Split into chunks
 ↓
Generate embeddings
 ↓
Store embeddings in ChromaDB
```

The current chunking configuration is:

```text
Chunk size:    1200 characters
Chunk overlap: 150 characters
```

The vector database is persisted locally in:

```text
chroma_db/
```

---

# 💬 Asking Questions

After indexing the documents, enter a question in the question box.

For example:

```text
What was Jio Platforms EBITDA in Q4 FY26?
```

Click:

```text
🔍 Ask
```

The system will:

1. Analyze the question.
2. Identify the relevant entity, quarter, metric and intent.
3. Generate an embedding for the question.
4. Search ChromaDB.
5. Retrieve relevant financial-report chunks.
6. Pass the retrieved context to Ollama.
7. Generate a grounded answer.
8. Display source document and page information.

---

# 🧠 Example

### Question

```text
What was Jio Platforms EBITDA in Q4 FY26?
```

### Answer

```text
Jio Platforms' EBITDA in Q4 FY26 was ₹20,060 crore.
```

### Source

```text
24042026_Media_Release_RIL_Q4_FY2025-26_Financial_and_Operational_Performance.pdf
Page 5
```

---

# 🧪 Example Questions

The following questions can be used to test the application.

### 1. Financial Metric

```text
What was Jio Platforms EBITDA in Q4 FY26?
```

### 2. EBITDA Margin

```text
What was Jio Platforms EBITDA margin in Q4 FY26?
```

### 3. Profitability

```text
What was Jio Platforms profit after tax in Q4 FY26?
```

### 4. Growth

```text
How much did Jio Platforms EBITDA grow year-over-year in Q4 FY26?
```

### 5. Business Segment

```text
What was JioStar EBITDA in Q4 FY26?
```

### 6. Operational Information

```text
What was Jio Platforms' total subscriber base in Q4 FY26?
```

### 7. Company-Level Financial Information

```text
What was Reliance Industries' capital expenditure in Q4 FY26?
```

### 8. Unsupported / Trap Question

```text
What was Jio Platforms EBITDA in Q4 FY20?
```

For information that is not available in the uploaded documents, the system is instructed not to invent an answer.

---

# 🔐 Grounding and Hallucination Control

The language model is instructed to answer only from the retrieved financial-report context.

The system follows these principles:

- Do not use outside knowledge.
- Do not guess or invent financial figures.
- Match the requested entity.
- Match the requested quarter.
- Match the requested metric.
- Do not confuse different business segments.
- Do not confuse quarterly and annual figures.
- Clearly state when requested information is unavailable.

This is particularly important for financial applications because unsupported financial figures can lead to misleading conclusions.

---

# 📌 Source Attribution

The application displays the sources used for the generated answer.

Example:

```text
Document:
24042026_Media_Release_RIL_Q4_FY2025-26_Financial_and_Operational_Performance.pdf

Quarter:
Q4 FY2025-26

Page:
5
```

This allows users to verify the generated answer against the original financial report.

---

# 🔄 Complete Workflow

```text
Upload PDF
     ↓
Index Documents
     ↓
PDF Extraction
     ↓
Recursive Chunking
     ↓
Ollama Embeddings
     ↓
ChromaDB
     ↓
User Question
     ↓
Query Analysis
     ↓
Question Embedding
     ↓
Similarity Search
     ↓
Relevant Chunks
     ↓
Ollama LLM
     ↓
Grounded Answer
     ↓
Sources
```

---

# ⚠️ Limitations

The current system has the following limitations:

1. The quality of answers depends on the quality of text extracted from the PDF.
2. Scanned or image-only PDFs may not be processed correctly.
3. Complex financial tables may lose some structure during PDF text extraction.
4. Retrieval quality depends on the embedding model and chunking strategy.
5. The local language model has limited reasoning capabilities compared with larger hosted models.
6. The system cannot reliably answer questions about information that does not exist in the uploaded reports.
7. The current system is designed for the uploaded financial documents and is not a live financial-data service.
8. The application currently works with PDF financial reports.

---

# 🔮 Future Improvements

Possible future improvements include:

- Better financial table extraction
- Hybrid keyword and semantic search
- Retrieval reranking
- Improved entity-aware retrieval
- Multi-quarter comparison
- Conversation history
- Better financial reasoning
- Automated evaluation
- Support for additional document formats
- Cloud deployment

---

# ▶️ Quick Start

For users who already have Python and Ollama installed:

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd Financial_rag

python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt

ollama pull embeddinggemma
ollama pull llama3.2:3b

python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

Upload the financial reports, click **Index Documents**, and start asking questions.

---

# 👨‍💻 Project Status

The project currently provides an end-to-end local Financial RAG pipeline:

```text
PDF
 ↓
Extraction
 ↓
Chunking
 ↓
Embeddings
 ↓
ChromaDB
 ↓
Retrieval
 ↓
Ollama LLM
 ↓
Grounded Answer
 ↓
Source Attribution
 ↓
Streamlit UI
```

The project demonstrates how Retrieval-Augmented Generation can be applied to financial documents while maintaining source-level traceability.