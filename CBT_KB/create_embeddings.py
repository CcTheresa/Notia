import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

print(" Creating embeddings for CBT knowledge base...\n")

# 1. Load processed data
print(" Loading processed data...")
with open('processed_data/all_cbt_data.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

print(f"✅ Loaded {len(documents)} documents\n")

# 2. Load embedding model
print("🧠 Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight model
print("✅ Model loaded (384-dimensional embeddings)\n")

# 3. Extract text from documents
print("📝 Extracting text from documents...")
texts = [doc.get('text') or doc.get('advice_text') for doc in documents]
print(f"✅ Extracted {len(texts)} text chunks\n")

# 4. Create embeddings
print("⚡ Creating embeddings (this may take 1-2 minutes)...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
print(f"✅ Created embeddings with shape: {embeddings.shape}\n")

# 5. Create FAISS index
print(" Building FAISS search index...")
dimension = embeddings.shape[1]  # 384 for MiniLM
index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
index.add(embeddings)
print(f"✅ FAISS index created with {index.ntotal} vectors\n")

# 6. Save everything
print(" Saving embeddings and index...")
os.makedirs('embeddings', exist_ok=True)

# Save FAISS index
faiss.write_index(index, 'embeddings/cbt_faiss.index')

# Save documents metadata
with open('embeddings/documents.json', 'w', encoding='utf-8') as f:
    json.dump(documents, f, indent=2, ensure_ascii=False)

# Save embeddings as numpy array (optional, for backup)
np.save('embeddings/embeddings.npy', embeddings)

print("\n" + "="*60)
print("✅ EMBEDDING CREATION COMPLETE!")
print("="*60)
print(f" Total documents: {len(documents)}")
print(f" Embedding dimension: {dimension}")
print(f" Files saved:")
print(f"   - embeddings/cbt_faiss.index (FAISS search index)")
print(f"   - embeddings/documents.json (document metadata)")
print(f"   - embeddings/embeddings.npy (raw embeddings)")
print("="*60)

print("\n🎉 Your knowledge base is now ready for semantic search!")