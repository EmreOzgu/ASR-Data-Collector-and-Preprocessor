from chars import find_lang
from process import clean_up, find_nth_occ
import os

def find_total_time(readf):
    result = 0
    for line in readf:
        try:
            start = float(line[line.find('start=')+6:find_nth_occ(line, ' ', 2)])
            end = float(line[line.find('end=')+4:find_nth_occ(line, ' ', 3)])
        except ValueError:
            continue
        result += end - start
    return result

def write_audio_info(dest, audio_info):
    for lang in audio_info:
        with open(f'{dest}{lang}/{lang}_audio.txt', 'a', encoding='utf-8') as writef:
            for kind in audio_info[lang]:
                writef.write(f'{kind}={audio_info[lang][kind]/60} mins\n')

def collect_audio_info(src, xml_src, file, audio_info):
    xml = f'{file[:file.find("_Processed")]}.xml'
    lang = find_lang(xml_src, xml)
    kind = file[file.rfind('_')+1:file.find('.txt')]
    total_time = 0

    if lang not in audio_info:
        audio_info[lang] = {}

    with open(f'{src}{file}', 'r', encoding='utf-8') as readf:
        total_time += find_total_time(readf)

    if total_time:
        if kind in audio_info[lang]:
            audio_info[lang][kind] += total_time
        else:
            audio_info[lang][kind] = total_time
        

if __name__ == "__main__":
    src = "Processed/"
    dest = "Stats/"
    xml_src = "Recordings_xml/"
    audio_info = {}
    written = []
    for file in os.listdir(src):
        collect_audio_info(src, xml_src, file, audio_info)
    write_audio_info(dest, audio_info)
