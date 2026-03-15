# General utility functions
import pandas as pd
import json

def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def save_json(data, path):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)
