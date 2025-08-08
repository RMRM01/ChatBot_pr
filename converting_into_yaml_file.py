import json
import yaml
import os

# === Your Gemini Output JSON ===


#saving output in file... 


def save_yaml(filename, data):
    with open(f"output_yaml/{filename}.yml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)



# === Parse Gemini JSON Output ===

def generate_final_rasa_yamls(gemini_output):
    parsed = gemini_output

    # === Custom dumper to format multiline examples as block-style (|)
    class BlockStyleDumper(yaml.SafeDumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(BlockStyleDumper, self).increase_indent(flow, False)

        def represent_scalar(self, tag, value, style=None):
            if tag == 'tag:yaml.org,2002:str' and '\n' in value:
                style = '|'
            return super().represent_scalar(tag, value, style)


    def write_yaml(filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True, Dumper=BlockStyleDumper)
    



    # === Build and Write NLU YAML ===
    if "nlu" in parsed:
        formatted_nlu = {
            "version": "3.1",
            "nlu": []
        }
        for intent in parsed["nlu"]["intents"]:
            example_block = "\n".join([f"- {ex}" for ex in intent["examples"]])
            formatted_nlu["nlu"].append({
                "intent": intent["name"],
                "examples": example_block
            })

        write_yaml(".//data_test//nlu.yml", formatted_nlu)

    # === Build and Write Domain YAML ===
    if "domain" in parsed:
        responses = parsed["domain"].get("responses", {})
        domain_intents = []
        for key in responses:
            if key.startswith("utter_"):
                domain_intents.append(key.replace("utter_", ""))

        domain_yaml = {
            "version": "3.1",
            "intents": domain_intents,
            "responses": responses
        }
        write_yaml(".//data_test//domain.yml", domain_yaml)

    # ===  Build and Write Stories YAML ===
    if "stories" in parsed:
        stories_yaml = {
            "version": "3.1",
            "stories": parsed["stories"]
        }
        write_yaml(".//data_test//stories.yml", stories_yaml)

    # === Build and Write Rules YAML ===
    if "rules" in parsed:
        rules_yaml = {
            "version": "3.1",
            "rules": parsed["rules"]
        }
        write_yaml(".//data_test//rules.yml", rules_yaml)

    print("Final Rasa YAML files generated: nlu.yml, domain.yml, stories.yml, rules.yml")

#uncomment to run directly


# with open(".//old_new_output_marger//old_json//old_.json", "r", encoding="utf-8") as f:
#   old_json_file_data = json.load(f)
#   generate_final_rasa_yamls(old_json_file_data) 