import json

# Load the therapeutic advice
with open('therapeutic_advice.json', 'r', encoding='utf-8') as f:
    therapeutic_advice = json.load(f)

# Load the existing all_cbt_data
with open('processed_data/all_cbt_data.json', 'r', encoding='utf-8') as f:
    all_cbt_data = json.load(f)

# Check how many entries we currently have
print(f"Current entries in all_cbt_data: {len(all_cbt_data)}")
print(f"Therapeutic advice entries to add: {len(therapeutic_advice)}")

# Append the therapeutic advice
all_cbt_data.extend(therapeutic_advice)

print(f"Total entries after merge: {len(all_cbt_data)}")

# Save the updated file
with open('processed_data/all_cbt_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_cbt_data, f, indent=2, ensure_ascii=False)

print("✅ Successfully appended therapeutic advice!")
