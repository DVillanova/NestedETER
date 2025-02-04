import sys
import os 
import pickle
from compute_nested_substitution_cost import calc_edit_dist, count_number_tokens_named_entity
import typing
from math import sqrt
import copy

from munkres import Munkres

# Global Munkres algorithm
M = Munkres()

#Given two lists of NEs, return matrices of cost and size of substitution operations considering micro average
def generate_micro_cost_and_lengths_matrices(list_ref_ne_trees: list, list_hyp_ne_trees: list) -> tuple[list,list]:
    matrix_size = len(list_ref_ne_trees) + len(list_hyp_ne_trees)
    costs = list()
    lengths = list()
    #Initialize all slots of the matrices to 0.0
    for i in range(matrix_size):
        costs.append([0.0]*matrix_size)
        lengths.append([0.0]*matrix_size)
    
    #Substitutions of GT NEs for dummy symbols
    for i in range(0, len(list_ref_ne_trees)):
        for j in range(len(list_hyp_ne_trees), matrix_size):
            number_tokens_i = count_number_tokens_named_entity(list_ref_ne_trees[i]) 
            costs[i][j] = number_tokens_i
            lengths[i][j] = number_tokens_i


    #Substitutions of HYP NEs for dummy symbols
    for i in range(len(list_ref_ne_trees), matrix_size):
        for j in range(0, len(list_hyp_ne_trees)):
            number_tokens_j = count_number_tokens_named_entity(list_hyp_ne_trees[j]) 
            costs[i][j] = number_tokens_j
            lengths[i][j] = number_tokens_j

    #Substitutions of empty NEs with empty NEs
    for i in range(len(list_ref_ne_trees), matrix_size):
        for j in range(len(list_hyp_ne_trees), matrix_size):
            costs[i][j] = 0.0
            lengths[i][j] = 0.0

    #General cases of cost matrix
    for i in range(len(list_ref_ne_trees)):
        for j in range(len(list_hyp_ne_trees)):
            ref_ne_tree = list_ref_ne_trees[i]
            hyp_ne_tree = list_hyp_ne_trees[j]
            (_, c_x_y, l_x_y) = calc_edit_dist(ref_ne_tree, hyp_ne_tree)

            costs[i][j] = c_x_y
            lengths[i][j] = l_x_y
    
    return costs,lengths

#Given two lists of NEs, return matrices of cost and size of substitution operations considering macro average
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
    
#Compute micro-averaged unordered ETER score for a whole corpus, considering a list of NEs for each document in the corpus
def compute_micro_eter(list_ref_doc_nes: list, list_hyp_doc_nes: list) -> float:
    numerator = 0.0
    denominator = 0.0

    number_ref_nes = 0
    number_hyp_nes = 0

    for doc_i, list_ref_ne_trees in enumerate(list_ref_doc_nes):
        list_hyp_ne_trees = list_hyp_doc_nes[doc_i]

        number_ref_nes += len(list_ref_ne_trees)
        number_hyp_nes += len(list_hyp_ne_trees)

        #If neither reference nor hypothesis contain NEs, skip
        if len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) == 0:
            pass
        #If only GT contains NEs => all NEs are considered as errors
        elif (len(list_ref_ne_trees) != 0 and len(list_hyp_ne_trees) == 0):
            list_number_tokens_ref_nes = [count_number_tokens_named_entity(named_entity) for named_entity in list_ref_ne_trees]
            number_tokens_ref_doc = sum(list_number_tokens_ref_nes)
            numerator += number_tokens_ref_doc
            denominator += number_tokens_ref_doc
        #If only HYP contains NEs => all NEs are considered as errors
        elif (len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) != 0):
            list_number_tokens_hyp_nes = [count_number_tokens_named_entity(named_entity) for named_entity in list_hyp_ne_trees]
            number_tokens_hyp_doc = sum(list_number_tokens_hyp_nes)
            numerator += number_tokens_hyp_doc
            denominator += number_tokens_hyp_doc
        #General case (both lists contain NE trees)
        else:
            cost_matrix, length_matrix = generate_micro_cost_and_lengths_matrices(list_ref_ne_trees, list_hyp_ne_trees)
            indexes = M.compute(cost_matrix)

            for i,j in indexes:
                numerator += cost_matrix[i][j]
                denominator += length_matrix[i][j]
    
    print("REF NEs: ", number_ref_nes)
    print("HYP NEs: ", number_hyp_nes)

    return (numerator / denominator)*100.0


