import json

# Load your new layered advice
with open('therapeutic_advice.json', 'r', encoding='utf-8') as f:
    layered_advice = json.load(f)

flattened_entries = []

for entry in layered_advice:
    entry_id = entry['id']
    issue = entry.get('issue', 'unknown')
    sub_issue = entry.get('sub_issue', 'general')
    emotions = entry.get('emotions', [])
    cog_dist = entry.get('cognitive_distortion', None)
    layers = entry.get('response_layers', {})

    
    # 1. Validation layer
    flattened_entries.append({
        "id": f"{entry_id}_validation",
        "parent_id": entry_id,
        "layer_type": "validation",
        "issue": issue,
        "sub_issue": sub_issue,
        "emotions": emotions,
        "cognitive_distortion": cog_dist,
        "text": layers['validation']
    })
    
    # 2. Psychoeducation layer
    flattened_entries.append({
        "id": f"{entry_id}_psychoeducation",
        "parent_id": entry_id,
        "layer_type": "psychoeducation",
        "issue": issue,
        "sub_issue": sub_issue,
        "emotions": emotions,
        "cognitive_distortion": cog_dist,
        "text": layers['psychoeducation']
    })
    
    # 3. Primary technique layer
    technique = layers['primary_technique']
    technique_text = f"{technique['name']}: {technique['instruction']}"
    
    flattened_entries.append({
        "id": f"{entry_id}_technique",
        "parent_id": entry_id,
        "layer_type": "technique",
        "technique_type": technique['type'],
        "technique_name": technique['name'],
        "issue": issue,
        "sub_issue": sub_issue,
        "emotions": emotions,
        "cognitive_distortion": cog_dist,
        "text": technique_text
    })
    
    # 4. Reframing layer (from deeper_work)
    for item in layers.get('deeper_work', []):
        if item['type'] == 'reframing':
            reframe_text = f"Extreme thought: {item['extreme_thought']}\n\nReframe: {item['reframe']}"
            flattened_entries.append({
                "id": f"{entry_id}_reframing",
                "parent_id": entry_id,
                "layer_type": "reframing",
                "issue": issue,
                "sub_issue": sub_issue,
                "emotions": emotions,
                "cognitive_distortion": cog_dist,
                "text": reframe_text
            })
    
    # 5. Journaling prompt layer (from deeper_work)
    for item in layers.get('deeper_work', []):
        if item['type'] == 'journaling_prompt':
            flattened_entries.append({
                "id": f"{entry_id}_journaling",
                "parent_id": entry_id,
                "layer_type": "journaling",
                "issue": issue,
                "sub_issue": sub_issue,
                "emotions": emotions,
                "cognitive_distortion": cog_dist,
                "text": item['prompt']
            })

print(f"✅ Flattened {len(layered_advice)} entries into {len(flattened_entries)} layer records")

# Save flattened entries
with open('processed_data/flattened_layered_advice.json', 'w', encoding='utf-8') as f:
    json.dump(flattened_entries, f, indent=2, ensure_ascii=False)

print("✅ Saved to processed_data/flattened_layered_advice.json")
