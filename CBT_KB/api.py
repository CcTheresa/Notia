from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

app = FastAPI(title="Notia Therapeutic Advice API")

# CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# LOAD MODELS AT STARTUP

EMOTION_LABELS = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
    'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
    'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
    'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
    'relief', 'remorse', 'sadness', 'surprise', 'neutral'
]

print("🔧 Loading models...")

emotion_classifier = pipeline(
    "text-classification",
    model="../model",
    top_k=None
)
print("✅ Emotion classifier loaded")

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('embeddings/layered_advice_faiss.index')

with open('embeddings/layered_advice_metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print("✅ Embedding model + FAISS loaded")
print(f"✅ {len(metadata)} advice layers ready\n")


# REQUEST/RESPONSE MODELS

class JournalEntry(BaseModel):
    text: str


# CORE FUNCTIONS

def extract_emotions(text, threshold=0.5):
    """Extract emotions using DistilBERT safely with explicit type handling"""
    result = emotion_classifier(text)
    # `result` can be a list of dict or list of lists of dicts depending on pipeline
    emotions = result[0] if isinstance(result[0], list) else result

    detected = []
    for emo in emotions:
        # Ensure emo is dictionary-like and has keys 'label' and 'score'
        if not isinstance(emo, dict):
            continue

        label = emo.get('label', '')
        score = emo.get('score', 0)

        # Convert types explicitly
        if isinstance(label, str) and isinstance(score, (float, int)):
            if label.startswith('LABEL_') and float(score) > threshold:
                idx = int(label.split('_')[1])
                detected.append({
                    'emotion': EMOTION_LABELS[idx],
                    'confidence': float(score)
                })

    detected.sort(key=lambda x: x['confidence'], reverse=True)
    return detected


def search_with_emotions(journal_entry, layer_type=None, top_k=3):
    """Two-stage retrieval: emotion detection + semantic search + boosting"""
    # Stage 1: Detect emotions
    detected_emotions = extract_emotions(journal_entry, threshold=0.5)
    detected_names = [e['emotion'] for e in detected_emotions]
    
    # Stage 2: Semantic search
    query_emb = embedding_model.encode([journal_entry])[0]
    search_k = min(top_k * 10, len(metadata))
    distances, indices = index.search(np.array([query_emb]).astype('float32'), search_k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        base_score = 1 / (1 + dist)
        entry = metadata[idx]
        
        if layer_type and entry['layer_type'] != layer_type:
            continue
        
        # Emotion overlap boosting
        entry_emotions = set(entry.get('emotions', []))
        pred_emotions = set(detected_names)
        overlap = entry_emotions.intersection(pred_emotions)
        
        emotion_boost = len(overlap) * 0.15
        final_score = base_score + emotion_boost
        
        results.append({
            'score': float(final_score),
            'parent_id': entry['parent_id'],
            'issue': entry['issue'],
            'sub_issue': entry['sub_issue'],
            'emotions': list(entry.get('emotions', [])),
            'emotion_overlap': list(overlap),
            'layer_type': entry['layer_type'],
            'text': entry['text']
        })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k], detected_emotions


def get_all_layers(parent_id):
    """Retrieve all advice layers for a matched entry"""
    layers = {}
    
    for layer_type in ['validation', 'psychoeducation', 'technique', 'reframing', 'journaling']:
        match = next((m for m in metadata if m['parent_id'] == parent_id and m['layer_type'] == layer_type), None)
        if match:
            layers[layer_type] = {
                'text': match['text'],
                'emotions': match.get('emotions', [])
            }
    
    return layers

# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "service": "Notia Therapeutic Advice API",
        "status": "running",
        "version": "1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_loaded": True,
        "advice_entries": len(set(m['parent_id'] for m in metadata)),
        "total_layers": len(metadata)
    }


@app.post("/get-advice")
def get_advice(entry: JournalEntry):
    """
    Main endpoint: Process journal entry and return layered therapeutic advice
    
    Args:
        entry: JournalEntry with 'text' field
    
    Returns:
        - detected_emotions: List of emotions with confidence scores
        - matched_issue: The cognitive distortion or issue identified
        - confidence: Match confidence score (0-1+)
        - advice_layers: All 5 layers (validation, psychoeducation, technique, reframing, journaling)
    """
    if not entry.text or len(entry.text.strip()) < 10:
        return {
            "error": "Journal entry too short. Please write at least 10 characters."
        }
    
    # Search for best match
    matches, emotions = search_with_emotions(entry.text, layer_type='validation', top_k=1)
    
    if not matches:
        return {
            "error": "No advice found. Please try rephrasing your entry."
        }
    
    match = matches[0]
    parent_id = match['parent_id']
    
    # Get all layers
    all_layers = get_all_layers(parent_id)
    
    return {
        "detected_emotions": emotions[:5],  # Top 5 emotions
        "matched_issue": match['issue'],
        "matched_sub_issue": match['sub_issue'],
        "confidence": match['score'],
        "emotion_overlap": match['emotion_overlap'],
        "advice_layers": all_layers
    }


@app.post("/detect-emotions")
def detect_emotions(entry: JournalEntry):
    """
    Utility endpoint: Only detect emotions (no advice retrieval)
    """
    emotions = extract_emotions(entry.text, threshold=0.3)
    
    return {
        "text": entry.text,
        "detected_emotions": emotions[:10]
    }


# ============================================================
# STARTUP EVENT
# ============================================================

@app.on_event("startup")
def startup_event():
    print("="*60)
    print(" Notia API is ready")
    print("="*60)
