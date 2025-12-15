from __future__ import absolute_import
import zss
from zss import Node, Operation
import copy
from collections import deque
from six.moves import range

try:
    import numpy as np
    zeros = np.zeros
except ImportError:
    def py_zeros(dim, pytype):
        assert len(dim) == 2
        return [[pytype() for y in range(dim[1])]
                for x in range(dim[0])]
    zeros = py_zeros


try:
    from editdistance import eval as strdist
except ImportError:
    def strdist(a, b):
        if a == b:
            return 0
        else:
            return 1

artificial_root_category = "ARTIFICIAL_ROOT"
CATEGORY = 0
CHILDREN = 1
MARK = 2

#Given the representation of a Named Entity as a tuple (category, children) where children is a list that may contain
#either strings (leaf nodes, transcriptions) or tuples (category, children) that represent subtrees, do a breadth-first
#traversal of the tree to build the same structure in zss Nodes
def build_tagging_tree(named_entity: list) -> Node:
    if len(named_entity) == 0:
        return None

    tagging_tree = Node(named_entity[CATEGORY])
    queue = deque()

    # Store (path_from_root, node_tuple, depth_index)
    # path_from_root: list of indices to follow from root
    # node_tuple: the current node data
    # depth_index: index at current depth (to identify sibling position)
    for idx, subtree in enumerate(named_entity[CHILDREN]):
        if isinstance(subtree, list):
            queue.append(([], subtree, idx))

    while queue:
        path_from_root, node_tuple, current_depth_index = queue.popleft()

        # Locate parent node by following path indices
        parent_node = tagging_tree
        for index_path in path_from_root:
            parent_node = Node.get_children(parent_node)[index_path]

        # Insert the new node
        parent_node.addkid(Node(node_tuple[CATEGORY]))

        # Create new path for next depth (list concatenation, not deepcopy)
        new_path = path_from_root + [current_depth_index]

        # Add children to queue
        for idx, subtree in enumerate(node_tuple[CHILDREN]):
            if isinstance(subtree, list):
                queue.append((new_path, subtree, idx))

    return tagging_tree

#Overwrite function definition of Distance in zss to return all sequences of edit operations instead of
#just one that can reach the final node

REMOVE = Operation.remove
INSERT = Operation.insert
UPDATE = Operation.update
MATCH = Operation.match

def distance(A, B, get_children, insert_cost, remove_cost, update_cost,
             return_operations=False):
    A, B = zss.AnnotatedTree(A, get_children), zss.AnnotatedTree(B, get_children)
    size_a = len(A.nodes)
    size_b = len(B.nodes)
    treedists = zeros((size_a, size_b), float)
    operations = [[[] for _ in range(size_b)] for _ in range(size_a)]

    def treedist(i, j):
        Al = A.lmds
        Bl = B.lmds
        An = A.nodes
        Bn = B.nodes

        m = i - Al[i] + 2
        n = j - Bl[j] + 2
        fd = zeros((m, n), float)
        partial_ops = [[[] for _ in range(n)] for _ in range(m)]

        ioff = Al[i] - 1
        joff = Bl[j] - 1

        partial_ops[0][0] = [[]]

        for x in range(1, m):
            node = An[x + ioff]
            fd[x][0] = fd[x-1][0] + remove_cost(node)
            partial_ops[x][0] = [[Operation(REMOVE, node)]]  

        for y in range(1, n):
            node = Bn[y + joff]
            fd[0][y] = fd[0][y-1] + insert_cost(node)
            partial_ops[0][y] = [[Operation(INSERT, arg2=node)]]  

        for x in range(1, m):
            for y in range(1, n):
                node1 = An[x + ioff]
                node2 = Bn[y + joff]

                if Al[i] == Al[x + ioff] and Bl[j] == Bl[y + joff]:
                    costs = [fd[x-1][y] + remove_cost(node1),
                             fd[x][y-1] + insert_cost(node2),
                             fd[x-1][y-1] + update_cost(node1, node2)]
                    min_cost = min(costs)
                    fd[x][y] = min_cost



                    if costs[0] == min_cost:
                        partial_ops[x][y].extend([path + [Operation(REMOVE, node1)]
                                                  for path in partial_ops[x-1][y]])
                    if costs[1] == min_cost:
                        partial_ops[x][y].extend([path + [Operation(INSERT, arg2=node2)]
                                                  for path in partial_ops[x][y-1]])
                    if costs[2] == min_cost:
                        op_type = MATCH if fd[x][y] == fd[x-1][y-1] else UPDATE
                        partial_ops[x][y].extend([path + [Operation(op_type, node1, node2)]
                                                  for path in partial_ops[x-1][y-1]])

                    operations[x + ioff][y + joff] = partial_ops[x][y]
                    treedists[x + ioff][y + joff] = fd[x][y]

                else:
                    p = Al[x + ioff] - 1 - ioff
                    q = Bl[y + joff] - 1 - joff
                    costs = [fd[x-1][y] + remove_cost(node1),
                             fd[x][y-1] + insert_cost(node2),
                             fd[p][q] + treedists[x + ioff][y + joff]]
                    min_cost = min(costs)
                    fd[x][y] = min_cost

                    if costs[0] == min_cost:
                        partial_ops[x][y].extend([path + [Operation(REMOVE, node1)]
                                                  for path in partial_ops[x-1][y]])
                    if costs[1] == min_cost:
                        partial_ops[x][y].extend([path + [Operation(INSERT, arg2=node2)]
                                                  for path in partial_ops[x][y-1]])
                    if costs[2] == min_cost: 
                        #operations[x][y] may contain a list of lists
                        for op_list in operations[x + ioff][y + joff]:
                            partial_ops[x][y].extend([path + op_list for path in partial_ops[p][q]])

    for i in A.keyroots:
        for j in B.keyroots:
            treedist(i, j)

    if return_operations:
        return treedists[-1][-1], operations[-1][-1]
    else:
        return treedists[-1][-1]

