import sys
import nltk
import csv
import ast
from operator import itemgetter
import random

stopwords = nltk.corpus.stopwords.words('english')

disorder_phrases = {}

DICTIONARY_FILE = 'mental diseases dictionary.csv'

try:
	TITLES_FILE = 'parsed_titles.txt' 
except IndexError: 
	print "\nERROR: No file name given. Please add the filename of the titles file; e.g.,:\n\n"   
	sys.exit(0)

#parse target mental disorder phrases, but keep original version of phrase

with open(DICTIONARY_FILE, 'rb') as csvfile:
	dictreader = csv.reader(csvfile, delimiter='\t')
	for row in dictreader:
		#print row
		term_words = [w.lower() for w in nltk.RegexpTokenizer(r'\w+').tokenize(row[0])]
		for word in term_words:
			#print word
			if word in stopwords:
				term_words.remove(word)
		disorder_phrases[row[0]] = term_words

#print disorder_phrases

with open(TITLES_FILE, 'rb') as csvfile:
	file_id = str(random.randint(1,99999)) # add a random number to filenames to make them unique
	with open('tagging_titles_' + file_id + '.txt', 'wb') as pubfile:
		titlesreader = csv.reader(csvfile, delimiter='|', escapechar='\\')

		recordwriter = csv.writer(pubfile, delimiter='|', quotechar='"', escapechar='\\')
		recordwriter.writerow(["pmid","pubyear","lang","title","match_found","best_full_match","best_window_match"])

		'''
		run through titles in file
		file format is "pmid|year|title|language"
		'''
		for row in titlesreader:

			title = ''
			match_found = ''
			best_full_match = ''
			best_window_match = ''
		
			pmid = row[0]
			pubyear = row[1]
			title = row[2] #third column of original file
			lang = row[3]
			print title

			#split and tokenize the title
			title_words = [w.lower() for w in nltk.RegexpTokenizer(r'\w+').tokenize(title)]
		
			full_title_scores = {}
			small_window_scores = {}

			# test paper titles for each word of disorder phrase from dictionary
			# keep scores for all disorder phrases

			for phrase in disorder_phrases:
				word_matches = {}
				for word in disorder_phrases[phrase]:

					'''
					for each word in disorder phrase, find the index of that word in the title
					'''
					indexes = [i for i, j in enumerate(title_words) if j == word]

					'''
					if word was found at least once, keep track of it and the indexes
					'''

					if len(indexes) > 0:
						word_matches[word] = indexes

					'''
					if found as many words in the title as started with
					in the disorder phrase, keep it as at least a "full title"
					match, and possibly also a "within window" match
					'''

				if len(word_matches) == len(disorder_phrases[phrase]):
					print "potential match (all words found in title):", phrase
					
					full_title_scores[phrase] = len(disorder_phrases[phrase])
				
					'''
					if phrase is only one word long, it also counts as a small_window_match
					'''
					if len(disorder_phrases[phrase]) == 1:
							small_window_scores[phrase] = len(disorder_phrases[phrase])
							print "single word phrase; stored!"
					else:
						'''
						if phrase is longer than one word, find min and max indexes
						by sorting the matched words by the indexes (in descending
						order), then taking the first and last elements
						'''
						sorted_word_matches = sorted(word_matches.items(), key=itemgetter(1), reverse=True)
						max_index = sorted_word_matches[0][1][0] #first index value of first element
						min_index = sorted_word_matches[-1][1][0] #first index value of last element
						'''
						if difference between max and min index is no more than 2
						more than the length of the original phrase (that is, if there
						are no more than 2 additional words intermingled in the disorder
						phrase words), count it as a match
						'''
						if (max_index - min_index) <= len(disorder_phrases[phrase]) + 2:
							small_window_scores[phrase] = len(disorder_phrases[phrase])
							print "in window!"
						else:
							print "not in window!"

			'''
			Take all of the potential "full title" and "small window" matches.
			If more than one match has been found in either category, sort
			the matches by the length of the phrase, and take the longest phrase
			as the best match.
			'''
			if len(full_title_scores) > 0 and len(small_window_scores) > 0:
				match_found = 'Y'
				print "all phrases checked; testing for best one"
				if len(full_title_scores) == 1:
			        	best_full_match = full_title_scores.keys()[0]
					print "only one full match:", best_full_match
				else:
					sorted_full_scores = sorted(full_title_scores.items(), key=itemgetter(1), reverse=True)
					best_full_match = sorted_full_scores[0][0]
					print "found best full match:", best_full_match
					#but need to check if first and second are tied
				if len(small_window_scores) == 1:
					best_window_match = small_window_scores.keys()[0]
					print "only one window match:", best_window_match
				else:
					sorted_window_scores = sorted(small_window_scores.items(), key=itemgetter(1), reverse=True)
					best_window_match = sorted_window_scores[0][0]
					print "found best window match:", best_window_match
					#but need to check if first and second are tied
			        			
		        else:
		        	print "no matches found."
		        	match_found = 'N'
		        recordwriter.writerow([pmid,pubyear,lang,title,match_found,best_full_match,best_window_match])	