#Compute macro-averaged unordered ETER score for a whole corpus, considering a list of NEs for each document in the corpus
def compute_macro_eter(list_ref_doc_nes: list, list_hyp_doc_nes: list) -> float:

    numerator = 0.0
    denominator = 0.0

    number_ref_nes = 0
    number_hyp_nes = 0

    for doc_i, list_ref_ne_trees in enumerate(list_ref_doc_nes):
        list_hyp_ne_trees = list_hyp_doc_nes[doc_i]

        number_ref_nes += len(list_ref_ne_trees)
        number_hyp_nes += len(list_hyp_ne_trees)

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
    

    print("REF NEs: ", number_ref_nes)
    print("HYP NEs: ", number_hyp_nes)

    return (numerator / denominator)*100.0

#Compute edit distance between sequences of NEs -> return cost of the path and length of the path
def compute_macro_levenshtein(list_ref_ne_trees: list, list_hyp_ne_trees: list) -> tuple[float,float]:
    
    LEN_VECTOR = len(list_ref_ne_trees)+1
    #Vectors of two components -> cost of path and length of  path
    prev_dist_vec = [[0,0] for _ in range(LEN_VECTOR)]
    dist_vec = [[0,0] for _ in range(LEN_VECTOR)]

    #Initialize previous vector
    for i in range(LEN_VECTOR):
        prev_dist_vec[i][0] = i
        prev_dist_vec[i][1] = i

    #Dynamic programming version of levenshtein distance
    for j in range(1, len(list_hyp_ne_trees) + 1):
        dist_vec[0][0] = j
        dist_vec[0][1] = j

        j_hyp_ne = list_hyp_ne_trees[j-1]

        for i in range(1, LEN_VECTOR):
            i_ref_ne = list_ref_ne_trees[i-1]
            dist_ins = 1 + dist_vec[i - 1][0]
            dist_del = 1 + prev_dist_vec[i][0]
            cost_sus, _, _ = calc_edit_dist(ref_ne=i_ref_ne, hyp_ne=j_hyp_ne)
            
            dist_sus = prev_dist_vec[i - 1][0] + cost_sus

            min_dist = min(dist_ins, dist_del, dist_sus)
            dist_vec[i][0] = min_dist
            path_lens = []
            if dist_ins == min_dist:
                path_lens.append(dist_vec[i - 1][1] + 1)
            if dist_del == min_dist:
                path_lens.append(prev_dist_vec[i][1] + 1)
            if dist_sus == min_dist:
                path_lens.append(prev_dist_vec[i - 1][1] + 1)
            dist_vec[i][1] = max(path_lens)

        prev_dist_vec = copy.deepcopy(dist_vec)
        dist_vec = [[0,0] for _ in range(LEN_VECTOR)]

    return prev_dist_vec[-1][0], prev_dist_vec[-1][1]