zss.distance = distance

def simple_distance(A, B, get_children=Node.get_children,
        get_label=Node.get_label, label_dist=strdist, return_operations=False):
    return zss.distance(
        A, B, get_children,
        insert_cost=lambda node: label_dist('', get_label(node)),
        remove_cost=lambda node: label_dist(get_label(node), ''),
        update_cost=lambda a, b: label_dist(get_label(a), get_label(b)),
        return_operations=return_operations
    )

zss.simple_distance = simple_distance


def post_order_traversal_named_entity(orig_named_entity: list, path_from_root=None, index_node=0) -> list:
    if path_from_root is None:
        path_from_root = []

    if len(orig_named_entity) > 1:  # Category node
        path_from_root.append((orig_named_entity[CATEGORY], index_node))
        post_order = []

        children = orig_named_entity[CHILDREN]
        for idx, child in enumerate(children):
            if isinstance(child, list):
                post_order.extend(post_order_traversal_named_entity(child, path_from_root, idx))

        post_order.append(path_from_root[:])
        path_from_root.pop()  # Backtrack - reuse same list
        return post_order
    else:
        return []

#Function to count number of textual tokens in a NE with list representation
def count_number_tokens_named_entity(named_entity: list) -> int:
    post_order_traversal = post_order_traversal_named_entity(named_entity)
    number_tokens = 0

    for path_from_root in post_order_traversal:
        node_to_count = named_entity
        for node_step in path_from_root[1:]:
            node_to_count = node_to_count[CHILDREN][node_step[1]]
        
        list_tokens = [child for child in node_to_count[CHILDREN] if isinstance(child, str)]
        number_tokens += len(list_tokens)
        

    return number_tokens

def post_order_traversal_tagging_tree(tagging_tree: Node, path_from_root = [], index_node = 0) -> list:
    if tagging_tree is not None:
        path_from_root = path_from_root[:]
        path_from_root.append((Node.get_label(tagging_tree), index_node))
        post_order = []
        children = list(Node.get_children(tagging_tree))

        for idx,child in enumerate(children):
            post_order.extend(post_order_traversal_tagging_tree(child, path_from_root, idx))
        
        post_order.append(path_from_root)
        return post_order
    else:
        return []

def obtain_list_tagged_transcriptions(named_entity: list, counter_dict: dict) -> list:
    transcription_list = []
    counter_tag = counter_dict.get(named_entity[CATEGORY], 0)
    counter_dict[named_entity[CATEGORY]] = counter_tag + 1

    for child in named_entity[CHILDREN]:
        if isinstance(child, str): #Child is a transcription
            transcription_list.append((named_entity[CATEGORY] + "_" + str(counter_tag), child))
        else: #Child is a subtree
            transcription_list.extend(obtain_list_tagged_transcriptions(child, counter_dict))

    return transcription_list

