import os
from shutil import copyfile
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

def file_phono(file):
    ''' Returns true if file seems to contain ipa specific chars. '''
    ipa = ['ɲ', 'ŋ', 'ʰ', 'ʌ', 'æ', 'ᵐ', 'ʃ', 'ʊ', 'ᵑ', 'ː', 'ⁿ', 'ʉ', 'ɟ', 'ɨ', 'ħ', 'ʧ', 'ɹ', 'ɖ', 'ɽ', 'ɱ', 'ʐ', 'ʈ', 'ʔ', 'ɔ', 'ʒ', 'ɛ', 'ˀ', 'ɟ', 'ð', 'ʲ', 'ɣ', \
           'ɑ', '˧', 'ʝ', 'ɕ', 'ʐ', 'ɭ', 'ɬ', 'ɗ', 'ʎ', 'ɕ', 'ɤ']
    total = ""
    found = []
    
    for line in file:
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
    written = []
    with open(old_file, 'a+', encoding='utf8') as origf, open(add_file, 'r', encoding=('utf-8')) as addf:
        for line in origf:
            written.append(line.rstrip('\n'))
        for line in addf:
            char = line.rstrip('\n')
            if char not in written:
                origf.write(char + '\n')
        

def classify_undet(src):
    ''' Classifies undet preprocessed.txt files in src directory '''
    phono = False
    new_name = ""
    
    for file in os.listdir(src):
        if file.endswith('undet.txt'):
            with open(f'{src}{file}', 'r', encoding='utf-8') as undetf:
                phono = file_phono(undetf)
                
            if phono:
                new_name = f"{file[:file.find('undet.txt')]}phono.txt"
                
                if os.path.isfile(f'{src}{new_name}'):
                    add_on(f'{src}{new_name}', f'{src}{file}')
                else:   
                    os.rename(f"{src}{file}", f"{src}{new_name}")
            else:
                new_name = f"{file[:file.find('undet.txt')]}ortho.txt"
                
                if os.path.isfile(f'{src}{new_name}'):
                    add_on(f'{src}{new_name}', f'{src}{file}')
                    os.remove(f'{src}{file}')
                else:
                    os.rename(f"{src}{file}", f"{src}{new_name}")
        
        
           

if __name__ == "__main__":
    src = "Processed/"
    logger.info("Classifying undet.txt files...")
    classify_undet(src)
    src = "Stats/"
    for folder in os.listdir(src):
        classify_undet(f'{src}{folder}/')
    logger.info("Done")
