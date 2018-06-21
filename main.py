import urllib
import urllib.request
import sys
from bs4 import BeautifulSoup

#Gets a list of URLs and returns the .wav URL.
def find_wav(urls):
    for url in urls:
        if url.find('.wav') != -1:
            return url

#Download the wav file from pangloss, given the url
def download_wav(url, lang, rec_num):
    url = "http://lacito.vjf.cnrs.fr/pangloss/corpus/" + url
    site = urllib.request.urlopen(url)
    soup = BeautifulSoup(site, 'html.parser')

    urls = []

    for link in soup.find_all('source'):
        urls.append(link.get('src'))

    wav_url = find_wav(urls)

    urllib.request.urlretrieve(wav_url, lang + "Recording" + str(rec_num + 1) + ".wav")


#START OF SCRIPT

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

print("Downloading...")
sys.stdout.flush()

soup = BeautifulSoup(site, 'html.parser')

urls = []

#Find the URLs of all recordings.
for link in soup.find_all('a'):
    if link.get('href') is not None and link.get('href').encode('utf-8').find('show_text'.encode('utf-8')) == 0:
        url = link.get('href')
        urls.append(url)

for u in urls:
    download_wav(u, lang, urls.index(u))

print("Download is complete.")