def add_marks_to_named_entity(named_entity: list, marks: list) -> list:
    named_entity_copy = copy.deepcopy(named_entity)
    post_order_traversal = post_order_traversal_named_entity(named_entity_copy)
    
    #Use marks information (in post-order) to add the mark to each node in the named_entity
    for idx,path_from_root in enumerate(post_order_traversal):
        mark = marks[idx]

        node_to_modify = named_entity_copy
        for node_step in path_from_root[1:]:
            node_to_modify = node_to_modify[CHILDREN][node_step[1]]
        
        node_to_modify.append(mark)
    
    return named_entity_copy

def obtain_marked_transcriptions(marked_named_entity: list) -> list:
    transcription_list = []
    for child in marked_named_entity[CHILDREN]:
        if isinstance(child, str): #Child is a transcription
            transcription_list.append((marked_named_entity[MARK], child))
        else: #Child is a subtree
            transcription_list.extend(obtain_marked_transcriptions(child))

    return transcription_list


#TODO: Make the method compute tagging error rate from tagging tree edit distance
def obtain_tagged_and_marked_transcriptions(orig_ref_named_entity: list, orig_hyp_named_entity: list) -> list[tuple]:
    #Cases where one NE is empty => mark all the elements in the other as "wrong"
    if len(orig_ref_named_entity) == 0:
        tagged_and_marked_ref_transc = []      
        
        hyp_ne = copy.deepcopy(orig_hyp_named_entity)
        tagged_hyp_transc = obtain_list_tagged_transcriptions(hyp_ne, dict())
        tagged_and_marked_hyp_transc = []
        for idx, tagged_item in enumerate(tagged_hyp_transc):
            tagged_and_marked_hyp_transc.append((True, tagged_item[1], tagged_item[0]))

        return [(tagged_and_marked_ref_transc, tagged_and_marked_hyp_transc)]

    elif len(orig_hyp_named_entity) == 0:
        tagged_and_marked_hyp_transc =  []

        ref_ne = copy.deepcopy(orig_ref_named_entity)
        tagged_ref_transc = obtain_list_tagged_transcriptions(ref_ne, dict())
        tagged_and_marked_ref_transc = []
        for idx, tagged_item in enumerate(tagged_ref_transc):
            tagged_and_marked_ref_transc.append((True, tagged_item[1], tagged_item[0]))

        return [(tagged_and_marked_ref_transc, tagged_and_marked_hyp_transc)]

    #Construct Node object to represent tagging structure for zss computation of Tree Edit Distance
    hyp_ne = copy.deepcopy(orig_hyp_named_entity)
    ref_ne = copy.deepcopy(orig_ref_named_entity)
    ref_tagging_tree = build_tagging_tree(ref_ne) 
    hyp_tagging_tree = build_tagging_tree(hyp_ne)

    #Compute tree edit distance between reference and hypothesis tagging tree
    #to employ the best sequences of edit operations in a post-process
    (cost, operations) = simple_distance(ref_tagging_tree, 
                                         hyp_tagging_tree,
                                         label_dist=lambda a, b: int(a != b),
                                         return_operations=True)


    list_tagged_and_marked_ref_hyp_transc = list()
    
    
    orig_ref_ne = copy.deepcopy(ref_ne)
    orig_hyp_ne = copy.deepcopy(hyp_ne)

    for op_seq in operations:
        #Operations are given in post-order (left to right, depth first) over reference and
        #when inserting, the order of insertions is also given in post-order.
        post_order_ref = post_order_traversal_named_entity(orig_ref_ne)
        marks_ref = [False]*len(post_order_ref)
        idx_traversal_ref = 0
        removed_nodes = 0

        post_order_hyp = post_order_traversal_named_entity(orig_hyp_ne)
        marks_hyp = [False]*len(post_order_hyp)
        idx_traversal_hyp = 0
        inserted_nodes = 0

        ref_ne = copy.deepcopy(orig_ref_ne)
        hyp_ne = copy.deepcopy(orig_hyp_ne)    


        for (idx,op) in enumerate(op_seq): 
            if idx_traversal_ref < len(post_order_ref):
                path_node_ref = post_order_ref[idx_traversal_ref]
            else:
                path_node_ref = False

            if idx_traversal_hyp < len(post_order_hyp):
                path_node_hyp = post_order_hyp[idx_traversal_hyp]
            else:
                path_node_hyp = False
            
            
            if op.type == op.remove:
                removed_nodes += 1
                #Since we have to remove the GT category, the text for the ref. node is wrong
                marks_ref[idx_traversal_ref] = True

                #Traverse the reference ne to find node
                node_to_modify = ref_ne
                father_node = ref_ne
                for node_step in path_node_ref[1:]:
                    father_node = node_to_modify
                    node_to_modify = node_to_modify[CHILDREN][node_step[1]]
                
                #Delete child category by slicing the father
                #Insert the text from the removed node into the father
                slicing_point = path_node_ref[-1][1]
                father_node[CHILDREN] = (father_node[CHILDREN][:slicing_point] +
                                        node_to_modify[CHILDREN] +
                                        father_node[CHILDREN][slicing_point+1:])

                #Recompute post-order to account for changes in NE structure
                post_order_ref = [[]]*removed_nodes + post_order_traversal_named_entity(ref_ne)

                #Deletion of node (match op.arg1 -> None), advance in traversal for ref. tree
                idx_traversal_ref += 1
            elif op.type == op.insert:
                inserted_nodes += 1
                #Since we have to insert the hypothesized category, the text for the hyp. node is wrong
                marks_hyp[idx_traversal_hyp] = True

                #An insertion in the reference tree is going to be treated as a deletion in hyp. tree
                #Traverse the hyp ne to find node
                node_to_modify = hyp_ne
                father_node = hyp_ne
                for node_step in path_node_hyp[1:]:
                    father_node = node_to_modify
                    node_to_modify = node_to_modify[CHILDREN][node_step[1]]
                
                #Delete child category by slicing the father
                #Insert the text from the removed node into the father
                slicing_point = path_node_hyp[-1][1]
                father_node[CHILDREN] = (father_node[CHILDREN][:slicing_point] +
                                        node_to_modify[CHILDREN] +
                                        father_node[CHILDREN][slicing_point+1:])

                #Recompute post-order to account for changes in NE structure
                post_order_hyp = [[]]*inserted_nodes + post_order_traversal_named_entity(hyp_ne)

                #Insertion of node (match None -> op.arg2), advance in traversal for hyp. tree
                idx_traversal_hyp += 1
            elif op.type == op.update:
                #Since we have to update the label, the text for both ref. and hyp. nodes is wrong
                marks_ref[idx_traversal_ref] = True
                marks_hyp[idx_traversal_hyp] = True

                #Traverse the reference ne to find node
                node_to_modify = ref_ne
                for node_step in path_node_ref[1:]:
                    node_to_modify = node_to_modify[CHILDREN][node_step[1]]
                
                #Update the label in reference 
                node_to_modify[CATEGORY] = str(Node.get_label(op.arg2))

                #Label substitution, advance in the post-order traversal for both tagging trees 
                idx_traversal_hyp += 1
                idx_traversal_ref += 1
            elif op.type == op.match:
                #Perfect node match, advance in the post-order traversal for both tagging trees
                idx_traversal_hyp += 1
                idx_traversal_ref += 1
            
        
        tagged_ref_transc = obtain_list_tagged_transcriptions(ref_ne, dict())
        marked_ref_ne = add_marks_to_named_entity(orig_ref_ne, marks_ref)
        marked_ref_transc = obtain_marked_transcriptions(marked_ref_ne)
        
        
        tagged_hyp_transc = obtain_list_tagged_transcriptions(hyp_ne, dict())
        marked_hyp_ne = add_marks_to_named_entity(orig_hyp_ne, marks_hyp)
        marked_hyp_transc = obtain_marked_transcriptions(marked_hyp_ne)
        

        tagged_and_marked_ref_transc = []
        for idx, tagged_item in enumerate(tagged_ref_transc):
            marked_item = marked_ref_transc[idx]
            tagged_and_marked_ref_transc.append((marked_item[0], tagged_item[1], tagged_item[0]))

        tagged_and_marked_hyp_transc = []
        for idx, tagged_item in enumerate(tagged_hyp_transc):
            marked_item = marked_hyp_transc[idx]
            tagged_and_marked_hyp_transc.append((marked_item[0], tagged_item[1], tagged_item[0]))

        list_tagged_and_marked_ref_hyp_transc.append((tagged_and_marked_ref_transc, tagged_and_marked_hyp_transc))
    
    return list_tagged_and_marked_ref_hyp_transc
    

