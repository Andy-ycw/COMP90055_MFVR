Brief functionality descriptions of scripts in this repo. <br>
The default tokenizer is mostly the default tokenizer in SpaCy. `en_core_web_sm` pipline is used in development. May switch to `en_core_web_trf` when desired. <br>

# Extraction of text from proquest data.
proquest_text_parser.py <br><br>
text2json.ipynb <br>
    - Convert raw proquest text data to json. <br>
    - Manually coded pub_titles across states. <br>
    - Manually coded political stances of each pub_title. <br>
    - Some analysis using eMFD on political stance, time series, and states. <br><br>
wa2json.ipynb <br>
    - Use parser in proquest_text_parser.py to parse Factiva rtf, and output wa pickles. <br>

# Check frequent words in the corpus 
LDA.ipynb <br>

# Semantic axes building
#### Detect positions of moral words and sentences in each article
pickMFU.py <br>
locate_mf.ipynb <br>

#### BERT Pipeline
make_sma.ipynb <br>
sma_tools.py <br>

# Annotation
#### Sampling method - DDR + GloVe
ddr.py <br>
annotation_prep.ipynb <br>

#### Annotation guides
Hoover 2020 and Trager 2022 <br>

# Non semantic analyses
### Dictionary-based counting analysis
count.ipynb - Computed moral foundation counts by media aggregation with(out) token length normalisation.


# temp
mfrc_rough_count.ipynb <br>
tmp.py - for checking counts of mfd and mfd2 <br>
transcript_analysis.ipynb - Analyse the transcript that Kat sent. <br> 
paragraph_analysis - Check paragraph lengths. <br>
