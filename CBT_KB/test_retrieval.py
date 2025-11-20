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


print(f"✅ Loaded {len(documents)} documents from KB")
therapeutic_count = sum(1 for doc in documents if doc.get('type') == 'therapeutic_advice')
print(f"   📚 {therapeutic_count} therapeutic advice entries")
print(f"   📖 {len(documents) - therapeutic_count} CBT example entries\n")
print("="*60)


# 4. Test queries
test_queries = [
    "I always think the worst will happen",
    "I feel like I'm worthless and unlovable",
    "Everything is always my fault",
    "I can't do anything right",
    "I'm afraid of change and uncertainty"
]


def search_kb(query, top_k=5, filter_advice_only=True, min_results=1):
    """
    Search knowledge base for relevant documents
    
    Args:
        query: User's journal entry or emotional state
        top_k: How many results to retrieve (default 5)
        filter_advice_only: If True, only return therapeutic advice (default True)
        min_results: Minimum results to return even if low score (default 1)
    """
    # Convert query to embedding
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Search FAISS index - cast wider net if filtering
    # Cast WIDER net (×10) to ensure we find enough advice after filtering
    search_k = min(top_k * 10 if filter_advice_only else top_k, len(documents))
    distances, indices = index.search(query_embedding, search_k)
    
    # Get matching documents
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        doc = documents[idx]
        
        # Filter: only include therapeutic advice
        if filter_advice_only and doc.get('type') != 'therapeutic_advice':
            continue
        
        results.append({
            'document': doc,
            'similarity_score': float(1 / (1 + dist))  # Convert distance to similarity
        })
        
        # Stop once we have enough advice entries
        if len(results) >= top_k:
            break
    
    # Ensure we always return at least min_results (even if scores are low)
    if len(results) < min_results and filter_advice_only:
        # Emergency fallback: get ANY therapeutic advice
        remaining_needed = min_results - len(results)
        for i, doc in enumerate(documents):
            if doc.get('type') == 'therapeutic_advice' and i not in indices[0][:search_k]:
                results.append({
                    'document': doc,
                    'similarity_score': 0.0  # Mark as low confidence
                })
                if len(results) >= min_results:
                    break
    
    return results


# Test each query
for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"TEST QUERY #{i}: \"{query}\"")
    print('='*60)
    
    results = search_kb(query, top_k=5)
    
    for rank, result in enumerate(results, 1):
        doc = result['document']
        score = result['similarity_score']
        
        print(f"\n📄 Match {rank} (Similarity: {score:.3f})")
        print(f"This may relate to: {doc.get('issue', 'general coping').replace('_', ' ').title()}")
        print(f"Strategy type: {doc.get('sub_type', 'N/A').replace('_', ' ').title()}")
        print(f"Emotions addressed: {', '.join(doc.get('emotions', []))}")
        
        # Print the advice text
        advice = doc.get('advice_text', 'N/A')
        print(f"\n💡 {advice}\n")
        print("-"*60)


print("\n" + "="*60)
print("✅ RETRIEVAL TEST COMPLETE!")
print("="*60)


# Interactive mode
print("\n💬 Try your own query (or press Enter to skip):")
user_query = input("Your query: ").strip()


if user_query:
    print(f"\n🔍 Searching for: \"{user_query}\"\n")
    results = search_kb(user_query, top_k=5)
    
 
    for rank, result in enumerate(results, 1):
        doc = result['document']
        score = result['similarity_score']
            
        print(f"\n📄 Match {rank} (Similarity: {score:.3f})")
            
           
        print(f"This may relate to: {doc.get('issue', 'general coping').replace('_', ' ').title()}")
        print(f"Strategy type: {doc.get('sub_type', 'N/A').replace('_', ' ').title()}")
        print(f"Emotions addressed: {', '.join(doc.get('emotions', []))}")
            
        # Print the advice text
        advice = doc.get('advice_text', 'N/A')
        print(f"\n💡 {advice}\n")
        print("-"*60)


print("\n✨ Retrieval system is working!")
