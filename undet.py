import os
from shutil import copyfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

def transcript_phono(transcript):
    ''' Returns true if file/string/list of strings seems to contain ipa specific chars. '''
    ipa = ['ɲ', 'ŋ', 'ʰ', 'ʌ', 'æ', 'ᵐ', 'ʃ', 'ʊ', 'ᵑ', 'ː', 'ⁿ', 'ʉ', 'ɟ', 'ɨ', 'ħ', 'ʧ', 'ɹ', 'ɖ', 'ɽ', 'ɱ', 'ʐ', 'ʈ', 'ʔ', 'ɔ', 'ʒ', 'ɛ', 'ˀ', 'ɟ', 'ð', 'ʲ', 'ɣ', \
           'ɑ', '˧', 'ʝ', 'ɕ', 'ʐ', 'ɭ', 'ɬ', 'ɗ', 'ʎ', 'ɕ', 'ɤ']
    total = ""
    found = []
    
    for line in transcript:
        total += "".join(line.split())

    num = 0

    for char in total:
        if char in ipa and char not in found:
            num += 1
            found.append(char)
        if num == 4:
            return True
    return False
            
def add_on(old_file, add_file):
    ''' Reads the characters in the old_file and adds the characters in the add_file that aren't in the old_file. '''
    written = []
    with open(old_file, 'a+', encoding='utf8') as origf, open(add_file, 'r', encoding=('utf-8')) as addf:
        for line in origf:
            written.append(line.rstrip('\n'))
        for line in addf:
            char = line.rstrip('\n')
            if char not in written:
                origf.write(char + '\n')
        
def edit(src, file, new_name, add):
    '''After classifying undetermined char files, add on to existing types (phono/ortho) if add=True, or create a new file. '''
    if os.path.isfile(f'{src}/{new_name}'):
        if add:
            add_on(f'{src}/{new_name}', f'{src}/{file}')
        os.remove(f'{src}/{file}')
    else:   
        os.rename(f"{src}/{file}", f"{src}/{new_name}")

def classify_undet(src, add=False):
    ''' Classifies undet preprocessed.txt files in src directory. If is_char=True, then it will also add the char list of undet file to an existing file '''
    phono = False
    new_name = ""
    
    for file in os.listdir(src):
        if file.endswith('undet.txt'):
            with open(f'{src}/{file}', 'r', encoding='utf-8') as undetf:
                phono = transcript_phono(undetf)
                
            if phono:
                new_name = f"{file[:file.find('undet.txt')]}phono.txt"
                edit(src, file, new_name, add)
            else:
                new_name = f"{file[:file.find('undet.txt')]}ortho.txt"
                edit(src, file, new_name, add)
        
def main():        
    src = Path('./Processed')
    logger.info("Classifying undet.txt files...")
    classify_undet(src)
    src = Path('./Stats')
    for folder in os.listdir(src):
        classify_undet(Path(f'{src}/{folder}/'), add=True)
    logger.info("Done")

if __name__ == "__main__":
    main()
