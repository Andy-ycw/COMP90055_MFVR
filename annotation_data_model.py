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
            self.mfd_picker_wrapper.__func__.__defaults__ = (mfd_ver,)
            df[f'{mfd_ver}_count_info'] = df[df.columns[0]].apply(self.mfd_picker_wrapper)
            df[f'{mfd_ver}_count'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[0])
            for foundation in self.moral_foundations:
                df[f'{foundation}'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[1][foundation])         
            df[f'{mfd_ver}_match'] = df[f'{mfd_ver}_count_info'].apply(lambda x: x[2])
    
    def compute_cosine(self):
        # for i in range(len(self.excel_sheets)):
        #     df = self.excel_sheets[i]
        #     df['']
        pass

    def mfd_picker_wrapper(self, sent, mfd_ver='mfd'):
        # This wrapper aims to extract the count of mfd match of output from pickMFU() with mfd_ver =  'mfd'.
        # mfd_ver = 'mfd'
        raw_result = self.mfu_picker.pickMFU(sent, mfd_ver)[3]
        result = [
            foundation.split(".")[0]
            for sent_level in raw_result
            for word_level in sent_level
            for foundation in word_level
        ]

        result_dict = defaultdict(int)
        for foundation in self.moral_foundations:
            for foundation_found in result:
                if foundation_found == foundation:
                    result_dict[foundation] += 1
        
        word_result = self.mfu_picker.pickMFU(sent, mfd_ver)[4]
        matched_words = [
            word
            for sent_level in word_result
            for word in sent_level
        ] if len(word_result) != 0 else None

        return len(result), result_dict, matched_words

