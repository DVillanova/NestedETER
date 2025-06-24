#Translate word level BIO files from input folder into char level BIO
#files to be stored in the output folder

import sys
import os

if __name__=="__main__":
    if len(sys.argv) != 3:
        print("Usage: python word_to_char_bio.py <word_dir> <char_dir>")
        print("<word_dir>: Path to directory where the word-level .bio lists are stored")
        print("<char_dir>: Path to directory where the char-level .bio lists will be outputted")
        exit(1)

    word_dir = sys.argv[1]
    char_dir = sys.argv[2]

    for word_filename in os.listdir(word_dir):
        word_file = open(word_dir + "/" + word_filename, "r")
        char_file = open(char_dir + "/" + word_filename, "w")
        
        for l in word_file.readlines():
            out_str = ""
            (word, tags) = l.strip().split(" ", maxsplit=1)
            
            #First character keeps the original tags
            out_str += word[0] + " " + tags + "\n"
            
            #Rest of characters have I- tag
            tags = tags.replace("B-", "I-")
            for token in word[1:]:
                out_str += token + " " + tags + "\n"
            
            #Add extra whitespace token between words
            out_str += "_" + " " + tags + "\n"

            char_file.write(out_str)
        
        word_file.close()
        char_file.close()
            