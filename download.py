''' Script and functions to download xml files of recordings, currently only from Pangloss. '''

import urllib.request
import sys
import argparse
import pycountry
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import time
import unidecode
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(name)s:%(message)s', level=logging.INFO)

class Pangloss:
        ''' Class to keep endpoints and queries from pangloss constant and reachable. '''
        
        def endp(self):
            return "https://cocoon.huma-num.fr/sparql"

        def query(self):
            return """
                PREFIX edm: <http://www.europeana.eu/schemas/edm/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX dc: <http://purl.org/dc/elements/1.1/> 
                PREFIX dcterms: <http://purl.org/dc/terms/> 
                PREFIX ebucore: <http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#>

                SELECT DISTINCT ?audioFile ?textFile ?lg ?cho WHERE {
                    ?aggr edm:aggregatedCHO  ?cho .
                    ?cho a edm:ProvidedCHO.
                    ?cho dc:subject ?lg FILTER regex(str(?lg), "^http://lexvo.org/id/iso639-3/")
                    ?cho edm:isGatheredInto <http://cocoon.huma-num.fr/pub/COLLECTION_crdo-COLLECTION_LACITO> .
                    ?cho  dcterms:accessRights "Freely available for non-commercial use" .
                    
                    ?aggr edm:hasView ?transcript .
                    ?transcript  dcterms:conformsTo <http://cocoon.huma-num.fr/pub/CHO_crdo-dtd_archive> .
                    ?transcript foaf:primaryTopic ?textFile .

                    ?aggr edm:hasView ?recording .
                    ?recording ebucore:sampleRate "22050" .
                    ?recording foaf:primaryTopic ?audioFile .
                }
                """

def download_lang(path_xml, path_wav, code):
    ''' Download xml files of the given language code to the given path. '''

    pangloss = Pangloss()

    recs = sparql_setup(pangloss)

    if not os.path.exists(path_xml):
        os.makedirs(path_xml)
    if not os.path.exists(path_wav):
        os.makedirs(path_wav)

    #prev = ""
    
    logger.info("Downloading...")

    rec_num = 1

    for rec in recs:
        xml_url = rec['textFile']['value']
        wav_url = rec['audioFile']['value']

        #Skip recording if not desired language
        if code != "all" and code != rec['lg']['value'][-3:]:
            continue
           
        #if xml_url != prev:
    
    lang = find_lang(rec['lg']['value'])

    #Continue trying to download until download succeeds.
    while True:
        try:
            urllib.request.urlretrieve(xml_url, f'{path}Recording{rec_num}_{lang}.xml')
            time.sleep(0.5)
            urllib.request.urlretrieve(wav_url, f'{path_wav}Recording{rec_num}_{lang}.wav')
            time.sleep(0.5)
        except urllib.error.URLError:
            continue
        break
    #prev = xml_url
    
    rec_num += 1

    logger.info("All downloads are complete.")
          
def find_lang(link):
    ''' Finds and returns the language name, given the code. '''
    code = link[-3:]
    return unidecode.unidecode(pycountry.languages.get(alpha_3=code).name).replace(' ', '_').replace('-', '_')

def sparql_setup(site):
    ''' Setup a sparql query, given a site object. '''
    sparql = SPARQLWrapper(site.endp())
    sparql.setQuery(site.query())
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()["results"]["bindings"]

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language", type=str, help="Language to download (all or specific ISO 693-3 code)")
    args = parser.parse_args()                

    code = args.language.lower()
    path_xml = "Recordings_xml/"
    path_wav = "Recordings_wav/"
    download_lang(path_xml, path_wav, code)
