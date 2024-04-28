Brief functionality descriptions of scripts in this repo. <br>
The default tokenizer is mostly the default tokenizer in SpaCy. `en_core_web_sm` pipline is used in development. May switch to `en_core_web_trf` when desired. <br>

# Extraction of text from proquest data, and perform mfd analysis.
proquest_text_parser.py <br><br>
main.ipynb <br> 
    - Convert raw proquest text data to json, with options to remove duplicates. <br>
    - Aggregate articles by editorial stance, time series, state, and media respectively to observe moral scores computed from each version of mfd.. <br><br> 

# Semantic axes building
#### Detect positions of moral words and sentences in each article
pickMFU.py <br>
locate_mf.ipynb <br>

#### BERT Pipeline
make_sma.ipynb <br>
sma_tools.py <br>

# Annotation
#### Sampling method - DDR + GloVe
annotation_data_model.py 
    - Class to read excel files of annotation validation sample.
annotation_candidate_validatoin.ipynb 
    - Validate candidate selection method (Both article and paragraph levels)
ddr.py <br>
annotation_prep.ipynb <br>

# archives
wa2json.ipynb <br>
    - Use parser in proquest_text_parser.py to parse Factiva rtf, and output wa pickles. <br>
text2json_emfd.ipynb and text2json_mfd.ipynb <br>
    - The initial attempt of parsing text from ProQuest files, and analysing the collected articles. <br>
    - Manually coded pub_titles across states. <br>
    - Manually coded political stances of each pub_title. <br>
LDA.ipynb <br>
    - Apply LDA on articles for right and left editorial stances
count.ipynb - Combine results from all searches (Removed duplicates and discover identical articles across media.)<br>
mfrc_rough_count.ipynb <br>
tmp.py - for checking counts of mfd and mfd2 <br>
transcript_analysis.ipynb - Analyse the transcript that Kat sent. <br> 
paragraph_analysis - Check paragraph lengths. <br>