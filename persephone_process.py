''' Divides all xml and wav recordings into small utterances that Persephone can process. '''
import os
from lxml import etree as ElementTree
from pathlib import Path
from analyze import calc_time
from process import clean_up, find_nth_occ
import logging
#from persephone.persephone.utterance import Utterance
#from persephone.persephone.preprocess.wav import extract_wavs
from persephone import Utterance, extract_wavs

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

def divide_phonemes(file, src, txt_dest, wav_dest):
    if not txt_dest.exists():
        txt_dest.mkdir()
    if not wav_dest.exists():
        wav_dest.mkdir()

    alpha = file[file.rfind('_')+1:file.find('.')]
    idx = file.find('_Processed')
    wav_name = f'{file[:idx]}.wav'
    xml_name = f'{file[:idx]}.xml'
    wav_path = Path(f'./Recordings_wav/{wav_name}')
    xml_path = Path(f'./Recordings_xml/{xml_name}')

    utterances = []
    
    with open(f'{src}/{file}', 'r', encoding='utf-8') as readf:
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
            
            with open(f'{txt_dest}/{utter.prefix}.txt', 'w', encoding='utf-8') as writef:
                writef.write(utter.text + '\n')

    extract_wavs(utterances, wav_dest, False)
        
if __name__ == "__main__":
    src = Path('./Processed/')
    txt_dest = Path('./label/')
    wav_dest = Path('./wav/')
    #Languages that we decided to skip testing in Persephone right now. We're starting out with pure ipa languages.
    skip = ["ortho", "west_uvean", "wallisian", "tiri", "bwatoo", "cemuhi", "numee", "laz", "paici", \
            "maore_comorian", "wayana", "ngazidja_comorian", "araki", "wetamut", "yucuna", "ajie", \
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
            tree = ElementTree.parse(f'Recordings_xml/{file[:idx]}.xml')
            root = clean_up(tree.getroot())
            time += calc_time(root)
            
    logger.info(f'Phoneme files created. Total audio in minutes:{time/60} mins.')
