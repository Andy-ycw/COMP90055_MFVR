Chronological Order of code development, along with functionality

# Extraction of text from proquest data.
proquest_text_parser.py <br>
text2json.ipynb <br>
    - Convert raw proquest text data to json. <br>
    - Manually coded pub_titles across states. <br>
    - Manually coded political stances of each pub_title. <br>
    - Some analysis using eMFD on political stance, time series, and states. <br>
wa2json.ipynb <br>
    - Use parser in proquest_text_parser.py to parse Factiva rtf, and output wa pickles. <br>

# Check frequent words in the corpus 
LDA.ipynb <br>

# Semantic axes building
## Detect positions of moral words and sentences in each article
pickMFU.py <br>
locate_mf.ipynb

## BERT Pipeline
make_sma.ipynb <br>
sma_tools.py

# Annotation
## Sampling strategy
DDR + GloVe - 95 percentile <br>
Additional requirements? (state, ...)

## Annotation guides
Hoover 2020 and Trager 2022


# temp
mfrc_rough_count.ipynb <br>
tmp.py - for checking counts of mfd and mfd2 <br>
transcript_analysis.ipynb - Analyse the transcript that Kat sent. <br> 
paragraph_analysis - Analyse paragraph and article in terms of moral foundation signal. <br>
