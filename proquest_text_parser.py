import re
from collections import defaultdict
from typing import List

def compute_initials(string):
    # Hyphen is used to format id so any original hyphen will be replaced.
    hyphen_regex = re.compile("-")
    string_filtered = hyphen_regex.sub("", string)

    word_list= string_filtered.split()
    initials = ""
    for i in range(len(word_list)):
        initials += word_list[i][0]
    return initials

def date_parser(string, proquest=True):
    if proquest:
        pattern = re.compile(r'(\D{3})\s(\d{1,2}),\s(\d{4})')
        matches = pattern.search(string)
        
        year = matches.group(3) 
        
        day = matches.group(2) 
        day = "0" + day if len(day) == 1 else day
        
        month = matches.group(1)
        if month == "Jan":
            month = "01"
        elif month == "Feb":
            month = "02"
        elif month == "Mar":
            month = "03"
        elif month == "Apr":
            month = "04"
        elif month == "May":
            month = "05"
        elif month == "Jun":
            month = "06"
        elif month == "Jul":
            month = "07"
        elif month == "Aug":
            month = "08"
        elif month == "Sep":
            month = "09"
        elif month == "Oct":
            month = "10"
        elif month == "Nov":
            month = "11"
        elif month == "Dec":
            month = "12"
        else:
            # print("Invalid month format")
            return None
    else: # data from Factiva
        year = '2023'
        raw_day_mon = string.split(year)[0].strip()
        day, month = raw_day_mon.split()
        day = '0'+ day if len(day) == 0 else day

        if month == "January":
            month = "01"
        elif month == "February":
            month = "02"
        elif month == "March":
            month = "03"
        elif month == "April":
            month = "04"
        elif month == "May":
            month = "05"
        elif month == "June":
            month = "06"
        elif month == "July":
            month = "07"
        elif month == "August":
            month = "08"
        elif month == "September":
            month = "09"
        elif month == "October":
            month = "10"
        elif month == "November":
            month = "11"
        elif month == "December":
            month = "12"
        else:
            return None
    
    return year + month + day

def main_parser_proquest(dir, file_num, date):
    pattern = re.compile(r'Full\stext:\s(.*?)(?=____________________________________________________________)', re.DOTALL)
    pattern_sub_list = [
        re.compile(r'\nSubject:.*\n'), 
        re.compile(r'\nBusiness indexing term:.*\n'),
        re.compile(r'\nLocation:.*\n'),
        re.compile(r'\nPeople:.*\n'),
        re.compile(r'\nCompany / organization:.*\n'),
        re.compile(r'\nIdentifier /\s?keyword:.*\n'),
        re.compile(r'\nURL:.*\n'),
        ]
    
    raw_article_list = []
    for text_number in range(1, file_num+1):
        proquest_text_title = f"ProQuestDocuments-{date}-{text_number}.txt"
        with open(f"{dir}/{proquest_text_title}", 'r') as f:
            text = f.read()
            for s in pattern_sub_list:
                text = s.sub("", text)
            matches = pattern.finditer(text)
            
            for match in matches:
                raw_article_list.append(match.group(1))
    
    return raw_article_list

