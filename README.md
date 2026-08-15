# 📊 Financial RAG Assistant

A Retrieval-Augmented Generation (RAG) based financial research assistant that allows users to ask questions about quarterly financial reports and receive grounded answers with document and page-level sources.

The system uses locally hosted Ollama models for embeddings and generation, ChromaDB for vector storage and similarity search, and Streamlit for the user interface.

---

## 🎯 Project Objective

Financial reports contain a large amount of structured and unstructured information distributed across multiple pages and quarterly documents.

Finding a specific financial figure manually can be time-consuming and can also lead to confusion between:

- Different business segments
- Different quarters
- Quarterly vs annual figures
- Similar financial metrics

This project solves the problem by creating a searchable knowledge base from financial reports and using Retrieval-Augmented Generation to answer questions based only on the information available in the uploaded documents.

The system also provides the source filename, quarter, and page number used to generate the answer.

---

# 🏗️ System Architecture

```text
                 Financial PDFs
                       │
                       ▼
                PDF Text Extraction
                       │
                       ▼
              Recursive Text Chunking
                 1200 chars
                 150 char overlap
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
User Question ─────────┘
       │
       ▼
   Query Parser
       │
       ├── Entity
       ├── Quarter
       ├── Metric
       └── Intent
       │
       ▼
 Question Embedding
       │
       ▼
 Semantic Retrieval
       │
       ▼
 Relevant Financial Chunks
       │
       ▼
      Ollama
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