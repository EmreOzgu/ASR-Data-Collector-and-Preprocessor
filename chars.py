from lxml import etree as ElementTree
import os
import process
import pycountry
import logging
import requests
from bs4 import BeautifulSoup
import time
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

def look_up_lang(root):
    lang = ""

    code = root.attrib['id']
    site = requests.get(f'https://cocoon.huma-num.fr/exist/crdo/meta/{code}').content
    time.sleep(1)
    soup = BeautifulSoup(site, 'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href[:-3].endswith('code='):
            lang = href[-3:]
            break
    return lang

def find_lang(root, xml):
    lang = ""
    if "xml:lang" in root.attrib and len(root.attrib['xml:lang']) >= 3 and not root.attrib['xml:lang'].endswith('und'):
        lang = root.attrib['xml:lang'][-3:]
    else:
        for child in root:
            if child.tag == "S" or child.tag == "M":
                forms = child.findall("FORM")
                for form in forms:
                    if "kindOf" in form.attrib and form.attrib['kindOf'].find('-txt-') != -1:
                        i = form.attrib['kindOf'].find('-txt-')
                        lang = form.attrib['kindOf'][i+5:i+8]
                        break
    if lang == "":
        lang_name = xml[xml.find('_')+1:-4].replace('_', ' ')
        try:
            lang = pycountry.languages.get(name=lang_name).alpha_3
        except KeyError:
            #lang = look_up_lang(root)
            if lang_name == Xaracuu:
                lang = "ane"

    return lang

def update_files(written, lines, kinds, phonof, orthof, undetf):
    #Get rid of whitespace
    for i, line in enumerate(lines):
        lines[i] = ''.join(lines[i].split())

    p_wrote = False
    o_wrote = False
    u_wrote = False

    if not lines:
        return False
    
    for i, line in enumerate(lines):
        if kinds[i] == "phono" and not p_wrote:
            write_to_file("phono", line, written, phonof)
            p_wrote = True
        elif kinds[i] == "ortho" and not o_wrote:
            write_to_file("ortho", line, written, orthof)
            o_wrote = True
        elif kinds[i] == "" and not u_wrote:
            write_to_file("undet", line, written, undetf)
            u_wrote = True

def write_to_file(kind, line, written, file):
    for char in line:
        char = char.lower()
        if char not in written[kind] and char != '\r' and char != '\n':
            file.write((char + '\r\n').encode('utf-8'))
            written[kind].append(char)

def update_written(written, path):
    written["phono"] = []
    written["ortho"] = []
    written["undet"] = []
    for filename in os.listdir(path):
        with open(f'{path}{filename}', 'r', encoding="utf8") as file:
            i = filename.find('_')
            kind = filename[i+1:i+6]
            for line in file:
                written[kind].append(line.rstrip('\n'))
    logger.info(len(written['undet']))

def create_set(xml):
    written = {}

    tree = ElementTree.parse("Recordings/" + xml)
    root = process.clean_up(tree.getroot())

    lang = find_lang(root, xml)

    path = f"Stats/{lang}/"

    if not os.path.exists(path):
        os.makedirs(path)

    update_written(written, path)

    '''
    for name in os.listdir(path):
        if xml[xml.find('_')+1:-4] == name[:"_Set"]:
            filename = name
        else:
            filename = f"{xml.find('_')+1:-4}_Set"
    '''
    
    with open(f'{path}{lang}_phono.txt', 'ab') as phonof, open(f'{path}{lang}_ortho.txt', 'ab') as orthof, open(f'{path}{lang}_undet.txt', 'ab') as undetf:
        sents = root.findall("S")
        
        #Three different processes for three different main formats of the xml files.
        if sents:
            for sent in sents:
                lines = []
                kinds = []
                process.process_sent(xml, sent, lines, kinds, get_id=False)
                update_files(written, lines, kinds, phonof, orthof, undetf)

        elif root.findall("W"):

            for word in root.findall("W"):
                lines = []
                kinds = []
                forms = word.findall("FORM")
                if forms:
                    for i, form in enumerate(forms):
                        if form.text is not None:
                            #line = word.attrib['id'] + audio_info(word) + " " + word.find("FORM").text + "\r\n"
                            line = process.strip_punc(form.text)
                            process.add_to_list(lines, line, i)
                            process.update_kinds(form, kinds, i)
                    update_files(written, lines, kinds, phonof, orthof, undetf)

                '''
                elif word.find("TRANSL") is not None and word.find("TRANSL").text is not None:
                    line = strip_punc(xml[:-4] + "_" + word.attrib['id'] + " " + word.find("TRANSL").text) + '\r\n'
                    ids.append(line[:line.find(' ')])
                    outf.write(line.encode('utf-8'))
                ''' 

        else:
            lines = []
            kinds = []
            lines.append(process.strip_punc(root.find("FORM").text))
            process.update_kinds(root.find("FORM"), kinds, 0)
            update_files(written, lines, kinds, phonof, orthof, undetf)

    process.remove_empty_files(path)

    logger.info(len(written['undet']))

logger.info("Creating character sets...")

for file in os.listdir("Recordings/"):
    #logger.info(file)
    create_set(file)
    sys.exit(1)

logger.info("Character set creation complete.")
