import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

print("🔍 Testing CBT Knowledge Base Retrieval\n")

# 1. Load the model (same one used for embeddings)
print("Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Load FAISS index
print("Loading FAISS index...")
index = faiss.read_index('embeddings/cbt_faiss.index')

# 3. Load documents
print("Loading documents...\n")
with open('embeddings/documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

print(f"✅ Loaded {len(documents)} documents from KB\n")
print("="*60)

# 4. Test queries
test_queries = [
    "I always think the worst will happen",
    "I feel like I'm worthless and unlovable",
    "Everything is always my fault",
    "I can't do anything right",
    "People always judge me negatively"
]

def search_kb(query, top_k=3):
    """Search knowledge base for relevant documents"""
    # Convert query to embedding
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)
    
    # Get matching documents
    results = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        results.append({
            'rank': i + 1,
            'document': documents[idx],
            'similarity_score': float(1 / (1 + dist))  # Convert distance to similarity
        })
    
    return results

# Test each query
for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"TEST QUERY #{i}: \"{query}\"")
    print('='*60)
    
    results = search_kb(query, top_k=3)
    
    for result in results:
        doc = result['document']
        print(f"\n📄 Rank {result['rank']} (Similarity: {result['similarity_score']:.3f})")
        print(f"   Type: {doc.get('type', 'N/A')}")
        print(f"   Classification: {doc.get('classification', 'N/A')}")
        print(f"   Situation: {doc['situation'][:100]}...")
        print(f"   Thoughts: {doc['thoughts'][:100]}...")

print("\n" + "="*60)
print("✅ RETRIEVAL TEST COMPLETE!")
print("="*60)

# Interactive mode
print("\n💬 Try your own query (or press Enter to skip):")
user_query = input("Your query: ").strip()

if user_query:
    print(f"\n🔍 Searching for: \"{user_query}\"\n")
    results = search_kb(user_query, top_k=3)
    
    for result in results:
        doc = result['document']
        print(f"\n📄 Match {result['rank']} (Score: {result['similarity_score']:.3f})")
        print(f"Type: {doc.get('type', 'N/A')}")
        print(f"Classification: {doc.get('classification', 'N/A')}")
        print(f"\n{doc['text']}\n")
        print("-"*60)

print("\n✨ Retrieval system is working!")