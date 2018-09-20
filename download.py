''' Script and functions to download xml and wav files of recordings, currently only from Pangloss. '''

import urllib.request
import sys
import argparse
import pycountry
from SPARQLWrapper import SPARQLWrapper, JSON
import time
import unidecode
import logging
from pathlib import Path

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

def download_lang(xml_dir, wav_dir, code):
    ''' Download xml files of the given language code to the given path. '''

    pangloss = Pangloss()

    recs = sparql_setup(pangloss)
    '''
    if not os.path.exists(xml_dir):
        os.makedirs(xml_dir)
    if not os.path.exists(wav_dir):
        os.makedirs(wav_dir)
    '''

    if not xml_dir.exists():
        xml_dir.mkdir()
    if not wav_dir.exists():
        wav_dir.mkdir()

    logger.info("Downloading...")

    for i, rec in enumerate(recs):
        rec_num = i+1
        xml_url = rec['textFile']['value']
        wav_url = rec['audioFile']['value']

        #Skip recording if not desired language
        if code != "all" and code != rec['lg']['value'][-3:]:
            continue

        lang = find_lang(rec['lg']['value'][-3:])
        
        xml_path = Path(f'{xml_dir}/Recording{rec_num}_{lang}.xml')
        wav_path = Path(f'{wav_dir}/Recording{rec_num}_{lang}.wav')
        #if os.path.exists(xml_path) and os.path.exists(wav_path):
        if xml_path.exists() and wav_path.exists():
            logger.info(f"Already found {xml_path} and {wav_path}")
            continue

        logger.info(f"Downloading {xml_path} and {wav_path}")

        #Continue trying to download until download succeeds.
        tries = 0
        while tries < 5:
            try:
                urllib.request.urlretrieve(xml_url, xml_path)
                time.sleep(0.5)
                urllib.request.urlretrieve(wav_url, wav_path)
                time.sleep(0.5)
            except urllib.error.URLError:
                logger.warn(f"""Failed to download
                                {xml_path} or {wav_path}.
                                Trying again; {tries} attempts.""")
                tries += 1
                continue
            break

    logger.info("All downloads are complete.")

def find_lang(code):
    ''' Finds and returns the language name, given the code. '''
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
    xml_dir = Path('./Recordings_xml')
    wav_dir = Path('./Recordings_wav')
    download_lang(xml_dir, wav_dir, code)
