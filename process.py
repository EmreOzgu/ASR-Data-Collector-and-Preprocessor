from lxml import etree as ElementTree
import argparse
import os
import sys

def strip_punc(string):
    puncs = [',', '!', '?', '"', '...', '--', '<', '>', '»', '«', '\n', '\r']

    for punc in puncs:
        string = string.replace(punc, '')

    string = string.replace('. ', ' ')
    
    ''' Get rid of excess whitespace, while preserving space between tokens '''
    string = ' '.join(string.split())

    return string

''' Checks if the word is empty, which is the case for some xml files. '''
def corrected_word_list(word_list):
    for word in word_list:
        if word.find("FORM") is not None:
            return word_list
    return None

''' Gets rid of empty tags in the xml file. '''
def clean_up(root):
    for child in root:
        if len(child) < 1 and len(child.attrib) < 1 and child.text is None:
            root.remove(child)
        elif len(child) > 1:
            child = clean_up(child)

    return root

def process_words(words):

    result = ""

    for word in words:

        forms = word.findall("FORM")

        if forms:
            for form in forms:
                if form.text:
                    result += " " + form.text
                    break
        else:
            result += " "

            for morph in word.findall("M"):
                result += morph.find("FORM").text
    return result


''' Processes given sentence and returns the output line '''
def process_sent(sent, num=None):

    if 'id' in sent.attrib:
        line = sent.attrib['id']
    else:
        line = "s" + str(num)

    line += audio_info(sent)

    words = sent.findall('W')

    phrases = sent.find("FORM")

    if phrases is not None:
        for phrase in phrases.itertext():
            line += " " + phrase
    elif words:
        line += process_words(words)
    elif sent.find("TRANSL") is not None:
        line += " " + sent.find("TRANSL").text
    '''    
    line += '\r\n'

    return strip_punc(line)
    '''

    line = strip_punc(line) + '\r\n'

    return line
def audio_info(tag):

    result = ""

    audio = tag.find("AUDIO")

    if audio is not None:
        result = " start=" + audio.attrib['start'] + " " + "end=" + audio.attrib['end']

    return result

def process_file(xml):
    path = "Processed/"

    if not os.path.exists(path):
        os.makedirs(path)
        
    tree = ElementTree.parse("Recordings/" + xml)
    root = clean_up(tree.getroot())
    
    with open("Processed/" + xml[:-4] + "-Processed.txt", 'wb') as outf:

        sents = root.findall("S")

        if sents:
        
            for sent in root.findall("S"):
                num = 1
                outf.write(process_sent(sent, num).encode('utf-8'))
                num += 1

        elif root.findall("W"):

            for word in root.findall("W"):
                
                if word.find("FORM") is not None and word.find("FORM").text is not None:
                    line = word.attrib['id'] + audio_info(word) + " " + word.find("FORM").text + "\r\n"

                    outf.write(strip_punc(line).encode('utf-8'))

        else:
            line = root.attrib['id'] + " " + root.find("FORM").text
            outf.write(strip_punc(line).encode('utf-8'))

#START OF SCRIPT
parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="XML file name in Recordings/ to process (all or specific)")
args = parser.parse_args()

if args.filename.lower() == "all":
    print("Processing...")
    for file in os.listdir("Recordings/"):
        process_file(file)
else:
    process_file(args.filename)
print("Processing complete.")
