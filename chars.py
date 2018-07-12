from lxml import etree as ElementTree
import os
import process
import pycountry
import logging
import requests
from bs4 import BeautifulSoup
import time
import sys
from analyze import calc_time

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
    for key in root.attrib:
        if key.endswith('lang') and len(root.attrib[key]) >= 3 and not root.attrib[key].endswith('und'):
            lang = root.attrib[key][-3:].lower()
            return lang

    for child in root:
        if child.tag == "S" or child.tag == "M":
            forms = child.findall("FORM")
            for form in forms:
                if "kindOf" in form.attrib and form.attrib['kindOf'].find('-txt-') != -1:
                    i = form.attrib['kindOf'].find('-txt-')
                    lang = form.attrib['kindOf'][i+5:i+8]
                    return lang
    if lang == "":
        lang_name = xml[xml.find('_')+1:-4].replace('_', ' ')
        
        if lang_name == "Xaracuu":
            lang = "ane"
        else:
            lang = pycountry.languages.get(name=lang_name).alpha_3.lower()

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

def create_written(written, path):
    kinds = ["phono", "ortho", "undet"]

    for kind in kinds:
        written[kind] = []
        
    for filename in os.listdir(path):
        i = filename.find('_')
        j = filename.find('.')
        kind = filename[i+1:j]

        if kind in kinds:
            with open(f'{path}{filename}', 'r', encoding="utf8") as file:
                for line in file:
                    written[kind].append(line.rstrip('\n'))

def write_audio_info(speakers, lang, path):
    filename = f'{path}{lang}_audio.txt'

    with open(filename, 'w', encoding="utf8") as audiof:
        for key in speakers:
            audiof.write(f'{key}={speakers[key]/60} mins\n')

def update_audio_info(speakers, tag):
    audio = tag.find("AUDIO")

    if audio is None:
        return False

    if 'who' in tag.attrib:
        key = tag.attrib['who']
        time = float(audio.attrib["end"]) - float(audio.attrib["start"])
        if key in speakers:
            speakers[key] += time
        else:
            speakers[key] = time

def create_audio_info(speakers, lang, root, path):
    filename = f'{path}{lang}_audio.txt'

    try:
        with open(filename, 'r', encoding="utf8") as audiof:
            for line in audiof:
                key = line[:line.find("=")]
                speakers[key] = float(line[line.find('=')+1:line.find(' mins')]) * 60
    except FileNotFoundError:
        pass

    speakers['Total time'] += calc_time(root)

def delete_audio_info(path):
    if os.path.exists(path):
        for folder in os.listdir(path):
            for file in os.listdir(f'{path}{folder}/'):
                if file.endswith('audio.txt'):
                    os.remove(f'{path}{folder}/{file}')

def create_set(xml):
    written = {}
    speakers = {'Total time' : 0}

    tree = ElementTree.parse("Recordings/" + xml)
    root = process.clean_up(tree.getroot())

    lang = find_lang(root, xml)

    path = f"Stats/{lang}/"

    if not os.path.exists(path):
        os.makedirs(path)

    create_written(written, path)
    create_audio_info(speakers, lang, root, path)

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
                update_audio_info(speakers, sent)
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
                    update_audio_info(speakers, word)
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
            update_audio_info(speakers, root)
            update_files(written, lines, kinds, phonof, orthof, undetf)

    write_audio_info(speakers, lang, path)
    process.remove_empty_files(path, report=False)


if __name__ == "__main__":
    logger.info("Creating character sets...")
    delete_audio_info("Stats/")
    for file in os.listdir("Recordings/"):
        #logger.info(file)
        create_set(file)
        
    logger.info("Character set creation complete.")
