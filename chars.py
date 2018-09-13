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
from unicodedata import normalize
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

def look_up_lang(root):
    ''' Finds the recording ID from root and looks up the iso code for the language. Function isn't used right now to prevent creating unnecessary traffic. '''
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
    #Pause for a second to regulate requests to the website.
    time.sleep(1)
    return lang

def find_lang(source, xml):
    ''' Finds and returns the iso 639-3 code for an xml file in the given source folder. '''

    tree = ElementTree.parse(f'{source}/{xml}')
    root = process.clean_up(tree.getroot())
    
    lang = ""

    #Try to find the code from the lang attribute in xml.
    for key in root.attrib:
        if key.endswith('lang') and len(root.attrib[key]) >= 3 and not root.attrib[key].endswith('und'):
            lang = root.attrib[key][-3:].lower()
            return lang

    #Try to find the code from the kindOf element in form.
    for child in root:
        if child.tag == "S" or child.tag == "M":
            forms = child.findall("FORM")
            for form in forms:
                if "kindOf" in form.attrib and form.attrib['kindOf'].find('-txt-') != -1:
                    i = form.attrib['kindOf'].find('-txt-')
                    lang = form.attrib['kindOf'][i+5:i+8]
                    return lang

    #If code is still not found, try to find the code from the xml name.
    if lang == "":
        lang_name = xml[xml.find('_')+1:-4].replace('_', ' ')

        #Hard coded one language that was causing trouble. look_up_lang function could be used here also, which is a more general solution, but I didn't want to create unnecessary traffic.
        if lang_name == "Xaracuu":
            lang = "ane"
        else:
            lang = pycountry.languages.get(name=lang_name).alpha_3.lower()

    return lang

def update_files(written, lines, kinds, phonof, orthof, undetf):
    ''' Write to each file the line with the appropriate kind. '''
    #Get rid of whitespace.
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
    ''' Write each char in line to the given file. Add the written char to written[kind] so that it doesn't get written into another file again. '''
    line = normalize('NFD', line.lower())
    
    for char in line:
        if char not in written[kind] and char != '\r' and char != '\n':
            file.write((char + '\r\n').encode('utf-8'))
            written[kind].append(char)

def create_written(written, path):
    ''' Reads the existing files in path and adds the written characters into the written dictionary, with the appropriate kind key. '''
    kinds = ["phono", "ortho", "undet"]

    for kind in kinds:
        written[kind] = []
        
    for filename in os.listdir(path):
        i = filename.find('_')
        j = filename.find('.')
        kind = filename[i+1:j]

        if kind in kinds:
            with open(f'{path}/{filename}', 'r', encoding="utf8") as file:
                for line in file:
                    written[kind].append(line.rstrip('\n'))

def write_audio_info(speakers, lang, path):
    ''' Writes the audio length in minutes for each speaker, into a txt file in path. '''
    filename = f'{path}/{lang}_audio.txt'

    with open(filename, 'w', encoding="utf8") as audiof:
        for key in speakers:
            audiof.write(f'{key}={speakers[key]/60} mins\n')

def update_audio_info(speakers, tag):
    ''' For a given xml tag, finds the speaker and audio info, and updates the total time in speakers dictionary. '''
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
    ''' Reads existing audio info from the path for a given lang code, updates speakers accordingly, and adds the total time of the given root xml file to the dictionary. '''
    filename = f'{path}/{lang}_audio.txt'

    try:
        with open(filename, 'r', encoding="utf8") as audiof:
            for line in audiof:
                key = line[:line.find("=")]
                speakers[key] = float(line[line.find('=')+1:line.find(' mins')]) * 60
    except FileNotFoundError:
        pass
    speakers['Total time'] += calc_time(root)
    speakers[f'{root.tag}'] += calc_time(root)

def delete_audio_info(path):
    ''' Deletes all of the audio info in the given path consisting of folders with iso 639-3 language codes. '''
    if os.path.exists(path):
        for folder in os.listdir(path):
            for file in os.listdir(f'{path}/{folder}/'):
                if file.endswith('audio.txt'):
                    os.remove(f'{path}/{folder}/{file}')

def create_set(source, dest, xml):
    ''' Creates character sets (phono, ortho, undetermined) and audio info for a given xml from the source folder, into the specific language's folder in dest. '''
    tree = ElementTree.parse(f'{source}/{xml}')
    root = process.clean_up(tree.getroot())

    speakers = {'Total time' : 0,
                f'{root.tag}': 0}
    written = {}
    
    lang = find_lang(source, xml)

    path = Path(f'{dest}/{lang}')

    if not dest.exists():
        dest.mkdir()
    if not path.exists():
        path.mkdir()

    create_written(written, path)
    create_audio_info(speakers, lang, root, path)

    '''
    for name in os.listdir(path):
        if xml[xml.find('_')+1:-4] == name[:"_Set"]:
            filename = name
        else:
            filename = f"{xml.find('_')+1:-4}_Set"
    '''
    
    with open(f'{path}/{lang}_phono.txt', 'ab') as phonof, open(f'{path}/{lang}_ortho.txt', 'ab') as orthof, open(f'{path}/{lang}_undet.txt', 'ab') as undetf:
        sents = root.findall("S")
        
        #Three different processes for three different main formats of the xml files.
        if sents:
            for sent in sents:
                lines = []
                kinds = []
                process.process_sent(xml, sent, lines, kinds, get_info=False)
                update_audio_info(speakers, sent)
                update_files(written, lines, kinds, phonof, orthof, undetf)

        elif root.findall("W"):

            for word in root.findall("W"):
                lines = []
                kinds = []
                forms = word.findall("FORM")
                if forms:
                    #For each form, add the line to lines, and find the kind for the same index and add it to kinds.
                    for i, form in enumerate(forms):
                        if form.text is not None:
                            #line = word.attrib['id'] + audio_info(word) + " " + word.find("FORM").text + "\r\n"
                            line = process.strip_punc(form.text, after_info=False)
                            process.add_to_list(lines, line, i)
                            process.update_kinds(form, lines, kinds, i)
                    update_audio_info(speakers, word)
                    update_files(written, lines, kinds, phonof, orthof, undetf)

                '''
                elif word.find("TRANSL") is not None and word.find("TRANSL").text is not None:
                    line = strip_punc(xml[:-4] + "_" + word.attrib['id'] + " " + word.find("TRANSL").text) + '\r\n'
                    ids.append(line[:line.find(' ')])
                    outf.write(line.encode('utf-8'))
                ''' 
        elif root.find("Episode") is not None:
            logger.warning(f'{xml} char set failed.')
            logger.warning("Functionality for this type of files currently not working")
            return False
        else:
            lines = []
            kinds = []
            lines.append(process.strip_punc(root.find("FORM").text, after_info=False))
            process.update_kinds(root.find("FORM"), lines, kinds, 0)
            update_audio_info(speakers, root)
            update_files(written, lines, kinds, phonof, orthof, undetf)

    write_audio_info(speakers, lang, path)
    process.remove_empty_files(path, report=False)

def create_all_sets(source, dest):
    ''' Creates character sets and audio information to the dest folder, from the xml files in source folder. '''
    #Delete existing audio info so that previously written time values don't get added up when time is being recalculated.
    delete_audio_info(dest)
    for file in os.listdir(source):
        create_set(source, dest, file)

def main():
    logger.info("Creating character sets...")
    dest = Path('./Stats')
    source = Path('./Recordings_xml')
    create_all_sets(source, dest)
        
    logger.info("Character set creation complete.")
      
if __name__ == "__main__":
    main()
