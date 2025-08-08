import pypdf
import nltk
from sentence_transformers import SentenceTransformer
import numpy as np
import re
import os
# import upload_vector_Data_in_pinecone as upload_vector
from dotenv import load_dotenv
import sending_to_gemini as send_message_to_llm #ok
import yaml
import json_file_merge  #ok
import converting_into_yaml_file   as make_yaml #ok
import merge_old_new_json as mon  #ok
import json
import delete_all_chunk
import copy_all_uploads_folder as copy
import save_in_data


load_dotenv()  # Load environment variables from .env file



# --- Extract Text ---
def extract_text_from_pdf(pdf_path):
    print(f"Reading text from {pdf_path}...")
    pdf_reader = pypdf.PdfReader(pdf_path)
    full_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            # Clean up text a bit
            full_text += re.sub(r'\s*\n\s*', ' ', text).strip()
    print("-> Done. length "+str(len(full_text)))
    return full_text

# --- Split into Sentences (Corrected) ---
def split_text_into_sentences(text):
    print("Splitting text into sentences...")
    try:
        # This checks if the 'punkt' model exists.
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        # If it doesn't exist, we download it.
        print("-> 'punkt' model not found. Downloading...")
        nltk.download('punkt')
    
    sentences = nltk.sent_tokenize(text)
    print(f"-> Found {len(sentences)} sentences.")
    return sentences

# --- Function to load data into the database
# def load_in_database(vector_data_to_upload, index_name, dimension, metric='cosine'):

#     print("----- Uploading vectors to Pinecone...")
    
#     # Initialize Pinecone
#     pinecone_client = upload_vector.initialize_pinecone()
    
#     # Create or get the index
#     index = upload_vector.create_pinecone_index(pinecone_client, index_name, dimension)
    
#     # Upload vectors in batches
#     batch_size = 100  # You can adjust this based on your needs
#     upload_vector.upload_vectors(index, vector_data_to_upload, batch_size)


# --- Create Semantic Chunks ---
def create_semantic_chunks(sentences, model, similarity_threshold):
    print("STEP 3: Creating intelligent semantic chunks...")
    
    if not sentences:
        print("-> No sentences to chunk.")
        return []
    
    # Create vector embeddings for every sentence
    print("-> Converting sentences to vectors of meaning...")
    embeddings = model.encode(sentences, show_progress_bar=True)

    # load_in_database(vectors_to_upload, "fentence-dhaka-pdf", dimension)
    # This list will hold our final chunks
    chunks = []
    
    # Start with the first sentence as the beginning of our first chunk
    current_chunk_sentences = [sentences[0]]
    j=1
    print("-> Finding topic breaks based on sentence similarity...")
    for i in range(len(sentences) - 1):
        # Get the vector for the current sentence and the next one
        emb1 = embeddings[i]
        emb2 = embeddings[i+1]
        
        
        # Calculate how similar they are (cosine similarity)
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # If the sentences are similar enough, add the next one to our current chunk
        if similarity > similarity_threshold:
            current_chunk_sentences.append(sentences[i+1])
        # If they are not similar, the topic has changed!
        else:
            # Finalize the current chunk by joining its sentences together
            dictionary_of_chunk={}
            dictionary_of_chunk["index"]= j
            j=j+1
            dictionary_of_chunk["chunk"]= " ".join(current_chunk_sentences)
            chunks.append(dictionary_of_chunk)
            current_chunk_sentences = []  # Reset for the next chunk
            # Start a brand new chunk with the next sentence
            current_chunk_sentences = [sentences[i+1]]
            
    # the very last chunk!
    if current_chunk_sentences:
        dictionary_of_chunk={}
        dictionary_of_chunk["index"]= j
        dictionary_of_chunk["chunk"]= " ".join(current_chunk_sentences)
        chunks.append(dictionary_of_chunk)
    # Print how many chunks we created
    print(f"-> Successfully created {len(chunks)} chunks.")
    with open("final_chunks_ok.txt", "w",encoding="utf-8") as file:
        for i, chunk in enumerate(chunks):
            file.write(f"--- CHUNK {i+1} ---\n")
            file.write(str(chunk) + "\n")
    
    return chunks




#new my work



# ===================================================================
# --- THIS IS WHERE RUN EVERYTHING ---
# ===================================================================


