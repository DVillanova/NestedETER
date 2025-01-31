import sys
import os 
import pickle
from compute_nested_substitution_cost import calc_edit_dist
import typing

from munkres import Munkres

# Global Munkres algorithm
M = Munkres()

def generate_macro_cost_and_lengths_matrices(list_ref_ne_trees: list, list_hyp_ne_trees: list) -> tuple[list,list]:
    matrix_size = len(list_ref_ne_trees) + len(list_hyp_ne_trees)
    costs = list()
    lengths = list()
    #Initialize all slots of the matrices to 1.0
    for i in range(matrix_size):
        costs.append([1.0]*matrix_size)
        lengths.append([1.0]*matrix_size)
    
    #Substitutions of empty NEs with empty NEs
    for i in range(len(list_ref_ne_trees), matrix_size):
        for j in range(len(list_hyp_ne_trees), matrix_size):
            costs[i][j] = 0.0
            lengths[i][j] = 0.0
    
    #Populating general cases of cost matrix
    for i in range(len(list_ref_ne_trees)):
        for j in range(len(list_hyp_ne_trees)):
            ref_ne_tree = list_ref_ne_trees[i]
            hyp_ne_tree = list_hyp_ne_trees[j]
            (distance_x_y, _, _) = calc_edit_dist(ref_ne_tree, hyp_ne_tree)

            costs[i][j] = distance_x_y
    
    return costs,lengths
    

def compute_macro_eter(list_ref_doc_nes: list, list_hyp_doc_nes: list):

    numerator = 0.0
    denominator = 0.0

    for doc_i, list_ref_ne_trees in enumerate(list_ref_doc_nes):
        list_hyp_ne_trees = list_hyp_doc_nes[doc_i]

        #If neither reference nor hypothesis contain NEs, skip
        if len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) == 0:
            pass

        #If only one contains NEs (XOR) => all NEs are considered as errors
        elif (len(list_ref_ne_trees) != 0 and len(list_hyp_ne_trees) == 0) or (len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) != 0):
            numerator += len(list_ref_ne_trees) + len(list_hyp_ne_trees)
            denominator += len(list_ref_ne_trees) + len(list_hyp_ne_trees)
        
        #General case (both lists contain NE trees)
        else:
            cost_matrix, length_matrix = generate_macro_cost_and_lengths_matrices(list_ref_ne_trees, list_hyp_ne_trees)
            indexes = M.compute(cost_matrix)

            for i,j in indexes:
                numerator += cost_matrix[i][j]
                denominator += length_matrix[i][j]
    
    return numerator / denominator



# def compute_micro_eter():
# def compute_ordered_macro_eter():
# def compute_ordered_micro_eter():


if __name__=="__main__":
    #Read flags to indicate normalization,score, and char-level   
    if len(sys.argv) != 5:
        print("Usage: python compute_corpus_metrics <macro|micro> <ordered|unordered> <char|word> <ref_dir> <hyp_dir>")
        print("<macro|micro>: Whether to macro-average or micro-average")
        print("<ordered|unordered>: Whether to use reading-order constraints (ordered) or hungarian algorithm (unordered)")
        print("<ref_dir>: Path to directory where the reference .pkl lists are stored")
        print("<hyp_dir>: Path to directory where the hypothesis .pkl lists are stored")
        exit(1)
    
    if sys.argv[1] != "macro" and sys.argv[1] != "micro":
        print("<macro|micro>: Whether to macro-average or micro-average")
        exit(1)
    macro_average = True if sys.argv[1] == "macro" else False

    if sys.argv[2] != "ordered" and sys.argv[2] != "unordered":
        print("<ordered|unordered>: Whether to use reading-order constraints (ordered) or hungarian algorithm (unordered)")
        exit(1)
    ordered = True if sys.argv[2] == "ordered" else False

    ref_dir = sys.argv[3]
    hyp_dir = sys.argv[4]

    list_ref_docs = list()
    list_hyp_docs = list()

    #Read .pkl files and form list with whole corpus
    for ref_filename in os.listdir(ref_dir):
        ref_file = open(ref_dir + "/" + ref_filename, "rb")
        ref_ne_tree = pickle.load(ref_file)
        list_ref_docs.append(ref_ne_tree)

    for hyp_filename in os.listdir(hyp_dir):
        hyp_file = open(hyp_dir + "/" + hyp_filename, "rb")
        hyp_ne_tree = pickle.load(hyp_file)
        list_hyp_docs.append(hyp_ne_tree)

    score = 100.0

    #Compute appropiate score
    if macro_average and not ordered:
        score = compute_macro_eter(list_ref_docs, list_hyp_docs)

        #Print results on screen
        print("MACRO ETER:", score)