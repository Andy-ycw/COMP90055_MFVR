import pandas as pd
# from typing import List
from pickMFU import MFU_picker
from collections import defaultdict
from ddr import DDR
import spacy
from emfdscore.load_mfds import emfd
import numpy as np


class AnnotationSample:
    moral_foundations = ['care', 'fairness', 'authority', 'loyalty', 'sanctity']

    def __init__(self, file_path, article_number, spacy_pipeline='en_core_web_sm'):
        assert file_path[-4:] == 'xlsx', print("The file should be in xlsx format.")
        self.nlp = spacy.load(spacy_pipeline)

        self.excel_sheets = list()
        with pd.ExcelFile(file_path) as f:
            for i in range(article_number):
                df = pd.read_excel(f, sheet_name=f'article_{i}')
                df = df.drop(df.columns[0],axis=1) # Remove a redundant index column.
                df = df.drop(df[df['MF Relevance'].isna() | df['YES/NO Argument Relevance'].isna()].index) # Remove empty rows.
                df['MF Relevance'] = df['MF Relevance'].astype(int)
                df['YES/NO Argument Relevance'] = df['YES/NO Argument Relevance'].astype(int)
                self.excel_sheets.append(df)

        self.mfu_picker = MFU_picker()
        self.ddr = DDR()        

    def compute_mfd_count(self, mfd_ver):
        mfd_vers = ['mfd', 'mfd2', 'emfd']
        assert mfd_ver in mfd_vers, print(f'Unsupported mfd version: {mfd_ver}')
        for i in range(len(self.excel_sheets)):
            df = self.excel_sheets[i]
            self.mfd_picker_wrapper.__func__.__defaults__ = (mfd_ver,)
            df[f'{mfd_ver}_count_info'] = df[df.columns[0]].apply(self.mfd_picker_wrapper)
            df[f'{mfd_ver}_count'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[0])
            for foundation in self.moral_foundations:
                df[f'{foundation}'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[1][foundation])         
            df['vice_count'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[3])
            df[f'{mfd_ver}_match'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[2])
    
    def compute_cosine(self):
        for df in self.excel_sheets:
            df['raw_ddr'] = df['paragraphs'].apply(self.ddr.compute_similarity)
            for mf in self.moral_foundations:
                df[f'{mf}_virtue'] = df['raw_ddr'].apply(lambda x: x[f'{mf}.virtue'])
                df[f'{mf}_vice'] = df['raw_ddr'].apply(lambda x: x[f'{mf}.vice'])
                df[mf] = df['raw_ddr'].apply(lambda x: max(x[f'{mf}.virtue'], x[f'{mf}.vice']))

    def mfd_picker_wrapper(self, sent, mfd_ver='mfd'):
        # This wrapper aims to extract the count of mfd match of output from pickMFU() with mfd_ver =  'mfd'.
        # mfd_ver = 'mfd'
        vice_count = 0
        if mfd_ver != 'emfd':
            raw_result = self.mfu_picker.pickMFU(sent, mfd_ver)[3]
            result = [
                foundation.split(".")[0]
                for sent_level in raw_result
                for word_level in sent_level
                for foundation in word_level
            ] if mfd_ver == 'mfd' else [
                foundation.split(".")[0]
                for sent_level in raw_result
                for word_level in sent_level
                for foundation in word_level.values()
            ]

            vice_count = sum([
                1
                for sent_level in raw_result
                for word_level in sent_level
                for foundation in word_level
                if foundation.split(".")[-1] == 'vice'
            ])
        else:
            raw_result = self.mfu_picker.pickMFU(sent, mfd_ver)[2]
            result = [
                position
                for sent_level in raw_result
                for position in sent_level
            ]
        
        word_result = self.mfu_picker.pickMFU(sent, mfd_ver)[4]
        matched_words = [
            word
            for sent_level in word_result
            for word in sent_level
        ] if len(word_result) != 0 else None

        if mfd_ver!='emfd':
            result_dict = defaultdict(int)
            for foundation_found in result:
                if foundation_found in self.moral_foundations:
                    result_dict[foundation_found] += 1
        else: # Calculate log(prob*intensity) for each matched word
            result_dict = defaultdict(float)
            if matched_words is not None:
                for foundation in self.moral_foundations:
                    for word in matched_words:
                        foundation_prob = emfd[word][f'{foundation}_p']
                        # foundation_sent = abs(emfd[word][f'{foundation}_sent'])
                        result_dict[foundation] += foundation_prob
            else:
                result_dict = {foundation: 0 for foundation in self.moral_foundations}

        # Fill in 0 for foundations without any matched word.
        for foundation in self.moral_foundations:
            if foundation not in result_dict:
                result_dict[foundation] = 0 
        
        # `result_dict` is for counting/scoring for each mf.
        # len(result) is the total number matched words in a paragraph/sentence.
        
        return len(result), result_dict, matched_words, vice_count

