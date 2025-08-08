import os
import requests
import json
import time
from dotenv import load_dotenv

# This is a helper function to extract text sections from the LLM response
def extract_section(text, section_name):
    try:
        start_tag = f"### START {section_name} ###"
        end_tag = f"### END {section_name} ###"
        start_index = text.index(start_tag) + len(start_tag)
        end_index = text.index(end_tag)
        return text[start_index:end_index].strip()
    except (ValueError, IndexError):
        return None

def sending_chunks_to_gemini(chunks):
    print("STEP 4: Sending chunks to Gemini LLM for processing...")

    load_dotenv()
    GEMINI_API_KEY = os.getenv("Gemini_API_KEY")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    output_dir = "nlu_rule_stories_domain_generator/yamlfiles"
    os.makedirs(output_dir, exist_ok=True)
    print(f"-> Output will be saved in the '{output_dir}' directory.")

    MAX_RETRIES = 5
    INITIAL_BACKOFF = 3

    for i, chunk in enumerate(chunks):
        originalChunk = chunk.get("chunk")
        prompt = """You are a chatbot training data generator for Rasa. Your task is to analyze the given document and do the following:

1. Think about what user **intents** could be handled based on this document.
2. Name each intent clearly (e.g., ask_history, ask_location).
3. For each intent, generate **3 to 5 different user expressions** (different ways to say the same intent).
4. For each intent, generate **one unique response** that the bot could say, based only on the information in the document.
5. Then generate a **story** in this JSON format:
   {
     "story": "story name",
     "steps": [
       {"intent": "intent_name"},
       {"action": "utter_intent_name"}
     ]
   }

6. Also generate a **rule** for each intent that has a simple one-turn response in this JSON format:
   {
     "rule": "rule name",
     "steps": [
       {"intent": "intent_name"},
       {"action": "utter_intent_name"}
     ]
   }

⚠️ Requirements:

- DO NOT ADD ```json at the beginning and ``` at the end.
- Every intent must be unique.
- Every intent must have a corresponding response, story, and rule.
- Every response must be named `utter_<intent_name>`.
- The entire output must be returned in valid JSON with the following structure:
- DO NOT ADD ```json at the beginning and ``` at the end.

{
  "nlu": {
    "intents": [
      {
        "name": "intent_name",
        "examples": [
          "example 1",
          "example 2"
        ]
      }
    ]
  },
  "domain": {
    "responses": {
      "utter_intent_name": [
        {"text": "Bot response based on the document"}
      ]
    }
  },
  "stories": [
    {
      "story": "story name",
      "steps": [
        {"intent": "intent_name"},
        {"action": "utter_intent_name"}
      ]
    }
  ],
  "rules": [
    {
      "rule": "rule name",
      "steps": [
        {"intent": "intent_name"},
        {"action": "utter_intent_name"}
      ]
    }
  ]
}

DOCUMENT:

"""
        prompt += originalChunk

        body = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        print(f"\n--- Processing Chunk {i+1}/{len(chunks)} ---")
        llm_response = None

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(body), timeout=300)
                print(f"Attempt {attempt + 1}: Received status code {response.status_code}")

                if response.status_code == 200:
                    output = response.json()
                    if "candidates" in output and output["candidates"]:
                        llm_response = output["candidates"][0]["content"]["parts"][0]["text"]
                        print("-> Successfully received response from LLM.")
                        break
                    else:
                        print("-> Error: Response OK but malformed. No 'candidates' found.")
                        print("   API Response:", output)
                        break

                elif response.status_code in (429, 500, 502, 503, 504):
                    print(f"-> Temporary error ({response.status_code}). Waiting to retry... {response.text}")
                    if attempt == MAX_RETRIES - 1:
                        print("-> All retries failed for this chunk. Giving up.")
                        break
                    wait_time = INITIAL_BACKOFF * (2 ** attempt)
                    print(f"   ...waiting for {wait_time} seconds.")
                    time.sleep(wait_time)

                else:
                    print(f"-> Critical error received ({response.status_code}). Not retrying.")
                    print("   Error Response:", response.text)
                    break

            except requests.exceptions.RequestException as e:
                print(f"-> A network-level error occurred: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(5)

        if llm_response:
            raw_output_filename = os.path.join(output_dir, f"raw_output_chunk_{i}.json")
            with open(raw_output_filename, 'w', encoding='utf-8') as f:
                f.write(llm_response)

            output_path = f"./old_new_output_marger/output_from_gemeini_json/chunk{i+1}_.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(llm_response)

            print(f"-> Successfully parsed and saved files for chunk {i+1}.")
        else:
            print(f"-> SKIPPING chunk {i+1} due to persistent API errors.")
