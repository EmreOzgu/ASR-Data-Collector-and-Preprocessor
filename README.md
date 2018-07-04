# Pangloss-Scraper
A Python script to download the recording xml files of a given language or all languages for ASR training, currently only from http://lacito.vjf.cnrs.fr/pangloss/index_en.html.

main.py requires the installation of [SPARQLWrapper.](https://github.com/RDFLib/sparqlwrapper)

analyze.py looks at the xml files in the Recordings file in the same directory as analyze.py and reports the percentage of IPA/Non-IPA transcriptions and total amount of data in minutes.