def compute_micro_levenshtein(list_ref_ne_trees: list, list_hyp_ne_trees: list) -> tuple[float,float]:
    LEN_VECTOR = len(list_ref_ne_trees)+1
    #Vectors of two components -> cost of path and length of  path
    prev_dist_vec = [[0,0] for _ in range(LEN_VECTOR)]
    dist_vec = [[0,0] for _ in range(LEN_VECTOR)]

    #Initialize previous vector
    for i in range(1,LEN_VECTOR):
        i_ref_ne = list_ref_ne_trees[i-1]
        prev_dist_vec[i][0] = prev_dist_vec[i-1][0] + count_number_tokens_named_entity(i_ref_ne)
        prev_dist_vec[i][1] = prev_dist_vec[i-1][1] + count_number_tokens_named_entity(i_ref_ne)

    #Dynamic programming version of levenshtein distance
    for j in range(1, len(list_hyp_ne_trees) + 1):
        j_hyp_ne = list_hyp_ne_trees[j-1]
        
        dist_vec[0][0] = prev_dist_vec[0][0] + count_number_tokens_named_entity(j_hyp_ne)
        dist_vec[0][1] = prev_dist_vec[0][1] + count_number_tokens_named_entity(j_hyp_ne)

        

        for i in range(1, LEN_VECTOR):
            i_ref_ne = list_ref_ne_trees[i-1]
            
            dist_ins = count_number_tokens_named_entity(i_ref_ne) + dist_vec[i - 1][0]
            length_ins = count_number_tokens_named_entity(i_ref_ne) + dist_vec[i - 1][1]

            dist_del = count_number_tokens_named_entity(j_hyp_ne) + prev_dist_vec[i][0]
            length_del = count_number_tokens_named_entity(j_hyp_ne) + prev_dist_vec[i][1]

            _, cost_sus, size_sus = calc_edit_dist(ref_ne=i_ref_ne, hyp_ne=j_hyp_ne)
            length_sus = prev_dist_vec[i - 1][1] + size_sus
            
            dist_sus = prev_dist_vec[i - 1][0] + cost_sus

            min_dist = min(dist_ins, dist_del, dist_sus)
            dist_vec[i][0] = min_dist
            path_lens = []
            if dist_ins == min_dist:
                path_lens.append(length_ins)
            if dist_del == min_dist:
                path_lens.append(length_del)
            if dist_sus == min_dist:
                path_lens.append(length_sus)
            dist_vec[i][1] = max(path_lens)

        prev_dist_vec = copy.deepcopy(dist_vec)
        dist_vec = [[0,0] for _ in range(LEN_VECTOR)]

    return prev_dist_vec[-1][0], prev_dist_vec[-1][1]

#Compute micro-averaged ordered ETER score for a whole corpus, considering a list of NEs for each document in the corpus
def compute_micro_ordered_eter(list_ref_doc_nes: list, list_hyp_doc_nes: list) -> float:
    numerator = 0.0
    denominator = 0.0

    number_ref_nes = 0
    number_hyp_nes = 0

    for doc_i, list_ref_ne_trees in enumerate(list_ref_doc_nes):
        list_hyp_ne_trees = list_hyp_doc_nes[doc_i]

        number_ref_nes += len(list_ref_ne_trees)
        number_hyp_nes += len(list_hyp_ne_trees)

        #If neither reference nor hypothesis contain NEs, skip
        if len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) == 0:
            pass
        #If only GT contains NEs => all NEs are considered as errors
        elif (len(list_ref_ne_trees) != 0 and len(list_hyp_ne_trees) == 0):
            list_number_tokens_ref_nes = [count_number_tokens_named_entity(named_entity) for named_entity in list_ref_ne_trees]
            number_tokens_ref_doc = sum(list_number_tokens_ref_nes)
            numerator += number_tokens_ref_doc
            denominator += number_tokens_ref_doc
        #If only HYP contains NEs => all NEs are considered as errors
        elif (len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) != 0):
            list_number_tokens_hyp_nes = [count_number_tokens_named_entity(named_entity) for named_entity in list_hyp_ne_trees]
            number_tokens_hyp_doc = sum(list_number_tokens_hyp_nes)
            numerator += number_tokens_hyp_doc
            denominator += number_tokens_hyp_doc
        #General case (both lists contain NE trees)
        else:
            cost_best_path, length_best_path = compute_micro_levenshtein(list_ref_ne_trees, list_hyp_ne_trees)
            numerator += cost_best_path
            denominator += length_best_path
    
    print("REF NEs: ", number_ref_nes)
    print("HYP NEs: ", number_hyp_nes)

    return (numerator / denominator)*100.0

