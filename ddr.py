from typing import Dict, List, Optional
import spacy
import numpy as np
from numpy.linalg import norm

class DDR:
    """
    `seed_words` := A dictionary of moral foundations with the corresponding seed words. 
    * If not specified, a default set of seed words from Mokhberian 2019 will be used.

    `glove_dict` := Dict[str, int] in which the integer is the byte position of the string in the glove embedding file.
    """

    # The seed words below are selected in reference to Twitter Corpus mainly, complement with Reddit Corpus.
    default_seed_words = {
        "care.virtue": ['save', 'defend', 'protect', 'compassion'],
        "care.vice"  : ['harm', 'war', 'kill', 'suffer'],
        "fairness.virtue": ['fair', 'equal', 'justice', 'honesty'],
        "fairness.vice"  : ['unfair', 'unequal', 'unjust', 'dishonest'],
        "loyalty.virtue": ['solidarity', 'nation', 'family', 'support'],
        "loyalty.vice"  : ['betray', 'treason', 'disloyal', 'traitor'], #R
        "authority.virtue": ['duty', 'law', 'obligation', 'order'],
        "authority.vice"  : ['subversion', 'chaos', 'disobey', 'disrespect'], #R
        "sanctity.virtue": ['sacred', 'preserve', 'pure', 'serenity'],
        "sanctity.vice"  : ['dirty', 'repulsive', 'disgusting', 'revolting'],
    }
    default_spacy_pipeline  = "en_core_web_sm"
    default_glove_path = "/Users/yu/Desktop/Data/comp90055/GloVe/glove.840B.300d.txt"

    def __init__(self, 
        seed_words: Optional[Dict[str, List[str]]] = None, 
        spacy_pipeline: Optional[str] = None,
        glove_path: Optional[str] = None):
        
        self.seed_words = seed_words if seed_words else self.default_seed_words
        self.spacy_pipline = self.spacy_pipeline if spacy_pipeline else self.default_spacy_pipeline
        self.glove_path = glove_path if glove_path else self.default_glove_path 

        self.nlp = spacy.load(self.spacy_pipline) 
        self.seed_words = self.seed_words
        self.glove_dict = self.compute_glove_dict(self.glove_path) 
        self.mf_ddr = self.compute_ddr()

    def compute_ddr(self):
        output = dict()
        for mf, seed_words in self.seed_words.items():
            arr_embeddings = np.array([self.get_embeddings(word) for word in seed_words])
            emb_dim = arr_embeddings.shape[1]
            ddr = np.mean(arr_embeddings, axis=0)
            assert emb_dim == ddr.shape[0]
            output[mf] = ddr
        return output

    def get_embeddings(self, word: str) -> List[float]:
        emb_position = self.glove_dict[word]
        with open(self.glove_path, 'r') as f:
            f.seek(emb_position)
            emb_str = f.readline()
            # print(emb_str[:50])
        try:
            emb = [float(num.strip()) for num in list(emb_str.split())[1:]]
        except ValueError:
            print(emb_str)
        assert len(emb) == 300
        return emb

    def compute_similarity(self, sent):
        doc = self.nlp(sent)
        tokens = [token.text for token in doc]
        semantic_emb = np.mean(np.array([self.get_embeddings(token) for token in tokens if token in self.glove_dict] ), axis=0)

        output = dict()
        for mf, ddr in self.mf_ddr.items():
            cosine = np.dot(ddr, semantic_emb)/(norm(ddr)*norm(semantic_emb))
            output[mf] = cosine
        return output

    def compute_glove_dict(self, glove_path):
        position_dict = {}
        with open(glove_path, 'r') as f:
            position = f.tell() 
            line = f.readline()
            while line:
                line_context = line.split()
                token = line_context[0]
                try:
                    float(line_context[1])
                    position_dict[token] = position
                except ValueError: # Skip abnormal tokens.
                    # print("Abnormal tokens: ", line_context[:50])
                    pass
                finally:
                    position = f.tell() 
                    line = f.readline()
                
        return position_dict

# for token in doc:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#             token.shape_, token.is_alpha, token.is_stop)

# position_dict = {}
# with open('/Users/yu/Desktop/Data/comp90055/GloVe/glove.840B.300d.txt', 'r') as f:
#     position = f.tell() 
#     line = f.readline()
#     while line:
#         token = line.split()[0]
#         position_dict[token] = position
        
#         # Next line
#         position = f.tell() 
#         line = f.readline()

# print(list(position_dict.keys())[:50])

# with open('/Users/yu/Desktop/Data/comp90055/GloVe/glove.840B.300d.txt', 'r') as f:
#     position = position_dict['will']
#     f.seek(position)
#     print('will')
#     print(f.readline()[:50])

