import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

print("🔧 Creating embeddings for layered advice...\n")

# Load flattened layered advice
print("📂 Loading flattened data...")
with open('processed_data/flattened_layered_advice.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

print(f"✅ Loaded {len(documents)} layer records\n")

# Load model
print("🧠 Loading sentence transformer...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded (384-dim)\n")

# Extract text
print("📝 Extracting text...")
texts = [doc['text'] for doc in documents]
print(f"✅ {len(texts)} text chunks ready\n")

# Create embeddings
print("⚡ Creating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
embeddings = np.array(embeddings, dtype='float32')

print(f"✅ Shape: {embeddings.shape}\n")

# Build FAISS index
print("🔍 Building FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
print(f"✅ Index has {index.ntotal} vectors\n")

# Save
os.makedirs('embeddings', exist_ok=True)
faiss.write_index(index, 'embeddings/layered_advice_faiss.index')

with open('embeddings/layered_advice_metadata.json', 'w', encoding='utf-8') as f:
    json.dump(documents, f, indent=2, ensure_ascii=False)

np.save('embeddings/layered_embeddings.npy', embeddings)

print("="*50)
print("✅ DONE")
print(f"📊 {len(documents)} layer records")
print(f"📐 {dimension}-dimensional embeddings")
print("="*50)
