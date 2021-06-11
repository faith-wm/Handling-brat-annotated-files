

import os
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize

class Brat_to_XML():
    def __init__(self,files_folder,xmlSaveFolder):
        self.files_folder=files_folder
        self.xmlSaveFolder =xmlSaveFolder

    def convert2XML(self):
        folder = self.files_folder
        ann_files = [file for file in os.listdir(folder) if file.split('.')[-1] == 'ann']
        txt_files = [file for file in os.listdir(folder) if file.split('.')[-1] == 'txt']


        # samples = [12374678, 12540501, 15084618, 15769994, 21145085, 26200977, 26547101, 26562292
        #             ,27029708,27589688]

        ann_files = sorted(ann_files)
        for file in ann_files:
            # pmid=file.replace('.ann','')
            # if int(pmid) in samples:
            read_ann = open(os.path.join(folder, file), 'r')

            txt_file = file.replace('ann', 'txt')
            read_txt = open(os.path.join(folder, txt_file), 'r').readlines()
            txt_list = list(read_txt[0])

            indexes = []
            for line in read_ann:
                line = line.split()
                indexes.append((int(line[2]), int(line[3]), line[1]))

            indexes.sort(key=lambda x: x[0])
            offset = 0
            for i in range(len(indexes)):
                start_in = indexes[i][0] + offset
                end_ind = indexes[i][1] + offset

                st_tag = '<{}>'.format(indexes[i][2])
                en_tag = '</{}>'.format(indexes[i][2])

                txt_list[start_in:end_ind] = '{}{}{}'.format(st_tag, ''.join(txt_list[start_in:end_ind]), en_tag)
                offset += len(st_tag) + len(en_tag)

            xml_file = file.replace('ann', 'xml')
            xmlFile=open(os.path.join(self.xmlSaveFolder,xml_file),'w')
            xmlFile.write(''.join(txt_list))

        return 0



class XML_to_BIO():
    def __init__(self, xmlFilesFolder,bio_save_folder):
        self.xmlFilesFolder= xmlFilesFolder
        self.bio_save_folder= bio_save_folder

    def escape_lower_than_symbol(self,html):
        html_list = list(html)
        for index in range(0, len(html) - 1):
            if html_list[index] == '<' and html_list[index + 1] == '.':
                html_list[index] = '&lt;'
        for index in range(0, len(html) - 1):
            if html_list[index] == '<' and html_list[index + 1] == 'or':
                    html_list[index] = '&lt;'
        for index in range(0, len(html) - 1):
            if html_list[index] == '<' and html_list[index + 1] == ' ':
                html_list[index] = '&lt;'
        return ''.join(html_list)

    def convertTOBio(self):
        xml_files = [file for file in os.listdir(self.xmlFilesFolder) if file.split('.')[-1]=='xml']

        for file in xml_files:

            pmid=file.replace('.xml','')

            read_xml= open(os.path.join(self.xmlFilesFolder,file),'r')
            xml_text=[line for line in read_xml]

            xml_text='<doc>{}</doc>'.format(xml_text[0])

            xml_text=self.escape_lower_than_symbol(xml_text)

            soup=bs(xml_text,parser='lxml',features='lxml')

            pmids,tokens,tags=[],[],[]
            for element in soup.find_all('doc'):
                children=list(element.children)
                for child in children:
                    tag_=child.name
                    if tag_!=None and re.search('[0-9]',tag_)==None:
                        words=child.text.split()
                        for w in words:
                            pmids.append(int(pmid))
                            tokens.append(w)
                            tags.append(tag_)

                    else:
                        words=child.split()
                        for w in words:
                            pmids.append(int(pmid))
                            tokens.append(w)
                            tags.append('O')

            df=pd.DataFrame()
            df['pmid']=np.array(pmids)
            df['token']=np.array(tokens)
            df['tag']=np.array(tags)
            df.to_csv(os.path.join(self.bio_save_folder,pmid+'.csv'), index=False,header=False)
        return 0



#BRAT to XML
# folder = 'Files_folder/V1_annotation'
# xmlFolder='Files_folder/XML_files'
# Brat_to_XML(files_folder=folder,xmlSaveFolder=xmlFolder).convert2XML()

#XML to BIO
xmlFolder='Files_folder/XML_files'
bio_folder='Files_folder/IOB_csv_files'
XML_to_BIO(xmlFilesFolder=xmlFolder,bio_save_folder=bio_folder).convertTOBio()




#BRAT to BIO

#CSV to XML