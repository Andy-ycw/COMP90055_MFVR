from typing import *
import spacy
import re
from ddr import DDR
from collections import defaultdict
import numpy as np

# This load dictionaries to variables mfd, mfd2 and emfd; mfd_regex
from emfdscore.load_mfds import mfd2, emfd_single_vice_virtue, mfd_regex, mfd, emfd

class MFU_picker:

    def __init__(self, tokenizer=None):
        self.nlp = spacy.load('en_core_web_sm')
        self.mfd = mfd
        self.mfd_regex = mfd_regex
        self.mfd2 = mfd2
        self.emfd_single_vice_virtue = emfd_single_vice_virtue
        self.mdf_version = ('mfd', 'mfd2', 'emfd')
        self.mdf2_keys = set(mfd2.keys())
        self.emdf_keys = set(emfd_single_vice_virtue.keys())
        self.tokenizer = tokenizer

    def pickMFU(self, text: str, mfd_ver: str = 'mfd') -> List:
        """
        The output is a four-element list - 
        1. A list of tokensized sentences which are the products of spaCy segmentation on a news article.
        2. An index list in which indices point to sentences with moral foundation words.
        3. A nested list of token indices which point to the positions of moral foundation words.
        4. A nested list of virtue-vice
        5. A nested list of matched word
        """
        
        assert mfd_ver in self.mdf_version

        result = [[], [], [], [], []]
        
        # Spacy pipeline - doc level
        doc = self.nlp(text)
        assert doc.has_annotation("SENT_START")

        sent_list = [sent_obj.text for sent_obj in doc.sents]        
        for i in range(len(sent_list)):
            sent = re.sub(r"[\n\xa0]", "", sent_list[i]).strip()
            token_list = self.tokenizer.tokenize(sent) if self.tokenizer else [re.sub(r'[\W]','',word) for word in sent.split()]
            sent = " ".join(token_list)

            # Start generating and formating output data
            result[0].append(sent)
            isSentAppend = False
            token_indices = list()
            virtue_vice_indices = list()
            word_list = list()

            for j in range(len(token_list)):
                word = token_list[j]
                if mfd_ver == 'mfd':
                    for v in self.mfd_regex.keys():
                        if self.mfd_regex[v].match(word):
                            if not isSentAppend:
                                result[1].append(i)
                            token_indices.append(j)
                            virtue_vice_indices.append(self.mfd[v])
                            word_list.append(word)
                            isSentAppend = True
                else:
                    match_condition = word in self.mdf2_keys if mfd_ver == "mfd2" else word in self.emdf_keys
                    if match_condition:
                        if not isSentAppend:
                            result[1].append(i)
                        token_indices.append(j)
                        if mfd_ver == "mfd2":
                            virtue_vice_indices.append(self.mfd2[word]) # emfd does not need.
                        isSentAppend = True
                        word_list.append(word)

            if len(token_indices) != 0:
                result[2].append(token_indices)
                result[3].append(virtue_vice_indices)
                result[4].append(word_list)
        
        return result

class DataFrame_MF_Wrapper:
    moral_foundations = ['care', 'fairness', 'authority', 'loyalty', 'sanctity']
    moral_directions = ['virtue', 'vice']

    def __init__(self, df, spacy_pipeline='en_core_web_sm'):
        # self.nlp = spacy.load(spacy_pipeline)
        self.mfu_picker = MFU_picker()
        # self.ddr = DDR()
        self.df = df        

    def compute_mfd_score(self, mfd_ver):
        mfd_vers = ['mfd', 'mfd2', 'emfd']
        assert mfd_ver in mfd_vers, print(f'Unsupported mfd version: {mfd_ver}')
        self.mfd_picker_wrapper.__func__.__defaults__ = (mfd_ver,)
        df = self.df.copy()

        df[f'{mfd_ver}_count_info'] = df['text'].apply(self.mfd_picker_wrapper)
        for mf in self.moral_foundations:
            for mf_dir in self.moral_directions:
                mf_axis = mf+'.'+mf_dir
                df[mf_axis] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[0][mf_axis])
        df[f'{mfd_ver}_match'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[1])

        return df
    
    # def compute_cosine(self):
    #     df = self.df.copy()
    #     df['raw_ddr'] = df['text'].apply(self.ddr.compute_similarity)
    #     for mf in self.moral_foundations:
    #         df[f'{mf}_virtue'] = df['raw_ddr'].apply(lambda x: x[f'{mf}.virtue'])
    #         df[f'{mf}_vice'] = df['raw_ddr'].apply(lambda x: x[f'{mf}.vice'])
    #         df[mf] = df['raw_ddr'].apply(lambda x: max(x[f'{mf}.virtue'], x[f'{mf}.vice']))
    #     return df

    def mfd_picker_wrapper(self, sent, mfd_ver='mfd'):
        # This wrapper aims to extract the count of mfd match of output from pickMFU() with mfd_ver =  'mfd'.
        # mfd_ver = 'mfd'
        mf_score_dict = defaultdict(float)
        raw_result = self.mfu_picker.pickMFU(sent, mfd_ver)
        foundation_info = raw_result[3]
        matched_words_raw = raw_result[4]

        if mfd_ver != 'emfd':
            mf_found = [
                foundation # i.e. 'care.virtue'
                for sent_level in foundation_info
                for word_level in sent_level
                for foundation in word_level
            ] if mfd_ver == 'mfd' else [
                foundation
                for sent_level in foundation_info
                for word_level in sent_level
                for foundation in word_level.values()
            ]
        
        matched_words = [
            word
            for sent_level in matched_words_raw
            for word in sent_level
        ] if len(matched_words_raw) != 0 else None

        if mfd_ver!='emfd':
            mf_axes = [
                mf+'.'+mf_dir
                for mf in self.moral_foundations
                for mf_dir in self.moral_directions
            ]
            for mf in mf_found:
                if mf in mf_axes:
                    mf_score_dict[mf] += 1
        else: 
            if matched_words is not None:
                for mf in self.moral_foundations:
                    for word in matched_words:
                        foundation_prob = emfd[word][f'{mf}_p']
                        foundation_sent = emfd[word][f'{mf}_sent']
                        mf_dir = 'virtue' if foundation_sent > 0 else 'vice'
                        mf_axis = mf+'.'+mf_dir
                        # mf_score_dict[mf_axis] += foundation_prob + foundation_sent
                        mf_score_dict[mf_axis] += foundation_prob
        
        return mf_score_dict, matched_words

