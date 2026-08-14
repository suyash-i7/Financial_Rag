import requests


OLLAMA_URL = "http://localhost:11434/api/embed"


text = "Revenue increased during the quarter."


response = requests.post(
    OLLAMA_URL,
    json={
        "model": "embeddinggemma",
        "input": text,
    },
)

response.raise_for_status()

data = response.json()

embedding = data["embeddings"][0]


print("Embedding created successfully.")
print(f"Vector dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")