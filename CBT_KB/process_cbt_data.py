from datasets import load_dataset
import json
import os

print("Processing CBT-Bench data...\n")

# Create folders for organized storage
os.makedirs("raw_data", exist_ok=True)
os.makedirs("processed_data", exist_ok=True)

# Subsets to process
subsets = [
    "distortions_seed",
    "distortions_test", 
    "core_major_seed",
    "core_major_test",
    "core_fine_seed",
    "core_fine_test"
]

all_documents = []
stats = {}

for subset in subsets:
    print(f" Processing {subset}...")
    
    try:
        # Load dataset
        ds = load_dataset("Psychotherapy-LLM/CBT-Bench", subset)
        split = list(ds.keys())[0]  # Get first split
        data = ds[split]
        
        documents = []
        
        # Process each example
        for idx, example in enumerate(data):
            # Create a structured document
            doc = {
                "id": f"{subset}_{idx}",
                "source": subset,
                "situation": example.get("situation", ""),
                "thoughts": example.get("thoughts", ""),
                "original_text": example.get("ori_text", ""),
            }
            
            # Add classification label (different names in different subsets)
            if "core_belief_fine_grained" in example:
                doc["classification"] = example["core_belief_fine_grained"]
                doc["type"] = "core_belief_fine"
            elif "core_belief_major" in example:
                doc["classification"] = example["core_belief_major"]
                doc["type"] = "core_belief_major"
            elif "distortion" in example:
                doc["classification"] = example["distortion"]
                doc["type"] = "cognitive_distortion"
            
            # Create searchable text (combine all text fields)
            searchable_text = f"""
Situation: {doc['situation']}

Thoughts: {doc['thoughts']}

Classification: {doc.get('classification', 'N/A')}

Type: {doc.get('type', 'N/A')}
""".strip()
            
            doc["text"] = searchable_text
            documents.append(doc)
        
        # Save to JSON
        output_file = f"processed_data/{subset}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        all_documents.extend(documents)
        stats[subset] = len(documents)
        
        print(f"   ✅ Processed {len(documents)} examples → {output_file}\n")
        
    except Exception as e:
        print(f"   ❌ Error processing {subset}: {e}\n")

# Save all combined data
combined_file = "processed_data/all_cbt_data.json"
with open(combined_file, 'w', encoding='utf-8') as f:
    json.dump(all_documents, f, indent=2, ensure_ascii=False)

print("\n" + "="*60)
print(" PROCESSING SUMMARY")
print("="*60)

for subset, count in stats.items():
    print(f"✓ {subset}: {count} documents")

print(f"\n Total documents created: {len(all_documents)}")
print(f" All data saved to: {combined_file}")
print("="*60)

# Show a sample document
if all_documents:
    print("\n Sample Document Preview:")
    print("-" * 60)
    sample = all_documents[0]
    print(f"ID: {sample['id']}")
    print(f"Type: {sample.get('type', 'N/A')}")
    print(f"Text preview:\n{sample['text'][:200]}...")
    print("-" * 60)

print("\n✅ Processing complete!")