def text2dict(raw_article_list, remove_duplicate=True):
    target_media = (
    # ABC assume national reach. 230 articles.
    ('ABC Premium News; Sydney', 'neutral', 'national'),
    ('7.30; Sydney', 'neutral', 'national'),

    # ACT. 951 articles. But Australian prolly national reach.
    ('The Australian (Online); Canberra, A.C.T.', 'right', 'national'),
    ('The Canberra Times; Canberra, A.C.T.', 'left', 'ACT'),
    
    # NSW
    # ('News.com.au; Sydney, N.S.W.', 'right', 'national'),
    ('Sydney Morning Herald; Sydney, N.S.W.', 'left', 'NSW'),
    ('Sun-Herald; Sydney, N.S.W.', 'left', 'NSW'),
    ('The Daily Telegraph (Online); Surrey Hills, N.S.W.', 'right', 'NSW'),

    # VIC
    ('The Age; Melbourne, Vic.', 'left', 'VIC'),
    ('Herald Sun; Melbourne, Vic.', 'left', 'VIC'),
    ('Sunday Age; Melbourne, Vic.', 'left', 'VIC'),

    # SA
    ('The Advertiser; Adelaide, S. Aust.', 'right', 'SA'),
    
    # QLD
    ('The Courier - Mail; Brisbane, Qld.', 'right', 'QLD'),
    # ('The Cairns Post; Cairns, Qld.', 'right', 'QLD'),
    
    # NT
    ('The Northern Territory News; Darwin, N.T.', 'unclear', 'NT'),

    # TAS
    ('Advocate; Burnie, Tas.', 'unclear', 'TAS'),
    ('The Examiner; Launceston, Tas.', 'unclear', 'TAS'),
    ('The Mercury (Online); Hobart Town', 'unclear', 'TAS'),

    # WA
    ('The West Australian', 'unclear', 'WA'),
    ('WAToday.com.au', 'unclear', 'WA')
    )

    pattern_text = re.compile(r'(.+?)Title:\s', re.DOTALL)
    pattern_title = re.compile(r'\nTitle:\s(.+)\n')
    pattern_date = re.compile(r'\nPublication\sdate:\s(.+)\n')
    pattern_publisher = re.compile(r'\nPublisher:\s(.+)\n')
    pattern_pub_title = re.compile(r'\nPublication\stitle:\s(.+)\n')
    pattern_source = re.compile(r'\nSource\stype:\s(.+)\n')
    pattern_doc = re.compile(r'\nDocument\stype:\s(.+)\n')

    master_dict = {}
    # id_set = set()
    # pub_title_set = set()

    for i in range(len(raw_article_list)):
        raw_text = raw_article_list[i]

        # Add text into the dictionary
        match = pattern_text.search(raw_text)
        text = match.group(1) 

        # Title
        match = pattern_title.search(raw_text)
        title = match.group(1)

        # Date 
        match = pattern_date.search(raw_text)
        try:
            date = date_parser(match.group(1)) if match else None
        except AttributeError:
            # print(match.group(1))
            # AttributeError indicates that abnormal format leading to unexpected parsing.
            date = None

        # Publication title 
        match = pattern_pub_title.search(raw_text)
        pub_title = match.group(1) if match else None
        # Skip articles not from the mainstream media.
        if pub_title not in [media_info[0] for media_info in target_media]:
            continue

        # Publisher 
        match = pattern_publisher.search(raw_text)
        publisher = match.group(1) if match else None

        # Source type 
        match = pattern_source.search(raw_text)
        source = match.group(1) if match else None
        
        # Doc type 
        match = pattern_doc.search(raw_text)
        doc = match.group(1) if match else None

        # Need to derive ID to avoid duplication.
        title_initials = compute_initials(title)
        date_element = date if date else "_"
        pub_title_element = compute_initials(pub_title) if pub_title else "_"

        # Load media info
        for i in range(len(target_media)):
            pub_title_instance = target_media[i][0]
            if pub_title == pub_title_instance:
                edit_stance = target_media[i][1]
                state = target_media[i][2]
    
        # id = title_initials + "-" + pub_title_element + "-" + date_element # Gives larger corpus.
        id = title_initials +  "-" + date_element if remove_duplicate else title_initials + "-" + pub_title_element + "-" + date_element + "-" + state
        
        if id not in master_dict:
            master_dict[id] = dict()
            master_dict[id]['text'] = text
            master_dict[id]['title'] = title
            master_dict[id]['date'] = date
            master_dict[id]['publisher'] = publisher
            master_dict[id]['pub_title'] = pub_title
            master_dict[id]['edit_stance'] = edit_stance
            master_dict[id]['state'] = state
            master_dict[id]['source'] = source
            master_dict[id]['doc'] = doc
        
    return master_dict

