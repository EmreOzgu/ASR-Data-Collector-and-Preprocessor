from xml.etree import ElementTree
import argparse
import os

def process_file(xml):

    path = "Processed/"

    if not os.path.exists(path):
        os.makedirs(path)
    
    tree = ElementTree.parse("Recordings/" + xml)
    root = tree.getroot()

    with open("Processed/" + xml[:-4] + "-Processed.txt", 'wb') as outf:

        for sent in root.findall("S"):
            
            line = sent.attrib['id']

            audio = sent.find("AUDIO")

            if audio is not None:
                line += " start=" + audio.attrib['start'] + " " + "end=" + audio.attrib['end']

            for word in sent.findall('W'):
                
                utter = word.find("FORM").text

                if utter is not None:
                    line += " " + utter

                else:
                    line += " "
                    
                    for morph in word:
                        line += morph.find("FORM").text

            line += '\r\n'
            outf.write(line.encode('utf-8'))

            




#START OF SCRIPT

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="XML file name in Recordings/ to process (all or specific)")
args = parser.parse_args()

if args.filename.lower() == "all":
    for file in os.listdir("Recordings/"):
        process_file(file)
else:
    process_file(args.filename)
