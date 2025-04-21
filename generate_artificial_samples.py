import pickle

word_label_list = [
    [
        "p", [
            "George,",
            "son",
            "of",
            [
                "p", [
                    "John"
                ]
            ],
            ",",
            "was",
            "born",
            "in",
            [
                "l", [
                    "York"
                ]
            ]
        ]
    ],
    [
        "l", [
            "Valencia"
        ]
    ],
    [ 
        "o", [
            "Public",
            "Accounting",
            "Office",
            "of",
            [
                "l", [
                    "Madrid"
                ]
            ]
        ]
    ]
]

output_file = open("labels/artificial_1.pkl", "wb")
pickle.dump(obj=word_label_list, file=output_file)
output_file.close()


word_hyp_list = [
    [ #Mistake is found here (wrong order of NEs)
        "l", [
            "Valancia" #Mistake is found here (wrong character ValAncia instead of Valencia)
        ]
    ],
    [
        "p", [ #Multiple mistakes, such as omitting a whole NE inside (John)
            "Georg,",
            "son",
            "o",
            "John,",
            "was",
            "barn",
            "in",
            [
                "l", [
                    "York"
                ]
            ]
        ]
    ],
    [ 
        "l", [ #Mistake is found here (wrong category "l" instead of "o")
            "Public",
            "Accounting",
            "Office",
            "of",
            [
                "l", [
                    "Madrid"
                ]
            ]
        ]
    ]
]

output_file = open("hypotheses/artificial_1.pkl", "wb")
pickle.dump(obj=word_hyp_list, file=output_file)
output_file.close()



char_label_list = [
    [
        "p", [
            "G",
            "e",
            "o",
            "r",
            "g",
            "e",
            ",",
            " ",
            "s",
            "o",
            "n",
            " ",
            "o",
            "f",
            " ",
            [
                "p", [
                    "J",
                    "o",
                    "h",
                    "n",
                    " "
                ]
            ],
            ",",
            " ",
            "w",
            "a",
            "s",
            " ",
            "b",
            "o",
            "r",
            "n",
            " ",
            "i",
            "n",
            " ",
            [
                "l", [
                    "Y",
                    "o",
                    "r",
                    "k",
                    " "
                ]
            ]
        ]
    ],
    [
        "l", [
            "V",
            "a",
            "l",
            "e",
            "n",
            "c",
            "i",
            "a",
            " "
        ]
    ],
    [ 
        "o", [
            "P",
            "u",
            "b",
            "l",
            "i",
            "c",
            " "
            "A",
            "c",
            "c",
            "o",
            "u",
            "n",
            "t",
            "i",
            "n",
            "g",
            " ",
            "O",
            "f",
            "f",
            "i",
            "c",
            "e",
            " "
            "o",
            "f",
            " ",
            [
                "l", [
                    "M",
                    "a",
                    "d",
                    "r",
                    "i",
                    "d",
                    " "
                ]
            ]
        ]
    ]
]

output_file = open("char_labels/artificial_1.pkl", "wb")
pickle.dump(obj=char_label_list, file=output_file)
output_file.close()


char_hyp_list = [
    [ #Mistake is found here (wrong order of NEs)
        "l", [
            "V",
            "a",
            "l",
            "a", #Mistake is found here (wrong character ValAncia instead of Valencia)
            "n",
            "c",
            "i",
            "a", 
            " "
        ]
    ],
    [
        "p", [ #Multiple mistakes, such as omitting a whole NE inside (John)
            "G",
            "e",
            "o",
            "r",
            "g",
            ",",
            " "
            "s",
            "o",
            "n",
            " ",
            "o",
            " ",
            "J",
            "o",
            "h",
            "n",
            ",",
            " ",
            "w",
            "a",
            "s",
            " ",
            "b",
            "a",
            "r",
            "n",
            " ",
            "i",
            "n",
            " ",
            [
                "l", [
                    "Y",
                    "o",
                    "r",
                    "k",
                    " "
                ]
            ]
        ]
    ],
    [ 
        "l", [ #Mistake is found here (wrong category "l" instead of "o")
            "P",
            "u",
            "b",
            "l",
            "i",
            "c",
            " ",
            "A",
            "c",
            "c",
            "o",
            "u",
            "n",
            "t",
            "i",
            "n",
            "g",
            " ",
            "O",
            "f",
            "f",
            "i",
            "c",
            "e",
            " ",
            "o",
            "f",
            " ",
            [
                "l", [
                    "M",
                    "a",
                    "d",
                    "r",
                    "i",
                    "d",
                    " ",
                ]
            ]
        ]
    ]
]

output_file = open("char_hypotheses/artificial_1.pkl", "wb")
pickle.dump(obj=char_hyp_list, file=output_file)
output_file.close()