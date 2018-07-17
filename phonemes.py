import os

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

for file in os.listdir(src):
    create = True
    for name in skip:
        if name in file.lower():
            create = False
            break
    if create:
        divide_phonemes(file, src, dest)
