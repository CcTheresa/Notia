import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

print("🔧 Loading models...\n")

# 1. Load emotion classifier (DistilBERT)
EMOTION_LABELS = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
    'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
    'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
    'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
    'relief', 'remorse', 'sadness', 'surprise', 'neutral'
]

emotion_classifier = pipeline(
    "text-classification",
    model="../model",
    top_k=None
)
print("✅ Emotion classifier loaded")

# 2. Load sentence embedding model + FAISS index
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('embeddings/layered_advice_faiss.index')

with open('embeddings/layered_advice_metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print("✅ Embedding model + FAISS index loaded")
print(f"✅ {len(metadata)} advice layers ready\n")
print("="*60)


def extract_emotions(text, threshold=0.5):
    """
    Extract emotions from journal entry using DistilBERT
    
    Returns: List of emotion names above threshold
    """
    result = emotion_classifier(text)
    
    emotions = result[0] if isinstance(result[0], list) else result
    
    detected_emotions = []
    for emo in emotions:
        label = emo['label']
        score = emo['score']
        
        if label.startswith('LABEL_') and score > threshold:
            idx = int(label.split('_')[1])
            emotion_name = EMOTION_LABELS[idx]
            detected_emotions.append({
                'emotion': emotion_name,
                'score': score
            })
    
    # Sort by score
    detected_emotions.sort(key=lambda x: x['score'], reverse=True)
    
    return detected_emotions


def search_with_emotions(journal_entry, layer_type=None, top_k=3):
    """
    Two-stage retrieval:
    1. Detect emotions from journal entry
    2. Semantic search + emotion-based boosting
    
    Returns: Top matches with emotion overlap highlighted
    """
    # Stage 1: Detect emotions
    detected_emotions = extract_emotions(journal_entry, threshold=0.5)
    detected_emotion_names = [e['emotion'] for e in detected_emotions]
    
    print(f"🎭 Detected emotions: {detected_emotion_names}\n")
    
    # Stage 2: Semantic search
    query_emb = embedding_model.encode([journal_entry])[0]
    search_k = min(top_k * 10, len(metadata))
    distances, indices = index.search(np.array([query_emb]).astype('float32'), search_k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        base_score = 1 / (1 + dist)
        entry = metadata[idx]
        
        # Filter by layer type
        if layer_type and entry['layer_type'] != layer_type:
            continue
        
        # Calculate emotion overlap
        entry_emotions = set(entry.get('emotions', []))
        pred_emotions = set(detected_emotion_names)
        overlap = entry_emotions.intersection(pred_emotions)
        
        # Boost score based on emotion overlap
        emotion_boost = len(overlap) * 0.15  # +0.15 per matching emotion
        final_score = base_score + emotion_boost
        
        results.append({
            'score': float(final_score),
            'base_score': float(base_score),
            'emotion_boost': float(emotion_boost),
            'layer': entry['layer_type'],
            'issue': entry['issue'],
            'sub_issue': entry['sub_issue'],
            'emotions': list(entry.get('emotions', [])),
            'emotion_overlap': list(overlap),
            'parent_id': entry['parent_id'],
            'text': entry['text']
        })
    
    # Sort by final score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results[:top_k], detected_emotions


def get_full_advice(parent_id):
    """Get all layers for a matched advice entry"""
    layers = {}
    
    for layer_type in ['validation', 'psychoeducation', 'technique', 'reframing', 'journaling']:
        match = next((m for m in metadata if m['parent_id'] == parent_id and m['layer_type'] == layer_type), None)
        if match:
            layers[layer_type] = match
    
    return layers


# ============================================================
# TESTING
# ============================================================

test_entries = [
    "I keep putting off work because I'm afraid I'll fail",
    "My friend didn't text back and I think they hate me",
    "I feel worthless no matter what I achieve"
]

for i, entry in enumerate(test_entries, 1):
    print(f"\n{'='*60}")
    print(f"TEST #{i}: \"{entry}\"")
    print('='*60)
    
    # Get validation layer match
    matches, emotions = search_with_emotions(entry, layer_type='validation', top_k=1)
    
    if matches:
        match = matches[0]
        
        print(f"✅ MATCHED: {match['issue'].replace('_', ' ').title()} > {match['sub_issue'].replace('_', ' ').title()}")
        print(f"📊 Score: {match['score']:.3f} (base: {match['base_score']:.3f} + emotion boost: {match['emotion_boost']:.3f})")
        print(f"🔗 Emotion overlap: {match['emotion_overlap']}")
        print(f"\n💚 VALIDATION:\n{match['text'][:200]}...\n")
    
    print("-"*60)

print("\n" + "="*60)
print("✅ INTEGRATED SYSTEM TEST COMPLETE!")
print("="*60)

# Interactive mode
print("\n💬 Try your own journal entry (or press Enter to skip):")
user_entry = input("Your entry: ").strip()

if user_entry:
    print(f"\n🔍 Processing: \"{user_entry}\"\n")
    
    matches, emotions = search_with_emotions(user_entry, layer_type='validation', top_k=1)
    
    if matches:
        match = matches[0]
        
        print(f"✅ MATCHED: {match['issue'].replace('_', ' ').title()} > {match['sub_issue'].replace('_', ' ').title()}")
        print(f"📊 Confidence: {match['score']:.3f}")
        print(f"😔 Entry emotions: {[e['emotion'] for e in emotions[:3]]}")
        print(f"🔗 Advice emotions: {match['emotions']}")
        print(f"✨ Overlap: {match['emotion_overlap']}\n")
        
        # Get all layers
        all_layers = get_full_advice(match['parent_id'])
        
        print(f"💚 VALIDATION:")
        print(f"{all_layers['validation']['text']}\n")
        
        print(f"📚 UNDERSTANDING:")
        print(f"{all_layers['psychoeducation']['text']}\n")
        
        # Stepwise options
        while True:
            print("="*60)
            print("Explore further:")
            print("  [1] Get technique")
            print("  [2] See reframing")
            print("  [3] Get journaling prompt")
            print("  [4] Done")
            
            choice = input("\nChoice (1/2/3/4): ").strip()
            
            if choice == "4" or not choice:
                break
            
            if choice == "1" and 'technique' in all_layers:
                print(f"\n🛠️  TECHNIQUE:\n{all_layers['technique']['text']}\n")
            
            elif choice == "2" and 'reframing' in all_layers:
                print(f"\n🔄 REFRAME:\n{all_layers['reframing']['text']}\n")
            
            elif choice == "3" and 'journaling' in all_layers:
                print(f"\n📝 JOURNAL PROMPT:\n{all_layers['journaling']['text']}\n")

print("\n✨ Integrated system is working!")
