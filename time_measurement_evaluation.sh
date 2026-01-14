#!/bin/bash

# PARSING .BIO FILES
# .bio files into labels, char_labels, hypotheses, and char_hypotheses directories
# mkdir -p ./labels/
# rm ./labels/*

# mkdir -p ./char_labels/
# rm ./char_labels/*

# mkdir -p ./hypotheses/
# rm ./hypotheses/*

# mkdir -p ./char_hypotheses/
# rm ./char_hypotheses/*


# TODO: Complete .bio parsing using bio_parser + json_to_pkl.py script


# EVALUATION OVER DATA
printf "WORD LEVEL METRICS\n" > evaluation_report.txt

ts=$(date +%s%N)
compute-eter macro ordered ./labels/ ./hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

ts=$(date +%s%N)
compute-eter micro ordered ./labels/ ./hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

ts=$(date +%s%N)
compute-eter macro unordered ./labels/ ./hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

ts=$(date +%s%N)
compute-eter micro unordered ./labels/ ./hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

printf "\n\nCHAR LEVEL METRICS\n" >> evaluation_report.txt

ts=$(date +%s%N)
compute-eter macro ordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

ts=$(date +%s%N)
compute-eter micro ordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

ts=$(date +%s%N)
compute-eter macro unordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

ts=$(date +%s%N)
compute-eter micro unordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
tt=$((($(date +%s%N) - $ts)/1000000)) ; echo "Time taken: $tt ms" >> evaluation_report.txt

