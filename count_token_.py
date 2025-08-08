import os
import re


def count_tokens(file_location):
    with open(file_location, 'r') as file:
        content = file.read()
    tokens = content.split()
    return len(tokens)*1.3

token= count_tokens('final_chunks.txt')
print(f"Total tokens in the file: {token}")