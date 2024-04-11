Chronological Order of code development, along with functionality

# Extraction of text from proquest data.
proquest_text_parser.py
text2json.ipynb 
    - Convert raw proquest text data to json. 
    - Manually coded pub_titles across states.
    - Manually coded political stances of each pub_title.
    - Some analysis using eMFD on political stance, time series, and states.
wa2json.ipynb
    - Use parser in proquest_text_parser.py to parse Factiva rtf, and output wa pickles.

# Check frequent words in the corpus 
LDA.ipynb

# Semantic axes building
## Detect positions of moral words and sentences in each article
pickMFU.py
locate_mf.ipynb

## BERT Pipeline
make_sma.ipynb
sma_tools.py

# Annotation
## Sampling strategy
DDR + GloVe - 95 percentile
Additional requirements? (state, ...)

## Annotation guides
Hoover 2020 and Trager 2022


# temp
mfrc_rough_count.ipynb
tmp.py - for checking counts of mfd and mfd2
transcript_analysis.ipynb - Analyse the transcript that Kat sent.
paragraph_analysis - Analyse paragraph and article in terms of moral foundation signal.
