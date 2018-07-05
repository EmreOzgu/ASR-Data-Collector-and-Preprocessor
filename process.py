from xml.etree import ElementTree
import argparse
import os

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

        if word.find("FORM") is not None:
            result += " " + word.find("FORM").text
        else:
            result += " "

            for morph in word:
                result += morph.find("FORM").text
    return result


''' Processes given sentence and returns the output line '''
def process_sent(sent):
    line = sent.attrib['id']

    line += audio_info(sent)

    #words = corrected_word_list(sent.findall('W'))

    words = sent.findall('W')

    if sent.find("FORM").text != "":
        line += " " + sent.find("FORM").text

    else:
        line += process_words(words)

    '''
    if words:
        line += process_words(words)
    else:
        line += " " + sent.find("FORM").text
    '''
        
    line += '\r\n'

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
    #root = tree.getroot()

    with open("Processed/" + xml[:-4] + "-Processed.txt", 'wb') as outf:

        sents = root.findall("S")

        if sents:
        
            for sent in root.findall("S"):
                '''
                line = sent.attrib['id']

                audio = sent.find("AUDIO")

                if audio is not None:
                    line += " start=" + audio.attrib['start'] + " " + "end=" + audio.attrib['end']

                words = corrected_word_list(sent.findall('W'))
                
                if words:

                    for word in words:
                        
                        utter = word.find("FORM").text

                        if utter is not None:
                            line += " " + utter

                        else:
                            line += " "
                            
                            for morph in word:
                                line += morph.find("FORM").text

                else:
                    line += " " + sent.find("FORM").text

                line += '\r\n'
                outf.write(line.encode('utf-8'))
                '''
                outf.write(process_sent(sent).encode('utf-8'))

        elif root.findall("W"):

            for word in root.findall("W"):

                line = word.attrib['id'] + audio_info(word) + " " + word.find("FORM").text + "\r\n"

                outf.write(line.encode('utf-8'))

                

            




#START OF SCRIPT

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="XML file name in Recordings/ to process (all or specific)")
args = parser.parse_args()

if args.filename.lower() == "all":
    for file in os.listdir("Recordings/"):
        print(file)
        process_file(file)
else:
    process_file(args.filename)
