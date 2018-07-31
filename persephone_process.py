import os
from lxml import etree as ElementTree
from pathlib import Path
from analyze import calc_time
from process import clean_up, find_nth_occ
import logging
from persephone.utterance import Utterance
from persephone.preprocess.wav import extract_wavs

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

def divide_phonemes(file, src, txt_dest, wav_dest):
    if not os.path.exists(txt_dest):
        os.makedirs(txt_dest)
    if not os.path.exists(wav_dest):
        os.makedirs(wav_dest)

    alpha = file[file.rfind('_')+1:file.find('.')]
    idx = file.find('_Processed')
    wav_name = file[:idx] + '.wav'
    xml_name = file[:idx] + '.xml'
    wav_path = Path('./Recordings_wav/' + wav_name)
    xml_path = Path('./Recordings_xml/'+ xml_name)

    utterances = []
        #new_file = f'{file[:idx]}_Phonemes{file[idx:]}'

    '''
    with open(f'{src}{file}', 'r', encoding='utf-8') as readf, open(f'{dest}{new_file}', 'w', encoding='utf-8') as writef:
        for line in readf:
            name = line[:line.find(' ')]
            trans = ''.join(line[line.find(' ')+1:].split())
            writef.write(name)
            for char in trans:
                writef.write(f' {char}')
            writef.write('\n')
    '''

    with open(src+file, 'r', encoding='utf-8') as readf:
        for line in readf:
            id_name = line[:line.find(' ')]
            name = id_name +'_'+alpha
            try:
                start = float(line[line.find('start=')+6:find_nth_occ(line, ' ', 2)])*1000
                end = float(line[line.find('end=')+4:find_nth_occ(line, ' ', 3)])*1000
            except ValueError:
                continue
            trans = line[find_nth_occ(line, ' ', 3)+1:]
            #Put whitespace between every char.
            trans = "".join(trans.split())
            trans = " ".join(trans)
            
            utter = Utterance(wav_path, xml_path, name, start, end, trans, "")
            utterances.append(utter)
            
            with open(txt_dest+utter.prefix+'.txt', 'w', encoding='utf-8') as writef:
                writef.write(utter.text + '\n')
            '''
            writef.write(name)
            for char in trans:
                writef.write(f' {char}')
            writef.write('\n')
            '''

    extract_wavs(utterances, Path('./'+wav_dest), False)
        
if __name__ == "__main__":
    src = "Processed/"
    txt_dest = "label/"
    wav_dest = "wav/"
    skip = ["ortho", "west_uvean", "wallisian", "tiri", "bwatoo", "cemuhi", "numee", "laz", "paici", "maore_comorian", "wayana", "ngazidja_comorian", "araki", "wetamut", "yucuna", "ajie", \
            "xaracuu", "xaragure", "dehu", "nelemwa", "nemi"]

    time = 0

    logger.info("Creating phoneme files...")
    
    for file in os.listdir(src):
        create = True
        for name in skip:
            if name in file.lower():
                create = False
                break
        if create:
            divide_phonemes(file, src, txt_dest, wav_dest)

            idx = file.find('_Processed')
            tree = ElementTree.parse('Recordings_xml/'+file[:idx]+'.xml')
            root = clean_up(tree.getroot())
            time += calc_time(root)
    '''
    with open(f'{dest}total_audio.txt', 'w') as outf:
        outf.write(f'Total audio in minutes: {time/60} mins')
    '''
    logger.info('Phoneme files created. Total audio in minutes:' + str(time/60) +' mins.')
