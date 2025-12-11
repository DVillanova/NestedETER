#!/bin/bash

# PARSING .BIO FILES
# .bio files into labels, char_labels, hypotheses, and char_hypotheses directories
mkdir -p ./labels/
rm ./labels/*

mkdir -p ./char_labels/
rm ./char_labels/*

mkdir -p ./hypotheses/
rm ./hypotheses/*

mkdir -p ./char_hypotheses/
rm ./char_hypotheses/*


# TODO: Complete .bio parsing using bio_parser + json_to_pkl.py script


# EVALUATION OVER DATA
# If it is necessary to obtain the computation time it takes, uncomment the SECONDS=0 line
# and the following DURATION=$SECONDS and printf to get it in the evaluation report

printf "WORD LEVEL METRICS\n" > evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py macro ordered ./labels/ ./hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py micro ordered ./labels/ ./hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py macro unordered ./labels/ ./hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py micro unordered ./labels/ ./hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt

printf "\n\nCHAR LEVEL METRICS\n" >> evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py macro ordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py micro ordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py macro unordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt

# SECONDS=0
python3 compute_corpus_metrics.py micro unordered ./char_labels/ ./char_hypotheses/ >> evaluation_report.txt
# DURATION=$SECONDS
# printf "===================\n" >> evaluation_report.txt
# printf "COMPUTATION TIME (IN SECONDS): ${DURATION}\n" >> evaluation_report.txt
# printf "===================\n" >> evaluation_report.txt