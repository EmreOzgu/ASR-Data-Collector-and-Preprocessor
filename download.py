import urllib.request
import sys
import argparse
import pycountry
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import time
import unidecode

class Pangloss:
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


#Download recordings for all of the languages available.
def download_lang(code):

    pangloss = Pangloss()

    recs = sparql_setup(pangloss)

    path = "Recordings/"

    if not os.path.exists(path):
        os.makedirs(path)

    #Tracking previous download to prevent copies of files.
    prev = ""

    print("Downloading...")
    sys.stdout.flush()

    rec_num = 1

    for rec in recs:
        xml_url = rec['textFile']['value']
        
        if code != "all" and code != rec['lg']['value'][-3:]:
            continue
        
        if xml_url != prev:
            lang = find_lang(rec['lg']['value'])

            #Continue trying to download until download succeeds.
            while True:
                try:
                    urllib.request.urlretrieve(xml_url, path + "Recording" + str(rec_num) + '-' + lang + ".xml")
                    time.sleep(0.5)
                except urllib.error.URLError:
                    continue
                break

            prev = xml_url
            rec_num += 1

#Finds and returns the language name, given the code.            
def find_lang(link):
    code = link[-3:]
    return unidecode.unidecode(pycountry.languages.get(alpha_3=code).name)

#Setup a sparql query, given a site object.
def sparql_setup(site):
    sparql = SPARQLWrapper(site.endp())
    sparql.setQuery(site.query())
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()["results"]["bindings"]

    return results


#START OF SCRIPT

parser = argparse.ArgumentParser()
parser.add_argument("language", type=str, help="Language to download (all or specific ISO 693-3 code)")
args = parser.parse_args()                

code = args.language.lower()

download_lang(code)

print("All downloads are complete.")
