from zss import Node
from compute_nested_substitution_cost import calc_edit_dist, obtain_tagged_and_marked_transcriptions, post_order_traversal_named_entity

# <A> a <B> b </B> c </A>
g_0_ne = [
    "A", [
        "a",
        [
            "B", [
                "b"
            ]
        ],
        "c"
    ]
]

# <persName> George Washington </persName>
g_1_ne_word = [
    "persName", [
        "George",
        "Washington"
    ]
]

g_1_ne_char = [
    "persName", [
        "G",
        "e",
        "o",
        "r",
        "g",
        "e",
        " ",
        "W",
        "a",
        "s",
        "h",
        "i",
        "n",
        "g",
        "t",
        "o",
        "n"
    ]
]

# <A> a b <C> c </C> d</A>
g_2_ne = [
    "A", [
        "a",
        "b",
        [
            "C", [
                "c"
            ]
        ],
        "d"
    ]
]

# <1> <2> A </2> <2> B </2> </1>
g_3_ne = [
    "1", [
        [
            "2", [
                "A"
            ]
        ],
        [
            "2", [
                "B"
            ]
        ]
    ]
] 

# Empty NE
h_0_ne = []

# <A> a b c </A> => Case of deletion of a category <B>
h_1_ne = [
    "A", [
        "a",
        "b",
        "c"
    ]
]

# <A> a <B> b </B> </A> => Case of missing a part of transcription
h_2_ne = [
    "A", [
        "a",
        [
            "B", [
                "b"
            ]
        ]
    ]
]

# <A> <B> b </B> c </A> => Case of missing a part of the transcription (in different part)
h_3_ne = [
    "A", [
        [
            "B", [
                "b"
            ]
        ],
        "c"
    ]
]

# <A> e <B> f </B> g </A> => Transcription substitutions
h_4_ne = [
    "A", [
        "e",
        [
            "B", [
                "f"
            ]
        ],
        "g"
    ]
]

# <A> e <B></B> g </A> => Category without transcription (shouldn't be possible)
h_5_ne = [
    "A", [
        "e",
        [
            "B", []
        ],
        "g"
    ]
]

# <persName> George </persName>
h_6_ne_word = [
    "persName", [
        "George"
    ]
]

h_6_ne_char = [
    "persName", [
        "G",
        "e",
        "o",
        "r",
        "g",
        "e",
    ]
]

# <placeName> George </placeName>
h_7_ne_word = [
    "placeName", [
        "George"
    ]
]

h_7_ne_char = [
    "placeName", [
        "G",
        "e",
        "o",
        "r",
        "g",
        "e",
    ]
]

# <A> a <C> b <C> c</C></C> d</A>
h_8_ne = [
    "A", [
        "a",
        [
            "C", [
                "b", 
                [
                    "C", [
                        "c"
                    ]
                ]
            ]
        ],
        "d"
    ]
]

# <A> a <C> b <D> c</D></C> d</A>
h_9_ne = [
    "A", [
        "a",
        [
            "C", [
                "b", 
                [
                    "D", [
                        "c"
                    ]
                ]
            ]
        ],
        "d"
    ]
]

# <1> A <2> B </2> </1> (goes with g_3_ne, case of deleting a category
h_10_ne = [
    "1", [
        "A",
        [
            "2", [
                "B"
            ]
        ]
    ]
]

#<1> <2> A </2> <2> B </2> </1>
#<1> A <2> B </2> </1>
#Comparison gives 1 due to order in which tagging tree edit operations is considered
#but should be 0.5
assert(calc_edit_dist(g_3_ne, h_10_ne)) == 0.5
assert(calc_edit_dist(h_10_ne, g_3_ne)) == 0.5

assert calc_edit_dist(g_0_ne, h_0_ne) == 1.0
assert calc_edit_dist(h_0_ne, g_0_ne) == 1.0

assert abs(0.33333333 - calc_edit_dist(g_0_ne, h_1_ne)) < 0.0001
assert abs(0.33333333 - calc_edit_dist(h_1_ne, g_0_ne)) < 0.0001

assert abs(0.33333333 - calc_edit_dist(g_0_ne, h_2_ne)) < 0.0001
assert abs(0.5 - calc_edit_dist(h_2_ne, g_0_ne)) < 0.0001

assert abs(0.33333333 - calc_edit_dist(g_0_ne, h_3_ne)) < 0.0001
assert abs(0.5 - calc_edit_dist(h_3_ne, g_0_ne)) < 0.0001

assert (calc_edit_dist(h_4_ne, g_0_ne)) == 1.0
assert (calc_edit_dist(g_0_ne, h_4_ne)) == 1.0

assert calc_edit_dist(g_0_ne, h_5_ne) == 1.0
assert calc_edit_dist(h_5_ne, g_0_ne) == 1.0

assert calc_edit_dist(g_1_ne_word, h_6_ne_word) == 0.5
assert calc_edit_dist(h_6_ne_word, g_1_ne_word) == 1.0

assert abs(0.647058824 - calc_edit_dist(g_1_ne_char, h_6_ne_char)) < 0.0001
assert calc_edit_dist(h_6_ne_char, g_1_ne_char) == 1.0

assert calc_edit_dist(g_1_ne_word, h_7_ne_word) == 1.0
assert calc_edit_dist(h_7_ne_word, g_1_ne_word) == 1.0

assert calc_edit_dist(g_1_ne_char, h_7_ne_char) == 1.0
assert calc_edit_dist(h_7_ne_char, g_1_ne_char) == 1.0

assert calc_edit_dist(g_2_ne, h_8_ne) == 0.25
assert calc_edit_dist(h_8_ne, g_2_ne ) == 0.25

assert calc_edit_dist(g_2_ne, h_9_ne) == 0.5
assert calc_edit_dist(h_9_ne, g_2_ne ) == 0.5

