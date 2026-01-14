#Open folder with JSON files and turn them into .pkl lists with just the hierarchy, store them in the same folder


import sys
import os
import json
import pickle

def process_nested_ne(ne: dict) ->  list:
    ne_tree = []
    category = ne["category"]
    ne_tree.append(category)
    ne_tree.append([])

    children = ne["children"]
    for child in children:
        if type(child) == str:
            ne_tree[1].append(child)
        else:
            subtree = process_nested_ne(child)
            ne_tree[1].append(subtree)
    
    return ne_tree

def hierarchy_to_nested_list(hierarchy: list) -> list:
    doc_tree = []

    for ne in hierarchy:
        ne_tree = process_nested_ne(ne)
        doc_tree.append(ne_tree)

    return doc_tree


if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: python word_to_char_bio.py <json_dir>")
        print("<json_dir>: Path to directory where the JSON files are stored")
        exit(1)

    json_dir = sys.argv[1]
    
    for filename in os.listdir(json_dir):
        if filename.endswith("json"):
            file = open(json_dir + filename)
            data = json.load(file)
            hierarchy_list= hierarchy_to_nested_list(data["hierarchy"])
            
            pickle_filename = filename.replace(".json", ".pkl")
            pickle_file = open(json_dir + pickle_filename, "wb")
            pickle.dump(hierarchy_list, pickle_file)

            file.close()
            pickle_file.close()