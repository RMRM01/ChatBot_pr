import yaml
import glob
import re
import os

def merge_rasa_yaml_files(path_to_old_yaml_parts, prefix, path_to_new_yaml_parts):
    # Match files like nlu1.yml, nlu2.yml, domain1.yml etc.
    yaml= "yaml"
    pattern_old_file = os.path.join(path_to_old_yaml_parts, f"{prefix}*.yml")
    pattern_new_file = os.path.join(path_to_new_yaml_parts, f"{yaml}*.yml")

    files_old = sorted(
        glob.glob(pattern_old_file),
        key=lambda x: int(re.search(r'\d+', os.path.basename(x)).group())
    )
    files_new = sorted(
        glob.glob(pattern_new_file),
        key=lambda x: int(re.search(r'\d+', os.path.basename(x)).group())
    )
    del files_old[0]
    print(len(files_old))
    print(len(files_new))

    #variable --------
    data = ""

    old=""
    new=""

    for file_old, file_new in zip(files_old, files_new):
        with open(file_old, 'r', encoding='utf-8') as f:
            old= f.read()
        with open(file_new, 'r', encoding='utf-8') as f:
            new= f.read()

        data = old+'\n'+new

        with open(file_old, 'w', encoding='utf-8') as f:
            f.write(data.strip('\n'))
        with open(file_old, 'r', encoding='utf-8') as f:
            n=f.read()
        with open(file_old, 'w', encoding='utf-8') as f:
            f.write(n.strip('\n'))       
        # print(data)


merge_rasa_yaml_files(".\\nlu_rule_stories_domain_generator\\old_divided_parts_of_YAML\\nlu_parts", "nlu", ".\\nlu_rule_stories_domain_generator\\new_divided_parts_of_YAML\\nlu_parts")

merge_rasa_yaml_files(".\\nlu_rule_stories_domain_generator\\old_divided_parts_of_YAML\\domain_parts", "domain", ".\\nlu_rule_stories_domain_generator\\new_divided_parts_of_YAML\\domain_parts")

merge_rasa_yaml_files(".\\nlu_rule_stories_domain_generator\\old_divided_parts_of_YAML\\rules_parts", "rules", ".\\nlu_rule_stories_domain_generator\\new_divided_parts_of_YAML\\rules_parts")

merge_rasa_yaml_files(".\\nlu_rule_stories_domain_generator\\old_divided_parts_of_YAML\\stories_parts", "stories", ".\\nlu_rule_stories_domain_generator\\new_divided_parts_of_YAML\\stories_parts")
