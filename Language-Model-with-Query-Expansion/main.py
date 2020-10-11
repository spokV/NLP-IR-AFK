import os
import fileinput
import collections
from math import log
import operator
import numpy as np
import readAssessment
import ProcDoc
import Expansion

documant_path = "../Corpus/TDT2/SPLIT_DOC_WDID_NEW"
query_path = "../Corpus/TDT2/QUERY_WDID_NEW"
data = {}				# content of document (doc, content)
background_word = {}	# word count of 2265 documant (word, number of words)
query = {}				# query
my_lambda = 0.5

# list all files of a directory(Document)
for dir_item in os.listdir(documant_path):
	# join dir path and file name
    dir_item_path = os.path.join(documant_path, dir_item)
	# check whether a file exists before read
    if os.path.isfile(dir_item_path):
        with open(dir_item_path, 'r') as f:
			# read content of document (doc, content)
            data[dir_item] = f.read()

# 16 query documants
for query_item in os.listdir(query_path):
	# join dir path and file name
    query_item_path = os.path.join(query_path, query_item)
	# check whether a file exists before read
    if os.path.isfile(query_item_path):
        with open(query_item_path, 'r') as f:
			# read content of query documant (doc, content)
            query[query_item] = f.read()
			
# count background_word
for key, value in data.items():
	background_word = ProcDoc.word_count(value, dict(background_word))

for key, value in query.items():
	background_word = ProcDoc.word_count(value, dict(background_word))
	
background_word_sum = ProcDoc.word_sum(background_word)
#background_word = sorted(background_word.items(), key=lambda x: x[1], reverse=True)
#{k: v for k, v in sorted(background_word.items(), key=lambda item: item[1])}
#print(background_word)
# doc preprocess
[data_tf, data] = ProcDoc.doc_preprocess(data)

# query preprocess
query = ProcDoc.query_preprocess(query)
query_word_count = {}
for q, q_content in query.items():
	query_word_count[q] = ProcDoc.word_count(q_content, {})	

feedback_model = []
# query process
assessment = readAssessment.get_assessment()
lambda_test = {0: 0}
interval	= 0.1
isBreak = "run"
while isBreak != "exit":
	isWrite = True
	store_docs_point_list = {}
	for my_lambda in np.arange(0.2, 1.0, interval):
		docs_point = {}
		AP = 0
		mAP = 0
		for q_key, q_w_wc in query_word_count.items():
			for doc_key, doc_words_prob in data.items():
				point = 0
				# calculate each query value for the document
				for query_word, q_word_count in q_w_wc.items():
					count = 0						# C(w , D)
					word_probability = 0			# P(w | D)
					background_probability = 0		# BG(w | D)
					# check if word at query exists in the document
					if query_word in doc_words_prob:
						word_probability = doc_words_prob[query_word]
					'''					
					if query_word in background_word:
						background_probability = (background_word[query_word] + 0.01) / (background_word_sum +0.01)
					else:	
						background_probability = 0.01 / (background_word_sum + 0.01)
					'''	
					background_probability = (background_word[query_word] + 0.01) / (background_word_sum +0.01)		
					point += q_word_count * log(my_lambda * word_probability + (1 - my_lambda ) * background_probability)
				docs_point[doc_key] = point
			if len(feedback_model) == 0:
				# sorted each doc of query by point
				docs_point_list = sorted(docs_point.items(), key=operator.itemgetter(1), reverse = True)
				# write ranking result to file
				Expansion.outputRank(q_key, docs_point_list, isWrite)
			# store ranking result
			store_docs_point_list[q_key] = docs_point_list
			if isWrite == True:
				isWrite = False
			AP += readAssessment.precision(docs_point_list, assessment[q_key])
			# mean average precision	
		mAP = AP / len(query)
		print(my_lambda)
		print(mAP)
		lambda_test[my_lambda] = mAP
	# get key with maximum value in lambda_test dictionary	
	max_lambda = max(lambda_test.items(), key=operator.itemgetter(1))[0]
	max_mAP = lambda_test[my_lambda]
	'''
	# print Lambda and Max value
	print "Max:"
	print max_lambda, max_mAP
	'''
	isBreak = input("exit ?\n")
	if (isBreak == "query_ex"):
		top_rank = int(input("docs ?"))
		[query_word_count, feedback_model] = Expansion.extQueryModel(dict(query_word_count), dict(store_docs_point_list), dict(data_tf), list(feedback_model), top_rank)
