import os
from lxml import etree as ElementTree
from analyze import calc_time
from process import clean_up

def divide_phonemes(file, src, dest):
    if not os.path.exists(dest):
        os.makedirs(dest)

    idx = file.rfind('_')
    new_file = f'{file[:idx]}_Phonemes{file[idx:]}'

    with open(f'{src}{file}', 'r', encoding='utf-8') as readf, open(f'{dest}{new_file}', 'w', encoding='utf-8') as writef:
        for line in readf:
            name = line[:line.find(' ')]
            trans = ''.join(line[line.find(' ')+1:].split())
            writef.write(name)
            for char in trans:
                writef.write(f' {char}')
            writef.write('\n')
        

src = "Processed/"
dest = "Phonemes/"
skip = ["ortho", "west_uvean", "wallisian", "tiri", "bwatoo", "cemuhi", "numee", "laz", "paici", "maore_comorian", "wayana", "ngazidja_comorian", "araki", "wetamut", "yucuna", "ajie", \
        "xaracuu", "xaragure", "dehu", "nelemwa", "nemi"]

time = 0

for file in os.listdir(src):
    create = True
    for name in skip:
        if name in file.lower():
            create = False
            break
    if create:
        divide_phonemes(file, src, dest)

        idx = file.find('_Processed')
        tree = ElementTree.parse(f'Recordings/{file[:idx]}.xml')
        root = clean_up(tree.getroot())
        time += calc_time(root)

with open(f'{dest}total_audio.txt', 'w') as outf:
    outf.write(f'Total audio in minutes: {time/60} mins')
