from transformers import pipeline

# Path to  model 
MODEL_PATH = "../model"

# GoEmotions label names (28 emotions)
EMOTION_LABELS = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
    'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
    'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
    'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
    'relief', 'remorse', 'sadness', 'surprise', 'neutral'
]

print("🧠 Loading emotion classifier...")
classifier = pipeline(
    "text-classification",
    model=MODEL_PATH,
    top_k=None,
)
print("✅ Model loaded\n")

# Test entries
test_entries = [
    "I keep putting off work because I'm afraid I'll fail",
    "My friend didn't text back and I think they hate me",
    "I feel worthless no matter what I achieve",
    "I can't stop worrying about everything"
]

print("="*60)
print("TESTING EMOTION PREDICTIONS")
print("="*60)

for entry in test_entries:
    print(f"\n📝 Entry: {entry}")
    
    result = classifier(entry)

    print(f"Detected emotions:")
    
    
    # Handle output format
    if isinstance(result, list) and len(result) > 0:
        emotions = result[0] if isinstance(result[0], list) else result
        
        # Map LABEL_X to actual emotion names
        emotion_scores = []
        for emo in emotions:
            label = emo['label']
            score = emo['score']
            
            # Extract index from LABEL_X
            if label.startswith('LABEL_'):
                idx = int(label.split('_')[1])
                emotion_name = EMOTION_LABELS[idx]
                
                # Only show emotions above threshold
                if score > 0.5:
                    emotion_scores.append({'emotion': emotion_name, 'score': score})
        
        # Sort by score and show top 3
        emotion_scores.sort(key=lambda x: x['score'], reverse=True)
        
        for emo in emotion_scores[:3]:
            print(f"   - {emo['emotion']}: {emo['score']:.3f}")
    
    print("-"*60)

print("\n" + "="*60)
print("✅ AUTOMATED TESTS COMPLETE!")
print("="*60)

# Interactive test
print("\n💬 Try your own journal entry (or press Enter to skip):")
user_entry = input("Your entry: ").strip()

if user_entry:
    print(f"\n🔍 Analyzing: \"{user_entry}\"\n")
    
    result = classifier(user_entry)
    
    print(f"Detected emotions:")
    
    if isinstance(result, list) and len(result) > 0:
        emotions = result[0] if isinstance(result[0], list) else result
        
        emotion_scores = []
        for emo in emotions:
            label = emo['label']
            score = emo['score']
            
            if label.startswith('LABEL_'):
                idx = int(label.split('_')[1])
                emotion_name = EMOTION_LABELS[idx]
                
                if score > 0.5:
                    emotion_scores.append({'emotion': emotion_name, 'score': score})
        
        emotion_scores.sort(key=lambda x: x['score'], reverse=True)
        
        for emo in emotion_scores[:3]:
            print(f"   - {emo['emotion']}: {emo['score']:.3f}")

print("\n Emotion classifier is working!")