def run_full_pipeline():
    # --- Configuration ---
    PDF_FILE = "./uploads/file.pdf"             # Path to your PDF file
    MODEL_NAME = 'all-MiniLM-L6-v2'     # free AI model
    # MODEL_NAME = 'BAAI/bge-large-en-v1.5'     # AI model we will use

    # This is "sensitivity" knob. Lower value = more chunks.
    SIMILARITY_THRESHOLD = 0.5   

    # 1. Get the raw text
    raw_text = extract_text_from_pdf(PDF_FILE)

    # 2. Split into sentences
    sentences = split_text_into_sentences(raw_text)

    # 3. Load the AI Model
    print("-> Loading the AI model (this may take a moment on first run)...")
    ai_model = SentenceTransformer(MODEL_NAME)

    # 4. Create the chunks
    final_chunks = create_semantic_chunks(sentences, ai_model, SIMILARITY_THRESHOLD)
    print('--------------------- *************************** final chunk done')

    #send Message to LLM
    send_message_to_llm.sending_chunks_to_gemini(final_chunks)

    # add all chunck 
    json_file_merge.merge_chunked_json_responses()

    # Deleting all chuncks 
    delete_all_chunk.deleteAll("./old_new_output_marger/output_from_gemeini_json/")

    # ==== merging old and new json file
    merged_data = mon.merge_gemini_outputs(
        ".//old_new_output_marger//old_json//old_.json",
        ".//old_new_output_marger//new_json/merged_response.json"
    )

    # Optionally, save it:
    with open(".//old_new_output_marger//old_json//old_.json", "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print("Merged new_ into merged_response.json")

    # convert into yaml file and save into data folder and domain folder
    with open(".//old_new_output_marger//old_json//old_.json", "r", encoding="utf-8") as f:
        old_json_file_data = json.load(f)
        make_yaml.generate_final_rasa_yamls(old_json_file_data)

    print("EVERYTHING IS DONE CURRECTLY CHECK DATA_TEST FOLDER< THANK YOU")

    # copyint uploaded document to a new folder 
    copy.copy_folder_contents("./uploads", "./learned_document")

    # cleaning uploads folder 
    delete_all_chunk.deleteAll("./uploads/")
    delete_all_chunk.deleteAll("./data/")
    # delete_all_chunk.deleteAll("./")

    save_in_data.move()


# # --- Configuration ---
# PDF_FILE = ".//uploads//file.pdf"             # Path to your PDF file
# MODEL_NAME = 'all-MiniLM-L6-v2'     # free AI model
# # MODEL_NAME = 'BAAI/bge-large-en-v1.5'     # AI model we will use

# # This is "sensitivity" knob. Lower value = more chunks.
# SIMILARITY_THRESHOLD = 0.5   

# # 1. Get the raw text
# raw_text = extract_text_from_pdf(PDF_FILE)

# # 2. Split into sentences
# sentences = split_text_into_sentences(raw_text)

# # 3. Load the AI Model
# print("-> Loading the AI model (this may take a moment on first run)...")
# ai_model = SentenceTransformer(MODEL_NAME)

# # 4. Create the chunks
# final_chunks = create_semantic_chunks(sentences, ai_model, SIMILARITY_THRESHOLD)
# print('--------------------- *************************** final chunk done')


# #send Message to LLM
# send_message_to_llm.sending_chunks_to_gemini(final_chunks)



# # add all chunck 

# json_file_merge.merge_chunked_json_responses()

# # Deleting all chuncks 

# delete_all_chunk.deleteAll("./old_new_output_marger/output_from_gemeini_json/")

# # ==== merging old and new json file

# merged_data = mon.merge_gemini_outputs(
#     ".//old_new_output_marger//old_json//old_.json",
#     ".//old_new_output_marger//new_json/merged_response.json"
# )

# # Optionally, save it:
# with open(".//old_new_output_marger//old_json//old_.json", "w", encoding="utf-8") as f:
#     json.dump(merged_data, f, indent=2, ensure_ascii=False)

# print("Merged new_ into merged_response.json")

# # convert into yaml file and save into data folder and domain folder

# with open(".//old_new_output_marger//old_json//old_.json", "r", encoding="utf-8") as f:
#   old_json_file_data = json.load(f)
#   make_yaml.generate_final_rasa_yamls(old_json_file_data)

# print("EVERYTHING IS DONE CURRECTLY CHECK DATA_TEST FOLDER< THANK YOU")

# # copyint uploaded document to a new folder 
# copy.copy_folder_contents("./uploads", "./learned_document")

# # cleaning uploads folder 
# delete_all_chunk.deleteAll("./uploads/")
# delete_all_chunk.deleteAll("./data/")
# # delete_all_chunk.deleteAll("./")

# save_in_data.move()