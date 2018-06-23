import urllib
import urllib.request
import requests
import sys
import argparse
from bs4 import BeautifulSoup

#Gets a list of URLs and returns the .wav URL.
def find_wav(urls):
    for url in urls:
        if url.find('.wav') != -1:
            return url
    return None

def find_xml(soup):
    for link in soup.find_all('a'):
        if link.get('href').encode('utf-8')[-4:] == ".xml".encode('utf-8'):
            return link.get('href')
    return None

def find_mp4(soup):
    for link in soup.find_all('a'):
        if link.get('href').encode('utf-8')[-4:] == ".mp4".encode('utf-8'):
            return link.get('href')
    return None

#Download the recording files from pangloss, given the url
def download_rec(url, lang, rec_num):
    url = "http://lacito.vjf.cnrs.fr/pangloss/corpus/" + url
    #site = urllib.request.urlopen(url)
    site = requests.get(url).content
    soup = BeautifulSoup(site, 'html.parser')

    urls = []

    for link in soup.find_all('source'):
        urls.append(link.get('src'))

    wav_url = find_wav(urls)

    xml_url = find_xml(soup)

    rec = "Recording" + str(rec_num + 1)

    sys.stdout.buffer.write("Downloading ".encode('utf-8') + lang + rec.encode('utf-8') + "...".encode('utf-8'))
    print()
    sys.stdout.flush()

    if xml_url is not None:
        urllib.request.urlretrieve(xml_url, lang.decode('utf-8') + "Recording" + str(rec_num + 1) + ".xml")
    else:
        mp4_url = find_mp4(soup)
        if mp4_url is not None:
            urllib.request.urlretrieve(mp4_url, lang.decode('utf-8') + "Recording" + str(rec_num + 1) + ".mp4")

    if wav_url is not None:
        urllib.request.urlretrieve(wav_url, lang.decode('utf-8') + "Recording" + str(rec_num + 1) + ".wav")

    #print(lang.decode('utf-8') + "Recording" + str(rec_num + 1) + " download complete.") 
    sys.stdout.buffer.write(lang + rec.encode('utf-8') + " download complete.".encode('utf-8'))
    print()
    sys.stdout.flush()


#Download all recording files for a given language's site.
def download_all_rec(lang, site):
    soup = BeautifulSoup(site, 'html.parser')

    urls = []

    #Find the URLs of all recordings.
    for link in soup.find_all('a'):
        if link.get('href') is not None and link.get('href').encode('utf-8').find('show_text'.encode('utf-8')) == 0:
            url = link.get('href')
            urls.append(url)

    for u in urls:
        download_rec(u, lang, urls.index(u))

    print("All downloads are complete.")

def download_lang(lang):

    #find = urllib.request.urlopen("http://lacito.vjf.cnrs.fr/pangloss/corpus/index_en.html")

    find = requests.get("http://lacito.vjf.cnrs.fr/pangloss/corpus/index_en.html").content

    soup_find = BeautifulSoup(find, 'html.parser')

    found = False
    
    #Finds the given language's website.
    for name in soup_find.find_all('a'):
        lang_name = name.text

        #Gets rid of parantheses for language names that include a description.
        if lang_name.find(" (") != -1:
            lang_name = lang_name[:lang_name.find(" (")]
            
        if lang_name.encode('utf-8') == lang:
            site = requests.get('http://lacito.vjf.cnrs.fr/pangloss/corpus/' + name.get('href')).content
            found = True
            break

    if not found:
        print("Language not found.")
        sys.exit(1)

    download_all_rec(lang, site)


def download_all_lang():
    #lang_list = urllib.request.urlopen("http://lacito.vjf.cnrs.fr/pangloss/corpus/index_en.html")

    lang_list = requests.get("http://lacito.vjf.cnrs.fr/pangloss/corpus/index_en.html").content

    soup_langs = BeautifulSoup(lang_list, 'html.parser')

    #Find all languages and download recordings.
    for link in soup_langs.find_all('a'):
        if link.get('href') is not None and link.get('href').encode('utf-8').find('list_rsc'.encode('utf-8')) == 0:
            lang = link.text.encode('utf-8')
            if lang[-1:] == "n".encode('utf-8'):
                site = requests.get("http://lacito.vjf.cnrs.fr/pangloss/corpus/" + link.get('href')).content
                download_all_rec(lang, site)
    

#START OF SCRIPT

parser = argparse.ArgumentParser()
parser.add_argument("language", type=str, help="language to download (all or specific)", nargs='*')
args = parser.parse_args()

lang = " ".join(args.language)

if lang.lower() == "all":
    download_all_lang()
else:
    lang = " ".join(args.language)
    download_lang(lang.encode('utf-8'))
