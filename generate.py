# import re
import requests
import chromadb
from query_parser import parse_query
import sys

sys.stdout.reconfigure(encoding="utf-8")

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
# ENTITY-BASED RE-RANKING
# ==================================================

entity = query_info["entity"]

if entity == "Jio Platforms":

    ranked = []

    for document, metadata in zip(documents, metadatas):

        text_lower = document.lower()

        if (
            "jio platforms limited" in text_lower
            or "consolidated jio platforms" in text_lower
            or '"jpl"' in text_lower
        ):
            score = 2

        elif "jiostar" in text_lower:
            score = -2

        else:
            score = 0

        ranked.append(
            (score, document, metadata)
        )

    ranked.sort(
        key=lambda x: x[0],
        reverse=True
    )

    documents = [
        item[1]
        for item in ranked
    ]

    metadatas = [
        item[2]
        for item in ranked
    ]


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

STRICT ENTITY RULES:

1. The entity requested in the question must match the entity
   described in the source.

2. Do NOT confuse Jio Platforms / JPL with JioStar.

3. Jio Platforms Limited ("JPL") is different from the
   JioStar business segment.

4. If the question asks for Jio Platforms, prefer sources
   explicitly describing:
   - Jio Platforms Limited
   - Consolidated Jio Platforms Limited
   - JPL

5. If a source describes JioStar, do NOT use its financial
   figures as Jio Platforms figures.

6. Do not confuse quarterly figures with annual figures.

7. Do not use outside knowledge.

8. Do not guess or invent information.

9. If the requested information is not available in a matching
   source, clearly say that it is not available.

10. Give a concise final answer.

Do not expose your reasoning process.
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

Answer the question using only the supplied context.

The requested entity is:
{query_info['entity']}

The requested quarter(s) are:
{query_info['quarters']}

The requested metric is:
{query_info['metric']}

The requested entity and metric must match the source.

If multiple businesses appear in the context, use only the
business that matches the requested entity.

Return only the final answer with the relevant figure and
brief supporting detail.
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