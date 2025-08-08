import json

def merge_gemini_outputs(old_json_path, new_json_path):
    # Load old JSON
    with open(old_json_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Load new JSON
    with open(new_json_path, "r", encoding="utf-8") as f:
        new_data = json.load(f)

    # Initialize merged output
    merged = {
        "nlu": {"intents": []},
        "domain": {"responses": {}},
        "stories": [],
        "rules": []
    }

    # === Merge NLU intents ===
    old_intents = old_data.get("nlu", {}).get("intents", [])
    new_intents = new_data.get("nlu", {}).get("intents", [])
    all_intents = old_intents + new_intents

    # Remove duplicates based on intent name
    seen = set()
    unique_intents = []
    for intent in all_intents:
        if intent["name"] not in seen:
            seen.add(intent["name"])
            unique_intents.append(intent)
    merged["nlu"]["intents"] = unique_intents

    # === Merge Domain Responses ===
    merged["domain"]["responses"] = {
        **old_data.get("domain", {}).get("responses", {}),
        **new_data.get("domain", {}).get("responses", {})
    }

    # === Merge Stories ===
    merged["stories"] = old_data.get("stories", []) + new_data.get("stories", [])

    # === Merge Rules ===
    merged["rules"] = old_data.get("rules", []) + new_data.get("rules", [])

    return merged


merged_data=merge_gemini_outputs(
    ".//old_new_output_marger//old_json//old_.json",
    ".//old_new_output_marger//new_json/merged_response.json"
)

# uncomment below to run directly



# with open(".//old_new_output_marger//old_json//old_.json", "w", encoding="utf-8") as f:
#     json.dump(merged_data, f, indent=2, ensure_ascii=False)

# print("Merged new_ into merged_response.json")
