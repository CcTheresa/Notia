from datasets import load_dataset

print("Downloading CBT-Bench dataset...\n")

subsets = {
    "distortions_seed": "Cognitive Distortions (Training)",
    "distortions_test": "Cognitive Distortions (Test)",
    "core_major_seed": "Primary Core Beliefs (Training)",
    "core_major_test": "Primary Core Beliefs (Test)",
    "core_fine_seed": "Fine-Grained Core Beliefs (Training)",
    "core_fine_test": "Fine-Grained Core Beliefs (Test)",
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
        
        # Safely get split keys
        split_keys = [str(s) for s in ds.keys()] if hasattr(ds, 'keys') else [] # type: ignore
        # Count total examples across splits
        total = 0
        for split in split_keys:
            subset = ds[split]
            if hasattr(subset, '__len__'):

                try:
                    total += len(subset) # type: ignore
                except TypeError:
                    continue
                pass  # Skip if size info is unavailable
        print(f"   Downloaded: {total} examples")
        print(f"   Splits: {split_keys}\n")
        
    except Exception as e:
        print(f"   Skipped '{subset_key}': {e}\n")

print("\n" + "="*60)
print(" DOWNLOAD SUMMARY")
print("="*60)

total_examples = 0
for subset_name, dataset in downloaded_data.items():
    split_keys = [str(s) for s in dataset.keys()] if hasattr(dataset, 'keys') else []
    if not split_keys:
        continue
    split = split_keys[0]
    count = 0
    if hasattr(dataset[split], '__len__'):
        try:
            count = len(dataset[split])
        except TypeError:
            pass
    print(f"\n✓ {subset_name}: {count} examples")
    print(f"  Columns: {dataset[split].column_names}")
    if count > 0:
        example = dataset[split][0]
        print(f"  Sample keys: {list(example.keys())}")

print(f"\n{'='*60}")
print(f"🎉 Total examples downloaded: {total_examples}")
print(f"✅ Successfully downloaded {len(downloaded_data)} subsets!")
print("="*60)
