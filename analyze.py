''' Analyzes every xml file in terms of what percentage uses ipa, and how much data there is in minutes. '''

from xml.etree import ElementTree
import os
import datetime
import logging
import sys
from pathlib import Path

def calc_time(root):
    ''' Calculate the length of the audio file the xml file is associated with. '''
    i = 0
    j = -1
    assess = True
    search = []
    time = 0
    
    if root.findall("S"):
        search = root.findall("S")
    elif root.findall("W"):
        search = root.findall("W")

    for child in search:
        audio = child.find("AUDIO")
        if audio is not None and "start" in audio.attrib and "end" in audio.attrib:
            try:
                time += float(audio.attrib["end"]) - float(audio.attrib["start"])
            except ValueError:
                continue
    return time

def uses_ipa(form):
    ''' Returns true if form of a S or W tag seems to be in ipa. '''
    return form.attrib["kindOf"] == "phono" or form.attrib["kindOf"] == "ipa" or form.attrib["kindOf"] == "phone" \
           or form.attrib["kindOf"] == "phonetic" or form.attrib["kindOf"] == "phonemic" or form.attrib["kindOf"].lower().startswith("a_word") \
           or form.attrib["kindOf"].lower().startswith("ut")

def is_phono(root):
    ''' Returns true if given xml file has ipa transcriptions, false otherwise. '''
    for child in root:
        if child.tag == "S" or child.tag == "W":
            forms = child.findall("FORM")

            for form in forms:
                if "kindOf" in form.attrib and uses_ipa(form):
                    return True

            return False

        elif child.tag == "FORM":
            if "kindOf" in child.attrib and uses_ipa(child):
                return True

    return False

if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

    phono = 0
    ortho = 0
    time = 0
    src = Path('./Recordings_xml')

    for file in os.listdir(src):
        search = []
        assess = True
        form = True
        
        if file.endswith(".xml"):
            tree = ElementTree.parse(f'{src}/{file}')
            root = tree.getroot()

            time += calc_time(root)

            if is_phono(root):
                phono += 1
            else:
                ortho += 1

                
    phono_perc = (phono / (phono + ortho)) * 100
    ortho_perc = (ortho / (phono + ortho)) * 100

    logger.info(f'Percentage of transcriptions using IPA: {phono_perc}%')
    logger.info(f'Percentage of transcriptions using language-specific orthography: {ortho_perc}%')
    logger.info(f'Total audio in minutes: {time/60}')
