import pandas as pd
# from typing import List
from pickMFU import MFU_picker
from collections import defaultdict


class AnnotationSample:
    moral_foundations = ['care', 'fairness', 'authority', 'loyalty', 'sanctity']

    def __init__(self, file_path, article_number):
        assert file_path[-4:] == 'xlsx', print("The file should be in xlsx format.")
        
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

    def compute_mfd_count(self, mfd_ver):
        mfd_vers = ['mfd', 'mfd2', 'emfd']
        assert mfd_ver in mfd_vers, print(f'Unsupported mfd version: {mfd_ver}')
        for i in range(len(self.excel_sheets)):
            df = self.excel_sheets[i]
            
            if mfd_ver == 'mfd':
                df['mfd_count'] = df[df.columns[0]].apply(self.mfd_picker_wrapper)
                df['mfd_match'] = df[df.columns[0]].apply(self.mfd_match)
            elif mfd_ver == 'mfd2':
                df['mfd2_count'] = df[df.columns[0]].apply(self.mfd2_picker_wrapper)
                df['mfd2_match'] = df[df.columns[0]].apply(self.mfd2_match)
            elif mfd_ver == 'emfd':
                df['emfd_count'] = df[df.columns[0]].apply(self.emfd_picker_wrapper)
                df['emfd_match'] = df[df.columns[0]].apply(self.emfd_match)

        # print(self.excel_sheets[2].head())
    
    def compute_cosine(self):
        # for i in range(len(self.excel_sheets)):
        #     df = self.excel_sheets[i]
        #     df['']
        pass

    def mfd_picker_wrapper(self, sent):
        # This wrapper aims to extract the count of mfd match of output from pickMFU() with mfd_ver =  'mfd'.
        mfd_ver = 'mfd'
        raw_result = self.mfu_picker.pickMFU(sent, mfd_ver)[3]
        result = [
            foundation 
            for sent_level in raw_result
            for word_level in sent_level
            for foundation in word_level
        ]
        return len(result)
    
    def mfd_match(self, sent):
        # This wrapper aims to extract mfd matches from pickMFU() with mfd_ver =  'mfd'.
        mfd_ver = 'mfd'
        sents, mf_sent_indices, mf_word_indices = self.mfu_picker.pickMFU(sent, mfd_ver)[:3]

        output = list()
        for i in range(len(mf_sent_indices)):
            target_sent_idx = mf_sent_indices[i]
            tokens = sents[target_sent_idx].split()
            target_word_indices = mf_word_indices[i]            
            for idx in target_word_indices:
                output.append(tokens[idx])
        
        output = None if not len(output) else output
        return output

    def mfd2_picker_wrapper(self, sent):
        # This wrapper aims to extract part of output from pickMFU() with mfd_ver =  'mfd2'.
        mfd_ver = 'mfd2'
        raw_result = self.mfu_picker.pickMFU(sent, mfd_ver)[3]
        result = [
            foundation 
            for sent_level in raw_result
            for word_level in sent_level
            for foundation in word_level.values()
        ]
        return len(result)
    
    def mfd2_match(self,sent):
        mfd_ver = 'mfd2'
        sents, mf_sent_indices, mf_word_indices = self.mfu_picker.pickMFU(sent, mfd_ver)[:3]

        output = list()
        for i in range(len(mf_sent_indices)):
            target_sent_idx = mf_sent_indices[i]
            tokens = sents[target_sent_idx].split()
            target_word_indices = mf_word_indices[i]            
            for idx in target_word_indices:
                output.append(tokens[idx])
        
        output = None if not len(output) else output
        return output
    
    def emfd_picker_wrapper(self, sent):
        # This wrapper aims to extract part of output from pickMFU() with mfd_ver =  '3mfd'.
        mfd_ver = 'emfd'
        raw_result = self.mfu_picker.pickMFU(sent, mfd_ver)[2]
        result = [
            word_level 
            for sent_level in raw_result
            for word_level in sent_level
        ]
        return len(result)
    
    def emfd_match(self,sent):
        mfd_ver = 'emfd'
        sents, mf_sent_indices, mf_word_indices = self.mfu_picker.pickMFU(sent, mfd_ver)[:3]

        output = list()
        for i in range(len(mf_sent_indices)):
            target_sent_idx = mf_sent_indices[i]
            tokens = sents[target_sent_idx].split()
            target_word_indices = mf_word_indices[i]            
            for idx in target_word_indices:
                output.append(tokens[idx])
        
        output = None if not len(output) else output
        return output

"""Code below is for testing."""
# file_path = './data/annotaion_sample.xlsx'
# article_number = 10

# mfd_vers = ['mfd', 'mfd2', 'emfd']
# for mfd_ver in mfd_vers:
#     sample = AnnotationSample(file_path, article_number)
#     sample.compute_mfd_count(mfd_ver)

#     for i in range(len(sample.excel_sheets)):
#         df = sample.excel_sheets[i]
#         df[f'{mfd_ver}_match_len'] = df[f'{mfd_ver}_match'].apply(lambda x: len(x) if x is not None else 0)
#         df['sanity_check'] = df[f'{mfd_ver}_match_len'] - df[f'{mfd_ver}_count']
#         if df['sanity_check'].sum() != 0:
#             print(f'Something is wrong in the row(s) of dataframe [{i}] below.')
#             print(df[df['sanity_check']!=0])

# Inspect specific sentences
# mfu_picker = MFU_picker()
# test_text = 'I remember living in a tent, I remember living in man-made humpies where it was just leaves and those kinds of shelters, and also have memories of sleeping in ruins along the Coorong,” she told the Sunday Mail'
# print(mfu_picker.pickMFU(test_text, mfd_ver='mfd'))
