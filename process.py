from lxml import etree as ElementTree
import argparse
import os
import sys

def strip_punc(string):
    ''' Gets rid of punctuations and unnecessary whitespace '''
    
    puncs = [',', '!', '?', '"', '...', '--', '<', '>', '»', '«', '\n', '\r']

    for punc in puncs:
        string = string.replace(punc, '')

    string = string.replace('. ', ' ')
    
    #Get rid of excess whitespace, while preserving space between tokens
    string = ' '.join(string.split())

    return string

def clean_up(root):
    ''' Gets rid of empty tags in the xml file. '''
    for child in root:
        if len(child) < 1 and len(child.attrib) < 1 and child.text is None:
            root.remove(child)
        elif len(child) > 1:
            child = clean_up(child)

    return root

def process_words(words):
    ''' Find and return the text for each word. '''
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

def process_sent(sent, num=None):
    ''' Processes given sentence and returns the output line '''
    #Get the ID.
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
        
    line = strip_punc(line) + '\r\n'

    return line

def audio_info(tag):
    ''' Get the audio info for a given tag. '''
    result = ""

    audio = tag.find("AUDIO")

    if audio is not None:
        result = " start=" + audio.attrib['start'] + " " + "end=" + audio.attrib['end']

    return result

def process_file(xml):
    ''' Process the information of an xml file into a .txt file. '''
    path = "Processed/"

    if not os.path.exists(path):
        os.makedirs(path)
        
    tree = ElementTree.parse("Recordings/" + xml)
    root = clean_up(tree.getroot())
    
    #with open(path + xml[:-4] + "-Processed.txt", 'wb') as outf:
    with open(f'{path}{xml[:-4]}-Processed.txt', 'wb') as outf:
        sents = root.findall("S")

        #Three different processes for three different main formats of the xml files.
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="XML file name in Recordings/ to process (all or specific)")
    args = parser.parse_args()

    if args.filename.lower() == "all":
        print("Processing...")
        sys.stdout.flush()
        for file in os.listdir("Recordings/"):
            process_file(file)
    else:
        process_file(args.filename)
    print("Processing complete.")
