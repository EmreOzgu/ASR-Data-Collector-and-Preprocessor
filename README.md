# ASR Data Scraper
A Python script to download the recording xml files of a given language or all languages for ASR training, currently only from http://lacito.vjf.cnrs.fr/pangloss/index_en.html.

Running download.py will dump the xml files in the folder "Recordings/" located at the same directory as the script. analyze.py looks at the xml files in "Recordings/" and reports the percentage of IPA/Non-IPA transcriptions and total amount of data in minutes. process.py processes the xml files in "Recordings/" into a .txt in "Processed/".

download.py requires the installation of [SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper), [pycountry](https://pypi.org/project/pycountry/), and [Unidecode](https://pypi.org/project/Unidecode/).

analyze.py looks at the xml files in the Recordings file in the same directory as analyze.py and reports the percentage of IPA/Non-IPA transcriptions and total amount of data in minutes.
