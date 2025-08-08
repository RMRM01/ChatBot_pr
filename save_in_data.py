import shutil

def save_to_rasa(source_path, destination_path):
    try:
        shutil.copy2(source_path, destination_path)
        print(f"File copied from '{source_path}' to '{destination_path}'")
    except Exception as e:
        print(f"Error: {e}")

def move():
    save_to_rasa("./data_test/nlu.yml", "data/nlu.yml")
    save_to_rasa("./data_test/stories.yml", "data/stories.yml")
    save_to_rasa("./data_test/rules.yml", "data/rules.yml")
    save_to_rasa("./data_test/domain.yml", "domain.yml")

# uncomment to perform the task

# save_to_rasa("./data_test/nlu.yml", "data/nlu.yml")
# save_to_rasa("./data_test/stories.yml", "data/stories.yml")
# save_to_rasa("./data_test/rules.yml", "data/rules.yml")
# save_to_rasa("./data_test/domain.yml", "domain.yml")