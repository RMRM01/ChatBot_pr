import os
import json

def merge_chunked_json_responses(
    folder_path=".//old_new_output_marger//output_from_gemeini_json",
    output_path=".//old_new_output_marger//new_json//merged_response.json"
):
    merged = {
        "nlu": {"intents": []},
        "domain": {"responses": {}},
        "stories": [],
        "rules": []
    }

    # Loop over all chunk_X.json files
    for filename in sorted(os.listdir(folder_path)):
        if filename.startswith("chunk") and filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    chunk_data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON in {filename}: {e}")
                    continue

            # Handle NLU
            if "nlu" in chunk_data:
                if isinstance(chunk_data["nlu"], dict) and "intents" in chunk_data["nlu"]:
                    merged["nlu"]["intents"].extend(chunk_data["nlu"]["intents"])
                elif isinstance(chunk_data["nlu"], list):
                    merged["nlu"]["intents"].extend(chunk_data["nlu"])

            # Handle Domain Responses — Keep first occurrence only
            if "domain" in chunk_data:
                responses = chunk_data["domain"].get("responses", {})
                if isinstance(responses, dict):
                    for key, value in responses.items():
                        if key not in merged["domain"]["responses"]:
                            merged["domain"]["responses"][key] = value

            # Merge Stories
            if "stories" in chunk_data and isinstance(chunk_data["stories"], list):
                merged["stories"].extend(chunk_data["stories"])

            # Merge Rules
            if "rules" in chunk_data and isinstance(chunk_data["rules"], list):
                merged["rules"].extend(chunk_data["rules"])

    # Remove duplicate intents by name
    seen_intents = set()
    unique_intents = []
    for intent in merged["nlu"]["intents"]:
        if intent["name"] not in seen_intents:
            seen_intents.add(intent["name"])
            unique_intents.append(intent)
    merged["nlu"]["intents"] = unique_intents

    # Save merged output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f" Merged {len(seen_intents)} unique intents and {len(merged['domain']['responses'])} unique responses into {output_path}")

# Uncomment to run directly:
# merge_chunked_json_responses()
