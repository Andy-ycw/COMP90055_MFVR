from typing import *
import spacy
import re

# This load dictionaries to variables mfd, mfd2 and emfd; mfd_regex
from emfdscore.load_mfds import mfd2, emfd_single_vice_virtue, mfd_regex, mfd

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