#Given 2 lists of tagged marked transcriptions, compute edit distance. Transcriptions incorporate the tag for each token
#and a mark (boolean) to indicate whether the substitution cost for that token must always be one (True) or can be computed
#normally (False). Therefore, each element is a tuple of three elements (MARKED: {True, False}, token: str, tag: str)
#if it is necessary to compute char-level edit distance, the elements must be split previously
def calc_edit_dist(ref_ne: list, hyp_ne: list, tagging_weight = 1.0) -> tuple[float,float,float]:
    #Exception: substituting empty NE with empty NE
    if len(ref_ne) == 0 and len(hyp_ne) == 0:
        raise Exception("Reference entity and hypothesized entity were of size 0")

    #Substituting an empty NE with a normal NE, cost 1
    if len(ref_ne) == 0 or len(hyp_ne) == 0:
        return 1.0, len(ref_ne)+len(hyp_ne), len(ref_ne)+len(hyp_ne)
    

    ref_ne = [artificial_root_category, [ref_ne]]
    hyp_ne = [artificial_root_category, [hyp_ne]]
    list_tagged_and_marked_transcription_tuples = obtain_tagged_and_marked_transcriptions(ref_ne, hyp_ne)

    list_edit_distances = []
    list_costs = []
    list_sizes = []

    #Compute levenshtein distance considering marked elements and tags
    #Iterate over tuples of reference and hypothesis tagged and marked transcriptions
    #according to the sequence of Tree Edit operations that produces said transcriptions
    #to later perform a search of the minimum
    for (ref_tagged_transcription, hyp_tagged_transcription) in list_tagged_and_marked_transcription_tuples:
        LEN_VECTOR = len(ref_tagged_transcription)+1
        #Vectors of two components -> cost of path and length of  path
        prev_dist_vec = [[0,0] for _ in range(LEN_VECTOR)]
        dist_vec = [[0,0] for _ in range(LEN_VECTOR)]

        #Initialize previous vector
        for i in range(LEN_VECTOR):
            prev_dist_vec[i][0] = i
            prev_dist_vec[i][1] = i

        #Dynamic programming version of levenshtein distance
        for j in range(1, len(hyp_tagged_transcription) + 1):
            dist_vec[0][0] = j
            dist_vec[0][1] = j
            for i in range(1, LEN_VECTOR):
                dist_ins = 1 + dist_vec[i - 1][0]
                dist_del = 1 + prev_dist_vec[i][0]
                
                transc_err = int(ref_tagged_transcription[i - 1][1] != hyp_tagged_transcription[j - 1][1])
                if (ref_tagged_transcription[i - 1][0] == True #Reference marked as wrong
                    or hyp_tagged_transcription[j - 1][0] == True #Hypothesis marked as wrong
                    or ref_tagged_transcription[i - 1][2] != hyp_tagged_transcription[j - 1][2]): #Tagging does not match    
                    cost_sus = tagging_weight + (1-tagging_weight) * transc_err
                else:
                    cost_sus = transc_err
                
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

            prev_dist_vec, dist_vec = dist_vec, prev_dist_vec
            
            dist_vec = [[0,0] for _ in range(LEN_VECTOR)]

        delta_o_x_y = float(prev_dist_vec[-1][0]) / prev_dist_vec[-1][1]
        list_edit_distances.append(delta_o_x_y)
        list_costs.append(prev_dist_vec[-1][0])
        list_sizes.append(prev_dist_vec[-1][1])
    
    #Search for index of min cost
    min_cost_o_x_y = min(list_costs)
    index_min = 0
    for i,cost_o_x_y in enumerate(list_costs):
        if min_cost_o_x_y == cost_o_x_y:
            index_min = i

    return list_edit_distances[index_min],list_costs[index_min],list_sizes[index_min]