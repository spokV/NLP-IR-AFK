#!/usr/bin/env python
import numpy as np
import sys
sys.path.append("../Tools")

import ProcDoc
import Evaluate
import RelevanceModel as RM3
import logging
from CommonPath import CommonPath  
import argparse
import math
import os
import time

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser()

## Required parameters
parser.add_argument("--is_training",
                     default="False",
                     type=str2bool,
                     required=False)

parser.add_argument("--is_short",
                     default="False",
                     type=str2bool,
                     required=False)

parser.add_argument("--is_spoken",
                     default="False",
                     type=str2bool,
                     required=False)

parser.add_argument("--alpha",
                     default="0.8",
                     type=float,
                     required=False)

parser.add_argument("--beta",
                     default="0.4",
                     type=float,
                     required=False)

args = parser.parse_args()
is_training = args.is_training
is_short = args.is_short
is_spoken = args.is_spoken

alpha = args.alpha
beta = args.beta

path = CommonPath(is_training, is_short, is_spoken)
log_filename = path.getLogFilename()
qry_path = path.getQryPath()
doc_path = path.getDocPath()
rel_path = path.getRelPath()

dict_path = path.getDictPath()
bg_path = path.getBGPath()

print("Relevance-Model")
logging.basicConfig(filename=log_filename, format="%(asctime)s %(levelname)s:%(message)s", 
                    level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger().setLevel(logging.INFO)

# Read relevant set for queries and documents
eval_mdl = Evaluate.EvaluateModel(rel_path, is_training)
rel_set = eval_mdl.getAset()

# Preprocess
qry_file = ProcDoc.readFile(qry_path)
doc_file = ProcDoc.readFile(doc_path)

# Term Frequency
qry_mdl_dict = ProcDoc.qryPreproc(qry_file, rel_set)
doc_mdl_dict = ProcDoc.docPreproc(doc_file)

# Unigram
qry_unimdl_dict = ProcDoc.unigram(qry_mdl_dict)
doc_unimdl_dict = ProcDoc.unigram(doc_mdl_dict)

# Convert dictionary to numpy array (feasible to compute)
qry_mdl_np, qry_IDs = ProcDoc.dict2npSparse(qry_unimdl_dict)
doc_mdl_np, doc_IDs = ProcDoc.dict2npSparse(doc_unimdl_dict)


############################################
def word_sum(data):
    num = 0
    for key, value in data.items():
        num += int(value)
        return num

data = {}
background_word = {}

for key, value in doc_mdl_dict.items():
    for key1, value1 in value.items():
        if key1 in background_word:
            background_word[key1] += value1
        else:
            background_word[key1] = value1
        #print(key1, value1, background_word)
        #print('--')
    #time.sleep(5)
    #background_word = ProcDoc.wordCount(value, dict(background_word))

background_word_sum = word_sum(background_word)
#print('len bg word: ', len(background_word))
bg_mdl_np = np.zeros(51253)
bg_mdl_np += 0.00001
for key in background_word:
    #print(background_word[key])
    #prob = math.exp(float(background_word[key]/background_word_sum))
    prob = float(background_word[key]/background_word_sum)
    bg_mdl_np[key] = prob

#print('bg np shape: ', bg_mdl_np.shape)
#print(bg_mdl_np)
#bg_mdl_np = qry_mdl_np.copy()#ProcDoc.readBGnp(bg_path)

# Smoothing
for doc_idx in range(doc_mdl_np.shape[0]):
    doc_mdl_np[doc_idx] = (1-alpha) * doc_mdl_np[doc_idx] + alpha * bg_mdl_np

# Smoothing
for qry_idx in range(qry_mdl_np.shape[0]):
    qry_mdl_np[qry_idx] = (1-beta) * qry_mdl_np[qry_idx] + beta * bg_mdl_np

# KL divergence
results = np.argsort(-np.dot(qry_mdl_np, np.log(doc_mdl_np.T)), axis = 1)

# fisrt stage retrieval
print("Fisrt stage retrieval")
qry_docs_ranking = {}
for q_idx, q_ID in enumerate(qry_IDs):
    docs_ranking = []
    for doc_idx in results[q_idx]:
        docs_ranking.append(doc_IDs[doc_idx])
    qry_docs_ranking[q_ID] = docs_ranking

#eval_mdl = EvaluateModel(rel_path, isTraining)
mAP = eval_mdl.mAP(qry_docs_ranking)
print('alpha: ', alpha)
print(mAP)
print('-----')
logging.debug("The mAP is " + str(mAP))

# Relevance Feedback
RM_mdl_np = RM3.feedback(qry_IDs, qry_mdl_np, doc_IDs, doc_mdl_np, bg_mdl_np, qry_docs_ranking, 9)
qry_mdl_np_ = np.zeros((qry_mdl_np.shape[0],qry_mdl_np.shape[1]))
#print(RM_mdl_np)
print("Second stage")
for alpha in np.linspace(0, 1, 11):
    logging.debug("alpha " + str(alpha))
    print('alpha: ', alpha)
    qry_mdl_np_ = (1 - alpha) * RM_mdl_np + alpha * qry_mdl_np
    #print(qry_mdl_np)
    # KL divergence
    results = np.argsort(-np.dot(qry_mdl_np_, np.log(doc_mdl_np.T)), axis = 1)

    # second-stage retrieval
    qry_docs_ranking = {}
    for q_idx, q_ID in enumerate(qry_IDs):
        docs_ranking = []
        for doc_idx in results[q_idx]:
            docs_ranking.append(doc_IDs[doc_idx])
        qry_docs_ranking[q_ID] = docs_ranking

    mAP = eval_mdl.mAP(qry_docs_ranking)
    logging.debug("The mAP is " + str(mAP))
    print(mAP)
    eval_mdl.reset()