class FactivaRtfParser:
    target_media = (
    # ABC assume national reach. 230 articles.
    ('ABC Premium News; Sydney', 'neutral', 'national'),
    ('7.30; Sydney', 'neutral', 'national'),

    # ACT. 951 articles. But Australian prolly national reach.
    ('The Australian (Online); Canberra, A.C.T.', 'right', 'national'),
    ('The Canberra Times; Canberra, A.C.T.', 'left', 'ACT'),
    
    # NSW
    # ('News.com.au; Sydney, N.S.W.', 'right', 'national'),
    ('Sydney Morning Herald; Sydney, N.S.W.', 'left', 'NSW'),
    ('Sun-Herald; Sydney, N.S.W.', 'left', 'NSW'),
    ('The Daily Telegraph (Online); Surrey Hills, N.S.W.', 'right', 'NSW'),

    # VIC
    ('The Age; Melbourne, Vic.', 'left', 'VIC'),
    ('Herald Sun; Melbourne, Vic.', 'left', 'VIC'),
    ('Sunday Age; Melbourne, Vic.', 'left', 'VIC'),

    # SA
    ('The Advertiser; Adelaide, S. Aust.', 'right', 'SA'),
    
    # QLD
    ('The Courier - Mail; Brisbane, Qld.', 'right', 'QLD'),
    # ('The Cairns Post; Cairns, Qld.', 'right', 'QLD'),
    
    # NT
    ('The Northern Territory News; Darwin, N.T.', 'unclear', 'NT'),

    # TAS
    ('Advocate; Burnie, Tas.', 'unclear', 'TAS'),
    ('The Examiner; Launceston, Tas.', 'unclear', 'TAS'),
    ('The Mercury (Online); Hobart Town', 'unclear', 'TAS'),

    # WA
    ('The West Australian', 'unclear', 'WA'),
    ('WAToday.com.au', 'unclear', 'WA')
    )

    def __init__(self):
       self.pattern_dict = {
            "article": re.compile(r'\n\\par(.*)'),
            "HD": [re.compile(r'HD\\(.*)BY\\'), re.compile(r'HD\\(.*)WC\\'), ],
            "PD": [re.compile(r'PD\\(.*)SN\\')],
            "SN": [re.compile(r'SN\\(.*)SC\\')],
            "LP": [re.compile(r'LP\\(.*)TD\\')],
            "TD": [re.compile(r'TD\\(.*)RF\\'), re.compile(r'TD\\(.*)CO\\'), re.compile(r'TD\\(.*)IN\\'),  re.compile(r'TD\\(.*)NS\\')],
            "PUB": [re.compile(r'PUB\\(.*)AN\\')],
            'sub': r'\\.+?\s'
        }

    def parse(self, rtf_path: str, remove_duplicate: bool = True) -> List[str]:
        output_dict = dict() # Match the format with the pickled proquest data.
        with open(rtf_path, 'r') as f:
            text = f.read()
            matches = [match for match in self.pattern_dict["article"].finditer(text)][1:]
            
            # Each match is the content of a news article
            for i in range(len(matches)):
                match = matches[i]
                raw_content = match.group(1)

                # Extract raw text for from the SN row - pub_title
                for j in range(len(self.pattern_dict["SN"])):
                    match_SN = [match for match in self.pattern_dict["SN"][j].findall(raw_content)]
                    if len(match_SN) == 0:
                        continue
                    else:
                        break
                assert len(match_SN) == 1, (f"Sth wrong with parsing PD, match len = {len(match_SN)}, i = {i}\n content = {raw_content}")
                sn = re.sub(self.pattern_dict['sub'], " ", match_SN[0])
                sn = sn.strip()[2:-1].strip()
                if sn not in [media_info[0] for media_info in self.target_media]:
                    continue

                # Extract raw text for from the HD row - title
                for j in range(len(self.pattern_dict["HD"])):
                    match_HD = [match for match in self.pattern_dict["HD"][j].findall(raw_content)]
                    if len(match_HD) == 0:
                        continue
                    else:
                        break
                assert len(match_HD) == 1, (f"Sth wrong with parsing HD, match len = {len(match_HD)}, i = {i}\n content = {raw_content}")
                hd = re.sub(self.pattern_dict['sub'], " ", match_HD[0])
                hd = hd.strip()[2:-1].strip()

                # Extract raw text for from the PD row - date
                for j in range(len(self.pattern_dict["PD"])):
                    match_PD = [match for match in self.pattern_dict["PD"][j].findall(raw_content)]
                    if len(match_PD) == 0:
                        continue
                    else:
                        break
                assert len(match_PD) == 1, (f"Sth wrong with parsing PD, match len = {len(match_PD)}, i = {i}\n content = {raw_content}")
                pd = re.sub(self.pattern_dict['sub'], " ", match_PD[0])
                pd = pd.strip()[2:-1].strip()

                # Extract raw text for from the LP row - leads of article
                for j in range(len(self.pattern_dict["LP"])):
                    match_LP = [match for match in self.pattern_dict["LP"][j].findall(raw_content)]
                    if len(match_LP) == 0:
                        continue
                    else:
                        break
                assert len(match_LP) == 1, (f"Sth wrong with parsing PD, match len = {len(match_LP)}, i = {i}\n content = {raw_content}")
                lp = re.sub(self.pattern_dict['sub'], " ", match_LP[0])
                lp = lp.strip()[2:-1].strip()
                
                # Extract raw text for from the TD row - the body of article
                for j in range(len(self.pattern_dict["TD"])):
                    match_TD = [match for match in self.pattern_dict["TD"][j].findall(raw_content)]
                    if len(match_TD) == 0:
                        continue
                    else:
                        break
                assert len(match_TD) == 1, (f"Sth wrong with parsing PD, match len = {len(match_TD)}, i = {i}\n content = {raw_content}")
                td = re.sub(self.pattern_dict['sub'], " ", match_TD[0])
                td = td.strip()[2:-1].strip()
                
                # Extract raw text for from the PUB row - publisher
                for j in range(len(self.pattern_dict["PUB"])):
                    match_PUB = [match for match in self.pattern_dict["PUB"][j].findall(raw_content)]
                    if len(match_PUB) == 0:
                        continue
                    else:
                        break
                assert len(match_PUB) == 1, (f"Sth wrong with parsing PD, match len = {len(match_PUB)}, i = {i}\n content = {raw_content}")
                pub = re.sub(self.pattern_dict['sub'], " ", match_PUB[0])
                pub = pub.strip()[2:-1].strip()

                # Load media info 
                for i in range(len(self.target_media)):
                    pub_title_instance = self.target_media[i][0]
                    if sn == pub_title_instance:
                        edit_stance = self.target_media[i][1]
                        state = self.target_media[i][2]

                date = date_parser(pd, proquest=False)
                article_id = f"{compute_initials(hd)}-{date}" if remove_duplicate else f"{compute_initials(hd)}-{compute_initials(sn)}-{date}-{state}"
                output_dict[article_id] = {
                    'title': hd,
                    'text': " ".join(lp.split()) + " " + " ".join(td.split()),
                    'date': date,
                    'publisher': pub,
                    'pub_title': sn,
                    'edit_stance': edit_stance,
                    'state': state,
                    'source': '',
                    'doc': ''
                }
        
        return output_dict