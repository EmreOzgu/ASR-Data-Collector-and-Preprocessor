from lxml import etree as ElementTree
import argparse
import os
import sys
import logging
from analyze import uses_ipa

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

def remove_between(string, c1, c2):
    while True:
        i = string.find(c1)
        j = string.find(c2)
        if i != -1 and j != -1 and i < j:
            string = string.replace(string[i:j+1], '')
        else:
            break
    return string

def strip_punc(string):
    ''' Gets rid of punctuations and unnecessary whitespace '''
    
    puncs = ['.', ',', '! ', ' !', '?', '"', '...', '--', '<', '>', '»', '«', '\n', '\r', '~', '”', '“', ' /', '*', '(', ')', '[', ']', '…', ' :', ': ', ';', '~', '=']
    dashes = ['-', '—', '–', '–', '-']

    #Remove things in brackets, parantheses.
    string = remove_between(string, '[', ']')
    string = remove_between(string, '(', ')')
    string = remove_between(string, '<', '>')

    for punc in puncs:
        string = string.replace(punc, '')

    for dash in dashes:
        string = string.replace(dash, ' ')
    
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

def process_forms(forms, start, lines, kinds):
    for i, form in enumerate(forms):
        for phrase in form.itertext():
            add_to_line(lines, start, " " + phrase, i)
        update_kinds(form ,kinds, i)

def add_to_list(result, new, i):
    if i < len(result):
        result[i] = new
    else:
        result.append(new)

def add_to_line(lines, start, add, i):
    if i < len(lines):
        lines[i] += add
    else:
        lines.append(start + add)

def update_kinds(form, kinds, i):
    if 'kindOf' in form.attrib:
        if uses_ipa(form):
            add_to_list(kinds, "phono", i)
        else:
            add_to_list(kinds, "ortho", i)
    else:
        add_to_list(kinds, "", i)

def empty_forms(forms):
    for form in forms:
        if form.text:
            return False
    return True

def process_words(words, start, lines, kinds):
    ''' Find and return the text for each word. '''

    for word in words:

        forms = word.findall("FORM")

        if forms:
            process_forms(forms, start, lines, kinds)
        else:
            start += " "

            for i, line in enumerate(lines):
                add_to_line(lines, "", " ", i)
            
            for morph in word.findall("M"):
                forms = morph.findall("FORM")
                for i, form in enumerate(forms):
                    if form.text:
                        add_to_line(lines, start, form.text, i)
                        update_kinds(form, kinds, i)

def process_sent(xml, sent, lines, kinds, num=0, get_id=True):
    ''' Processes given sentence and returns the output line '''
    start = ""
    #Get the ID.
    if get_id:
        if 'id' in sent.attrib:
            start = xml[:-4] + '_' + sent.attrib['id']
        else:
            start = xml[:-4] + '_' + "s" + str(num)

    #line += audio_info(sent)
    words = sent.findall('W')
    forms = sent.findall("FORM")

    if forms and not empty_forms(forms):
        process_forms(forms, start, lines, kinds)

    elif words:
        process_words(words, start, lines, kinds)

    '''
    elif sent.find("TRANSL") is not None:
        line += " " + sent.find("TRANSL").text
    '''
    for i, line in enumerate(lines):
        lines[i] = strip_punc(lines[i]) + '\r\n'

def audio_info(tag):
    ''' Get the audio info for a given tag. '''
    result = ""

    audio = tag.find("AUDIO")

    if audio is not None:
        result = " start=" + audio.attrib['start'] + " " + "end=" + audio.attrib['end']

    return result

def check_errors(file, ids):

    if not ids:
        return None

    for id1 in ids:
        for id2 in ids:
            if id1 == id2 and ids.index(id1) != ids.index(id2):
                logger.warning(f'Duplicate ID found in {file}')

def write_files(lines, kinds, phonof, orthof, undetf):
    p_wrote = False
    o_wrote = False
    u_wrote = False

    if not lines:
        return False
    
    for i, line in enumerate(lines):
        if kinds[i] == "phono" and not p_wrote:
            phonof.write(line.encode('utf-8'))
            p_wrote = True
        elif kinds[i] == "ortho" and not o_wrote:
            orthof.write(line.encode('utf-8'))
            o_wrote = True
        elif kinds[i] == "" and not u_wrote:
            undetf.write(line.encode('utf-8'))
            u_wrote = True

def remove_empty_files(path, report=True):
    num = 0
    for file in os.listdir(path):
        if not os.path.getsize(path + file):
            os.remove(path + file)
            num += 1
        if num == 3 and report:
            logger.info(f"{file[:file.find('_Processed')]} is empty. Could be because transcription not available.")
  
def process_file(xml, src, path):
    ''' Process the information of an xml file into a .txt file. '''

    if not os.path.exists(path):
        os.makedirs(path)
        
    tree = ElementTree.parse(src + xml)
    root = clean_up(tree.getroot())
    
    
    with open(f'{path}{xml[:-4]}_Processed_phono.txt', 'wb+') as phonof, open(f'{path}{xml[:-4]}_Processed_ortho.txt', 'wb+') as orthof, open(f'{path}{xml[:-4]}_Processed_undet.txt', 'wb+') as undetf:

        sents = root.findall("S")
        ids = []
        
        #Three different processes for three different main formats of the xml files.
        if sents:
            for sent in sents:
                lines = []
                kinds = []
                num = 1
                process_sent(xml, sent, lines, kinds, num)
                if lines:
                    ids.append(lines[0][:lines[0].find(' ')])
                write_files(lines, kinds, phonof, orthof, undetf)
                num += 1

        elif root.findall("W"):

            for word in root.findall("W"):
                lines = []
                kinds = []
                forms = word.findall("FORM")
                if forms:
                    for i, form in enumerate(forms):
                        if form.text is not None:
                            #line = word.attrib['id'] + audio_info(word) + " " + word.find("FORM").text + "\r\n"
                            line = strip_punc(xml[:-4] + "_" + word.attrib['id'] + " " + form.text) + '\r\n'
                            add_to_list(lines, line, i)
                            update_kinds(form, kinds, i)
                    if lines:              
                        ids.append(lines[0][:lines[0].find(' ')])
                    write_files(lines, kinds, phonof, orthof, undetf)

                '''
                elif word.find("TRANSL") is not None and word.find("TRANSL").text is not None:
                    line = strip_punc(xml[:-4] + "_" + word.attrib['id'] + " " + word.find("TRANSL").text) + '\r\n'
                    ids.append(line[:line.find(' ')])
                    outf.write(line.encode('utf-8'))
                ''' 

        else:
            line = strip_punc(xml[:-4] + "_" + root.attrib['id'] + " " + root.find("FORM").text)
            ids.append(line[:line.find(' ')])
            undetf.write(line.encode('utf-8'))


        check_errors(phonof, ids)
        check_errors(orthof, ids)
        check_errors(undetf, ids)

    remove_empty_files(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="XML file name in Recordings/ to process (all or specific)")
    args = parser.parse_args()

    src = "Recordings/"
    path = "Processed/"

    if args.filename.lower() == "all":
        logger.info("Processing...")
        for file in os.listdir(src):
            process_file(file, src, path)
        
    else:
        process_file(args.filename, src, path)
    logger.info("Processing complete.")
