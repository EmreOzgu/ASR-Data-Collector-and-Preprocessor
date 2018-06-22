import urllib
import urllib.request
import requests
import sys
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

#Download the recording files from pangloss, given the url
def download_rec(url, lang, rec_num):
    url = "http://lacito.vjf.cnrs.fr/pangloss/corpus/" + url
    site = urllib.request.urlopen(url)
    soup = BeautifulSoup(site, 'html.parser')

    urls = []

    for link in soup.find_all('source'):
        urls.append(link.get('src'))

    wav_url = find_wav(urls)

    xml_url = find_xml(soup)

    print("Downloading " + lang.decode('utf-8') + "Recording" + str(rec_num + 1) + "...")
    sys.stdout.flush()

    if xml_url is not None:
        urllib.request.urlretrieve(xml_url, lang.decode('utf-8') + "Recording" + str(rec_num + 1) + ".xml")

    if wav_url is not None:
        urllib.request.urlretrieve(wav_url, lang.decode('utf-8') + "Recording" + str(rec_num + 1) + ".wav")

    print(lang.decode('utf-8') + "Recording" + str(rec_num + 1) + " download complete.") 

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

def download_lang():
    lang = input("Enter language: ").capwords()

    find = urllib.request.urlopen("http://lacito.vjf.cnrs.fr/pangloss/corpus/index_en.html")

    soup_find = BeautifulSoup(find, 'html.parser')

    found = False

    #Finds the given language's website.
    for name in soup_find.find_all('a'):
        if name.text.encode('utf-8') == lang.encode('utf-8'):
            site = urllib.request.urlopen('http://lacito.vjf.cnrs.fr/pangloss/corpus/' + name.get('href'))
            found = True
            break

    if not found:
        print("Language not found.")
        sys.exit(1)

    download_all_rec(lang.encode('utf-8'), site)


def download_all_lang():
    lang_list = urllib.request.urlopen("http://lacito.vjf.cnrs.fr/pangloss/corpus/index_en.html")

    soup_langs = BeautifulSoup(lang_list, 'html.parser')

    #Find all languages and download recordings.
    for link in soup_langs.find_all('a'):
        if link.get('href') is not None and link.get('href').encode('utf-8').find('list_rsc'.encode('utf-8')) == 0:
            lang = link.text.encode('utf-8')
            #sys.stdout.buffer.write(lang)
            if lang[-1:] == "n".encode('utf-8'):
                site = requests.get("http://lacito.vjf.cnrs.fr/pangloss/corpus/" + link.get('href')).content
                #site = urllib.request.urlopen("http://lacito.vjf.cnrs.fr/pangloss/corpus/" + link.get('href'))
                download_all_rec(lang, site)
    

#START OF SCRIPT

print("Download recordings for a specific language or all languages?")
print("s - specific")
print("a - all")

choice = ''

while choice != 's' and choice != 'a':
    choice = input("Choice: ")

if choice == 's':
    download_lang()
elif choice == 'a':
    download_all_lang()

    
'''
lang = input("Enter language: ").title()

find = urllib.request.urlopen("http://lacito.vjf.cnrs.fr/pangloss/corpus/corpora_list_en.php")

soup_find = BeautifulSoup(find, 'html.parser')

found = False

#Finds the given language's website.
for name in soup_find.find_all('b'):
    if name.encode('utf-8').find(lang.encode('utf-8')) != -1:
        site = urllib.request.urlopen('http://lacito.vjf.cnrs.fr/pangloss/corpus/' + name.a.get('href'))
        found = True
        break

if not found:
    print("Language not found.")
    sys.exit(1)
'''


'''
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
'''
