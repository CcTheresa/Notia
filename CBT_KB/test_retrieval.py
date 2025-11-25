import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

print("🔍 Testing Layered Retrieval System\n")

# Load model
print("Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load FAISS index
print("Loading FAISS index...")
index = faiss.read_index('embeddings/layered_advice_faiss.index')

# Load metadata
print("Loading metadata...\n")
with open('embeddings/layered_advice_metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"✅ Loaded {len(metadata)} layer records")
print(f"   📊 {len(set(m['parent_id'] for m in metadata))} unique advice entries")
print(f"   📐 5 layers per entry (validation, psychoeducation, technique, reframing, journaling)\n")
print("="*60)


def search_layers(query, layer_type=None, top_k=3, threshold=0.0):  # Changed threshold to 0.0
    """
    Search for relevant advice layers - ALWAYS returns results
    
    Args:
        query: User's journal entry or question
        layer_type: Filter by specific layer (validation/psychoeducation/technique/reframing/journaling)
        top_k: Number of results
        threshold: Minimum similarity score (0-1)
    """
    query_emb = model.encode([query])[0]
    
    # Search more than needed for filtering
    search_k = min(top_k * 10, len(metadata))
    distances, indices = index.search(np.array([query_emb]).astype('float32'), search_k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        score = 1 / (1 + dist)
        
        if score < threshold:
            continue
        
        entry = metadata[idx]
        
        # Filter by layer type if specified
        if layer_type and entry['layer_type'] != layer_type:
            continue
        
        results.append({
            'score': float(score),
            'layer': entry['layer_type'],
            'issue': entry['issue'],
            'sub_issue': entry['sub_issue'],
            'emotions': entry.get('emotions', []),
            'text': entry['text']
        })
        
        if len(results) >= top_k:
            break
    
    return results


def stepwise_response(query):
    """Generate initial response - ALWAYS returns something"""
    validation = search_layers(query, layer_type='validation', top_k=1, threshold=0.0)
    psychoed = search_layers(query, layer_type='psychoeducation', top_k=1, threshold=0.0)
    
    # Safety check - if still empty, get ANY validation/psychoed layers
    if not validation:
        validation = [m for m in metadata if m['layer_type'] == 'validation'][:1]
    
    if not psychoed:
        psychoed = [m for m in metadata if m['layer_type'] == 'psychoeducation'][:1]
    
    return {
        'validation': validation[0],
        'psychoeducation': psychoed[0],
        'technique_available': True,
        'deeper_available': True
    }



# Automated tests
test_queries = [
    "I keep putting off work because I'm afraid I'll fail",
    "My friend didn't text back and I think they hate me",
    "I feel worthless no matter what I achieve",
    "I can't stop worrying about everything"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"TEST #{i}: \"{query}\"")
    print('='*60)
    
    response = stepwise_response(query)
    val = response['validation']
    psy = response['psychoeducation']
    
    print(f"\n✅ MATCHED: {val['issue'].replace('_', ' ').title()} > {val['sub_issue'].replace('_', ' ').title()}")
    print(f"📊 Confidence: {val['score']:.3f}")
    print(f" Emotions: {', '.join(val['emotions'])}")
    
    print(f"\n💚 VALIDATION:")
    print(f"   {val['text']}")
    
    print(f"\n📚 UNDERSTANDING:")
    print(f"   {psy['text']}...")
    
    # Show technique preview
    tech = search_layers(query, layer_type='technique', top_k=1, threshold=0.0)
    if tech:
        print(f"\n TECHNIQUE AVAILABLE:")
        print(f"   {tech[0]['text'][:150]}...")
    
    print("-"*60)

print("\n" + "="*60)
print("✅ AUTOMATED TESTS COMPLETE!")
print("="*60)

# Interactive mode
print("\n💬 Try your own query (or press Enter to skip):")
user_query = input("Your query: ").strip()

if user_query:
    print(f"\n🔍 Searching for: \"{user_query}\"\n")
    
    response = stepwise_response(user_query)
    val = response['validation']
    psy = response['psychoeducation']
    
    print(f"✅ MATCHED: {val['issue'].replace('_', ' ').title()} > {val['sub_issue'].replace('_', ' ').title()}")
    print(f"📊 Confidence: {val['score']:.3f}")
    print(f" Emotions: {', '.join(val['emotions'])}\n")
    
    print(f"💚 VALIDATION:")
    print(f"{val['text']}\n")
    
    print(f"📚 UNDERSTANDING:")
    print(f"{psy['text']}\n")

    #keep offering next steps until user is done
    shown_layers = set()

    while True:
    
    # Offer next steps
        print("="*60)
        print("Next steps available:")
        print("  [1] Get a specific technique to try")
        print("  [2] Explore deeper (reframing)")
        print( "[3] See journaling prompt")
        print("  [4] Done")
    
        choice = input("\nChoice (1/2/3/4): ").strip()

        if choice == "4" or not choice:
            break
    
        if choice == "1":
            tech = search_layers(user_query, layer_type='technique', top_k=1, threshold=0.0)
            if tech:
                print(f"\n🛠️  TECHNIQUE:\n{tech[0]['text']}\n")
                shown_layers.add('1')
        
        elif choice == "2":
            reframe = search_layers(user_query, layer_type='reframing', top_k=1, threshold=0.0)
            if reframe:
                print(f"\n🔄 REFRAME YOUR THINKING:\n{reframe[0]['text']}\n")
                shown_layers.add('2')
        
        elif choice == "3":
            journal = search_layers(user_query, layer_type='journaling', top_k=1, threshold=0.0)
            if journal:
                print(f"\n📝 JOURNAL PROMPT:\n{journal[0]['text']}\n")
                shown_layers.add('3')
        
        elif choice in shown_layers:
            print("\n(Already shown - pick another option)\n")

print("\n✨ Layered retrieval system is working!")
