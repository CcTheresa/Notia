from datasets import load_dataset

print("Downloading CBT-Bench dataset...\n")

# Available subsets based on the dataset card
subsets = {
    # Level II - Cognitive Model Understanding
    "distortions_seed": "Cognitive Distortions (Training)",
    "distortions_test": "Cognitive Distortions (Test)",
    "core_major_seed": "Primary Core Beliefs (Training)",
    "core_major_test": "Primary Core Beliefs (Test)",
    "core_fine_seed": "Fine-Grained Core Beliefs (Training)",
    "core_fine_test": "Fine-Grained Core Beliefs (Test)",
    # Level III - extended versions
    "extended_fine_seed": "Extended Fine-Grained (Training)",
    "extended_fine_test": "Extended Fine-Grained (Test)",
    "extended_major_seed": "Extended Major (Training)",
    "extended_major_test": "Extended Major (Test)"
}

downloaded_data = {}

for subset_key, description in subsets.items():
    try:
        print(f" Downloading '{subset_key}' - {description}...")
        ds = load_dataset("Psychotherapy-LLM/CBT-Bench", subset_key)
        downloaded_data[subset_key] = ds
        
        # Count examples
        total = sum(len(ds[split]) for split in ds.keys())
        print(f"    Downloaded: {total} examples")
        print(f"   Splits: {list(ds.keys())}\n")
        
    except Exception as e:
        print(f"    Skipped '{subset_key}': {e}\n")

print("\n" + "="*60)
print(" DOWNLOAD SUMMARY")
print("="*60)

total_examples = 0
for subset_name, dataset in downloaded_data.items():
    split = list(dataset.keys())[0]  # Get first split
    count = len(dataset[split])
    total_examples += count
    
    print(f"\n✓ {subset_name}: {count} examples")
    print(f"  Columns: {dataset[split].column_names}")
    
    # Show one example
    if count > 0:
        example = dataset[split][0]
        print(f"  Sample keys: {list(example.keys())}")

print(f"\n{'='*60}")
print(f"🎉 Total examples downloaded: {total_examples}")
print(f"✅ Successfully downloaded {len(downloaded_data)} subsets!")
print("="*60)