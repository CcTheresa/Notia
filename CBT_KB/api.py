from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

#domain matching for better retrieval
# At the top, after imports
DOMAIN_KEYWORDS = {
    "academic": {
        "exam", "test", "assignment", "grade", "grades", "school", "university",
        "class", "lecture", "midterm", "final", "study", "studying", "homework"
    },
    "relationships": {
        "boyfriend", "girlfriend", "partner", "relationship", "friend", "friends",
        "family", "mom", "dad", "sister", "brother", "husband", "wife", "cheated",
        "cheat", "affair", "broke up", "breakup"
    },
    "work": {
        "job", "work", "manager", "boss", "deadline", "office", "coworker",
        "colleague", "promotion", "fired"
    },
    "gratitude_positive": {
        "grateful", "gratitude", "thankful", "appreciate", "blessed",
        "happy for", "proud of", "excited about"
    },
}

def detect_domains(text: str) -> set[str]:
    text_lower = text.lower()
    domains: set[str] = set()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            domains.add(domain)
    return domains

#mapping issues to domains for more contextual retrieval
# ---- existing: DOMAIN_KEYWORDS + detect_domains here ----

ISSUE_TO_DOMAIN = {
    "emotional_regulation": "emotional_regulation",
    "emotional_validation": "emotional_validation",
    "worthlessness": "worth/self_worth",
    "self_doubt": "self_doubt",
    "all_or_nothing_thinking": "all_or_nothing",
    "anxiety": "anxiety",
    "shame": "shame",
    "self_sabotage": "self_sabotage",
    "unhealthy_coping_mechanisms": "coping",
    # extend later if you add issues like gratitude / savoring
}

SUB_ISSUE_TO_DOMAIN = {
    # emotional_regulation
    "acceptance_vs_suppression": "emotional_regulation",
    "cognitive_defusion": "emotional_regulation",
    "values_driven_action": "emotional_regulation",
    "self_as_context": "emotional_regulation",
    "uncomfortable_vs_wrong": "emotional_regulation",
    "emotional_intensity_overwhelm": "emotional_regulation",
    "difficulty_sitting_with_discomfort": "emotional_regulation",
    "reactive_emotional_responses": "emotional_regulation",
    "emotional_numbness_shutdown": "emotional_regulation",
    "confusion_about_what_you_feel": "emotional_regulation",

    # worthlessness
    "intrinsic_value_recognition": "worth/self_worth",
    "challenging_negative_self_talk": "worth/self_worth",
    "worthlessness_driven_self_sabotage": "worth/self_worth",

    # anxiety
    "fear_vs_intuition": "anxiety",
    "worry_as_avoidance": "anxiety",
    "physical_symptoms_management": "anxiety",
    "cognitive_distortions_in_anxiety": "anxiety",
    "resistance_during_positive_change": "anxiety",

    # all_or_nothing_thinking
    "perfectionism_trap": "all_or_nothing",
    "discounting_partial_success": "all_or_nothing",
    "fear_of_starting": "all_or_nothing",
    "relationship_extremes": "relationships",
    "goal_abandonment_after_setbacks": "all_or_nothing",

    # shame
    "shame_vs_guilt_distinction": "shame",
    "childhood_origins_of_shame": "shame",
    "shame_spirals_and_rumination": "shame",
    "self_compassion_as_antidote": "shame",
    "shame_and_vulnerability": "shame",

    # self_doubt
    "confidence_through_action": "self_doubt",
    "challenging_inner_critic": "self_doubt",
    "understanding_origins": "self_doubt",
    "building_evidence_of_capability": "self_doubt",
    "embracing_imperfection": "self_doubt",

    # self_sabotage
    "upper_limit_problem": "self_sabotage",
    "procrastination_as_protection": "self_sabotage",
    "fear_of_outgrowing_old_identity": "self_sabotage",
    "fear_of_visibility_and_responsibility": "self_sabotage",
    "fear_of_disappointing_others": "self_sabotage",

    # unhealthy_coping_mechanisms
    "numbing_and_avoidance": "coping",
    "self_destructive_patterns": "coping",
    "overworking_and_productivity_addiction": "coping",
    "people_pleasing_and_self_abandonment": "coping",
    "emotional_eating_or_restriction": "eating_body",

    # emotional_validation
    "self_invalidation": "emotional_validation",
    "minimizing_your_pain": "emotional_validation",
    "fear_of_being_too_much": "emotional_validation",
    "needing_permission_to_feel": "emotional_validation",
}

from typing import Dict, List, Set, Any

