import os
import fileinput
import collections
import time
assessmentTraingSet_path = "../Corpus/LISA/AssessmentTrainSet/suffix_from_01"
assessmentTraingSetDict = {}

def get_assessment():
	# 16 query documants
	for assessment_item in os.listdir(assessmentTraingSet_path):
		# join dir path and file name
		assessment_item_path = os.path.join(assessmentTraingSet_path, assessment_item)
		# check whether a file exists before read
		if os.path.isfile(assessment_item_path):
			with open(assessment_item_path, 'r') as f:
				# read content of query documant (doc, content)
				title = "query"
				#print('path: ', assessment_item_path)
				for line in f.readlines():
					#print('line: ', line)
					if "Query" in line.split():
						words = line.split()
						title = words[2]
						#print(title)
						assessmentTraingSetDict[title] = ""
					else:
						assessmentTraingSetDict[title] += line
						#print(assessmentTraingSetDict[title])

	return assessmentTraingSetDict

# result : list [(doc, point)]
# assessment_list : list [(doc)]
def precision(result, assessment_list):
        iterative = 0
        count = 0
        precision = 0
        assessment = assessment_list.split()
        #print(assessment)
        #print(result)
        for doc_name, point in result:
                iterative += 1
                if count == len(assessment): break

                if doc_name in assessment:
                        #print('found')
                        count += 1
                        precision += count * 1.0 / iterative

        precision /= len(assessment)
        #time.sleep(10000)
        return precision
