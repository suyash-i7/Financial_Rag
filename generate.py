# import re
import requests
import chromadb
from query_parser import parse_query


# ==================================================
# CONFIGURATION
# ==================================================

CHROMA_DIR = "chroma_db"

EMBEDDING_URL = "http://localhost:11434/api/embed"
CHAT_URL = "http://localhost:11434/api/chat"

EMBEDDING_MODEL = "embeddinggemma"
LLM_MODEL = "llama3.2:3b"

TOP_K = 4


# ==================================================
# QUARTER DETECTION
# ==================================================



# ==================================================
# CONNECT TO CHROMADB
# ==================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name="financial_reports"
)


# ==================================================
# GET QUESTION
# ==================================================
question = input("Enter your question: ")

query_info = parse_query(question)

print("\nQuery Analysis:")
print(f"Entity   : {query_info['entity']}")
print(f"Quarters : {query_info['quarters']}")
print(f"Metric   : {query_info['metric']}")
print(f"Intent   : {query_info['intent']}")

# ==================================================
# EMBED QUESTION
# ==================================================

response = requests.post(
    EMBEDDING_URL,
    json={
        "model": EMBEDDING_MODEL,
        "input": question,
    },
    timeout=300,
)

response.raise_for_status()

question_embedding = response.json()["embeddings"][0]


# ==================================================
# RETRIEVE
# ==================================================

quarters = query_info["quarters"]

if len(quarters) == 1:

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=TOP_K,
        where={
            "quarter": quarters[0]
        },
    )

else:

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=TOP_K,
    )


documents = results["documents"][0]
metadatas = results["metadatas"][0]


# ==================================================
# BUILD CONTEXT
# ==================================================

context_parts = []

for i, (document, metadata) in enumerate(
    zip(documents, metadatas),
    start=1
):

    context_parts.append(
        f"""
SOURCE {i}:
File: {metadata['source']}
Quarter: {metadata['quarter']}
Page: {metadata['page']}

{document}
""".strip()
    )


context = "\n\n---\n\n".join(context_parts)


# ==================================================
# GROUNDED SYSTEM PROMPT
# ==================================================

system_prompt = """
You are a financial research assistant.

Answer the user's question ONLY using the supplied context.

The user may ask:
- financial metric questions
- comparison questions
- general business questions
- questions without a specified quarter

IMPORTANT:
Do not assume that every question has a quarter or financial metric.

When answering:
1. Identify the entity relevant to the question.
2. Use the requested quarter or quarters when specified.
3. Use the requested financial metric when specified.
4. Do not confuse different businesses or segments.
5. Do not confuse quarterly figures with annual figures.
6. Do not use outside knowledge.
7. Do not guess or invent information.
8. If the requested information is not available in the supplied context, clearly say so.
9. Be concise and factual.
10. Do not expose your reasoning or analysis process.
"""

# ==================================================
# USER PROMPT
# ==================================================

user_prompt = f"""
QUESTION:

{question}


CONTEXT:

{context}


TASK:

Find the information that answers the question.

Before answering, identify:
1. The entity/business requested.
2. The requested quarter/year.
3. The financial metric requested.

Use only a source that matches those requirements.

If none of the supplied sources matches the requested
entity and period, say that the information is not available.
"""


# ==================================================
# GENERATE ANSWER
# ==================================================

response = requests.post(
    CHAT_URL,
    json={
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    },
    timeout=300,
)

response.raise_for_status()

data = response.json()

answer = data["message"]["content"]


# ==================================================
# DISPLAY ANSWER
# ==================================================

print("\n" + "=" * 70)
print("QUESTION")
print("=" * 70)

print(question)


print("\n" + "=" * 70)
print("ANSWER")
print("=" * 70)

print(answer)


# ==================================================
# DISPLAY SOURCES
# ==================================================

print("\n" + "=" * 70)
print("SOURCES")
print("=" * 70)

for metadata in metadatas:

    print(
        f"- {metadata['source']} | "
        f"Quarter: {metadata['quarter']} | "
        f"Page: {metadata['page']}"
    )