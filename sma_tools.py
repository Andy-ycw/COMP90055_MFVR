from torch.utils.data import Dataset
from typing import Dict, List, Union
from transformers import BertTokenizer

def flatten_mf_dict(mf_dict, key_name: str, _size: int = -1) -> List[str]:
    assert type(mf_dict) == dict, f"Type {type(mf_dict)} is not a dictionary."
    keys = [key for key in mf_dict.keys()]
    sent_list = []

    assert _size >= -1, f"The size parameter is for debugging, the value {_size} is not within the supported range."
    start = 0 if _size == -1 else len(keys)-_size
    for i in range(start, len(keys)):
        key = keys[i]
        sents = mf_dict[key][key_name][0] # sents have already been tokenized with BertTokenizer
        indices_mf_sent = mf_dict[key][key_name][1]

        for idx in indices_mf_sent:
            sent_list.append(sents[idx])
    return keys, sent_list

class MFDataset(Dataset):

    def __init__(self, sents: List[str]):
        self.sents = sents
    
    def __len__(self):
        return len(self.sents)

    def __getitem__(self, idx):
        return self.sents[idx]



                