#Compute macro-averaged ordered ETER score for a whole corpus, considering a list of NEs for each document in the corpus
def compute_macro_ordered_eter(list_ref_doc_nes: list, list_hyp_doc_nes: list) -> float:
    numerator = 0.0
    denominator = 0.0

    number_ref_nes = 0
    number_hyp_nes = 0

    for doc_i, list_ref_ne_trees in enumerate(list_ref_doc_nes):
        list_hyp_ne_trees = list_hyp_doc_nes[doc_i]

        number_ref_nes += len(list_ref_ne_trees)
        number_hyp_nes += len(list_hyp_ne_trees)

        #If neither reference nor hypothesis contain NEs, skip
        if len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) == 0:
            pass
        #If only one contains NEs (XOR) => all NEs are considered as errors
        elif (len(list_ref_ne_trees) != 0 and len(list_hyp_ne_trees) == 0) or (len(list_ref_ne_trees) == 0 and len(list_hyp_ne_trees) != 0):
            numerator += len(list_ref_ne_trees) + len(list_hyp_ne_trees)
            denominator += len(list_ref_ne_trees) + len(list_hyp_ne_trees)
        #General case (both lists contain NE trees)
        else:
            cost_best_path, length_best_path = compute_macro_levenshtein(list_ref_ne_trees, list_hyp_ne_trees)
            numerator += cost_best_path
            denominator += length_best_path
            
    print("REF NEs: ", number_ref_nes)
    print("HYP NEs: ", number_hyp_nes)

    return (numerator / denominator)*100.0


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
    num_docs = len(list_ref_docs)

    #Compute appropiate score
    
    #Micro levenshtein
    if not macro_average and ordered:
        score = compute_micro_ordered_eter(list_ref_docs, list_hyp_docs)

        #Print results on screen
        print("MICRO OETER:", score)
        print("MICRO OETER (formatted):", round(score,1))

        #Compute 95% confidence interval assuming binomial distribution
        conf_interval = 1.96 * sqrt((score * (100-score)) / num_docs)

        print("95% Confidence interval (Binomial distribution): {:.1f} +- {:.1f} = [{:.1f},{:.1f}]".format(score, conf_interval, score-conf_interval, score+conf_interval))
    

    #Macro levenshtein
    if macro_average and ordered:
        score = compute_macro_ordered_eter(list_ref_docs, list_hyp_docs)

        #Print results on screen
        print("MACRO OETER:", score)
        print("MACRO OETER (formatted):", round(score,1))

        #Compute 95% confidence interval assuming binomial distribution
        conf_interval = 1.96 * sqrt((score * (100-score)) / num_docs)

        print("95% Confidence interval (Binomial distribution): {:.1f} +- {:.1f} = [{:.1f},{:.1f}]".format(score, conf_interval, score-conf_interval, score+conf_interval))
    

    #Micro hungarian
    if not macro_average and not ordered:
        score = compute_micro_eter(list_ref_docs, list_hyp_docs)

        #Print results on screen
        print("MICRO ETER:", score)
        print("MICRO ETER (formatted):", round(score,1))

        #Compute 95% confidence interval assuming binomial distribution
        conf_interval = 1.96 * sqrt((score * (100-score)) / num_docs)

        print("95% Confidence interval (Binomial distribution): {:.1f} +- {:.1f} = [{:.1f},{:.1f}]".format(score, conf_interval, score-conf_interval, score+conf_interval))
    
    

    #Macro hungarian
    if macro_average and not ordered:
        score = compute_macro_eter(list_ref_docs, list_hyp_docs)

        #Print results on screen
        print("MACRO ETER:", score)
        print("MACRO ETER (formatted):", round(score,1))

        #Compute 95% confidence interval assuming binomial distribution
        conf_interval = 1.96 * sqrt((score * (100-score)) / num_docs)

        print("95% Confidence interval (Binomial distribution): {:.1f} +- {:.1f} = [{:.1f},{:.1f}]".format(score, conf_interval, score-conf_interval, score+conf_interval))
    
    