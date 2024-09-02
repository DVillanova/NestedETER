from zss import Node
from compute_nested_substitution_cost import build_tagging_tree, calc_edit_dist, obtain_tagged_and_marked_transcriptions, post_order_traversal_named_entity

#Testing the parsing
g_0_ne = [
    "A", [
        "a", 
        ["B", [
                "b"
            ]],
        "c"
    ]]

g_0_tagging_tree = (
    Node("A").
        addkid( Node("B"))
)

print("Handcrafted tagging tree")
print(g_0_tagging_tree)

g_0_tagging_tree = build_tagging_tree(g_0_ne)

print("Automatic tagging tree")
print(g_0_tagging_tree)


g_1_ne = [
    "A", [
        "a",
        ["B", [
            "b"
        ]],
        ["C", [
            "c",
            ["D", [
                "d"
            ]]
        ]],
        #A SUBTREE TO BE DELETED
        ["C", [
            ["D", [
                "e"
            ]],
            "f"
        ]],
        ["C", [
            ["E", [
                "e"
            ]],
            "f"
        ]],
        "g",
        "h"
    ]
]


g_1_tagging_tree = build_tagging_tree(g_1_ne)
# print("GT tagging tree")
# print(g_1_tagging_tree)

h_1_ne = [
    "B", [
        "a",
        ["B", [
            "b"
        ]],
        ["C", [
            "c",
            ["D", [
                "d"
            ]]
        ]],
        ["C", [
            ["E", [
                "e"
            ]],
            "f"
        ]],
        "g",
    ]
]


# h_1_tagging_tree = build_tagging_tree(h_1_ne)
# print("HYP tagging tree")
# print(h_1_tagging_tree)

# print("GT:",post_order_traversal_named_entity(g_1_ne))
# print("HYP:", post_order_traversal_named_entity(h_1_ne))

ref_editted_transc, hyp_editted_transc = obtain_tagged_and_marked_transcriptions(g_1_ne, h_1_ne)

print(ref_editted_transc)
print(hyp_editted_transc)
print(calc_edit_dist(ref_editted_transc, hyp_editted_transc))

# ref_tagged_transcription = [(False, "a", "tag1"), (True, "b", "tag2"), (False, "c", "tag3"), (False, "d", "tag3")]
# hyp_tagged_transcription = [(False, "a", "tag1"), (False, "b", "tag2"), (False, "d", "tag3"), (False, "c", "tag4"), (False, "d", "tag3")]
# print(calc_edit_dist(ref_tagged_transcription, hyp_tagged_transcription))

#Example 1