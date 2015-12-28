import csv
import codecs
import sys
reload(sys)
sys.setdefaultencoding("utf-8")  # This block helps write the csv in utf-8

try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

meta_csv = codecs.open('parsed_titles.txt', encoding='utf-8', mode='a') #append mode
meta_writer = csv.writer(meta_csv, delimiter="|", quotechar='"', escapechar='\\')

f = open("mentaldisorders.xml", 'r')

try:
        parser = ET.XMLParser(encoding='utf-8')
        tree = ET.parse(f, parser=parser)
finally:
        f.close()
        
root = tree.getroot()

for mcite in root.findall('./PubmedArticle/MedlineCitation'):

			# Set all variables to empty string at the beginning of each article to clear out previous values 
			pmid = publang = title = ypub = ''

			pmid = mcite.findtext('PMID')
			
			# can be multiple of this field; joining them into one with ";"
			lang_objs = mcite.findall('./Article/Language')
			if len(lang_objs) > 0:
				for item in lang_objs:
					 publang += (item.text + ';')
				               
			title = mcite.findtext('./Article/ArticleTitle')
			
			ypub = mcite.findtext('./Article/Journal/JournalIssue/PubDate/Year')
			if ypub is None:
				ypub = mcite.findtext('./Article/Journal/JournalIssue/PubDate/MedlineDate')[:4]

                        meta_writer.writerow((pmid, ypub, title, publang))
			
					 