def score_candidate(
    entry_dict: Dict[str, Any],
    base_score: float,
    emotion_labels: List[str],
    domains: Set[str],
) -> float:
    """Adjust FAISS base score using emotion overlap + domain match."""
    score = base_score

    # Emotion overlap
    entry_emotions = set(entry_dict.get("emotions") or [])
    overlap = entry_emotions.intersection(set(emotion_labels))
    score += 0.05 * len(overlap)

    # Domain from issue/sub_issue (ensure strings)
    issue = entry_dict.get("issue") or ""
    sub_issue = entry_dict.get("sub_issue") or ""

    advice_domain = SUB_ISSUE_TO_DOMAIN.get(sub_issue) or ISSUE_TO_DOMAIN.get(issue)

    # Domain match bonus
    if advice_domain and advice_domain in domains:
        score += 0.4

    # Positive context: avoid pathologizing gratitude
    if "gratitude_positive" in domains:
        if advice_domain in {"shame", "self_sabotage", "self_doubt", "worth/self_worth"}:
            score -= 0.3

    return float(score)


def build_low_confidence_response(detected_emotions: list[dict], best_score: float):
    top_emotions = [e["emotion"] for e in detected_emotions[:3]]
    return {
        "detected_emotions": detected_emotions[:5],
        "matched_issue": None,
        "matched_sub_issue": None,
        "confidence": float(best_score),
        "emotion_overlap": top_emotions,
        "advice_layers": {
            "validation": {
                "text": (
                    "I'm not fully confident I understand your exact situation from my knowledge base, "
                    "but I can still offer some gentle, general reflections. "
                    "It might help to write a bit more about what's going on or what you need right now."
                ),
                "emotions": top_emotions,
            },
            "journaling": {
                "text": (
                    "What feels most important about what you're going through right now? "
                    "What do you most want help with—understanding your feelings, making a decision, "
                    "or finding a small next step?"
                ),
                "emotions": top_emotions,
            },
        },
    }

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

def semantic_search(
    query: str,
    layer_type: str | None = None,
    top_k: int = 3,
    threshold: float = 0.0,
):
    """
    Pure semantic search, same as CLI search_layers.
    Used as the base retrieval before emotion/domain tweaks.
    """
    query_emb = embedding_model.encode([query])[0]
    search_k = min(top_k * 10, len(metadata))
    distances, indices = index.search(
        np.array([query_emb]).astype("float32"), search_k
    )

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        score = 1 / (1 + dist)

        if score < threshold:
            continue

        entry = metadata[idx]

        if layer_type and entry["layer_type"] != layer_type:
            continue

        results.append(
            {
                "score": float(score),
                "parent_id": entry["parent_id"],
                "issue": entry["issue"],
                "sub_issue": entry["sub_issue"],
                "emotions": list(entry.get("emotions", [])),
                "layer_type": entry["layer_type"],
                "text": entry["text"],
            }
        )

        if len(results) >= top_k:
            break

    return results



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
    """
    Two-stage retrieval:
    1) Run pure semantic search (same as CLI).
    2) Detect emotions.
    3) Optionally re-score with emotion overlap + domains.
    """
    # Stage 1: base semantic search
    base_results = semantic_search(
        journal_entry,
        layer_type=layer_type,
        top_k=top_k,
        threshold=0.0,
    )

    # Stage 2: detect emotions
    detected_emotions = extract_emotions(journal_entry, threshold=0.5)
    detected_names = [e["emotion"] for e in detected_emotions]

    # Stage 2b: detect domains
    domains = detect_domains(journal_entry)
    print(f"Detected domains: {domains}")

    # If no extra signals, just return base results
    if not base_results:
        return [], detected_emotions

    # Re-score base_results with our score_candidate helper
    rescored = []
    for r in base_results:
        base_score = r["score"]
        final_score = score_candidate(r, base_score, detected_names, domains)
        r["score"] = float(final_score)
        # recompute overlap field
        overlap = set(r.get("emotions", [])) & set(detected_names)
        r["emotion_overlap"] = list(overlap)
        rescored.append(r)

    rescored.sort(key=lambda x: x["score"], reverse=True)
    return rescored[:top_k], detected_emotions



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

MIN_ACCEPTABLE_SCORE = 0.35  # tune if needed
@app.post("/get-advice")
def get_advice(entry: JournalEntry):
    if not entry.text or len(entry.text.strip()) < 10:
        return {"error": "Journal entry too short. Please write at least 10 characters."}

    # 1) run pure semantic search, like CLI
    matches = semantic_search(entry.text, layer_type="validation", top_k=1, threshold=0.0)

    # 2) run emotions only for display (not used for retrieval)
    emotions = extract_emotions(entry.text, threshold=0.5)

    if not matches:
        return build_low_confidence_response(emotions, best_score=0.0)

    match = matches[0]
    parent_id = match["parent_id"]

    all_layers = get_all_layers(parent_id)

    return {
        "detected_emotions": emotions[:5],
        "matched_issue": match["issue"],
        "matched_sub_issue": match["sub_issue"],
        "confidence": match["score"],
        "emotion_overlap": [],  # you can compute if you want
        "advice_layers": all_layers,
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
