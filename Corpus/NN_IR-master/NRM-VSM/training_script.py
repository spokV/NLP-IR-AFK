#!/usr/bin/env python3
import sys, os
pwd = os.path.dirname(os.path.realpath(__file__))

ROOTDIR = pwd + r"\.."
DATA = pwd + r"\data"
EXPPATH = pwd + r"\exp"

if(not os.path.isdir(DATA)):
    os.system("mkdir " + DATA)
    os.system("mkdir " + DATA + "\Train") 
    os.system("mkdir " + DATA + "\Test") 

if(not os.path.isdir(EXPPATH)):
    os.system("mkdir " + EXPPATH)

test_qry=ROOTDIR + r"\TDT2\QUERY_WDID_NEW"
test_rel=ROOTDIR + r"\TDT2\AssessmentTrainSet\AssessmentTrainSet.txt"
train_qry=ROOTDIR + r"\TDT2\Train\XinTrainQryTDT2\QUERY_WDID_NEW"
train_rel=ROOTDIR + r"\TDT2\Train\QDRelevanceTDT2_forHMMOutSideTrain"

TRAIN_DATA=DATA + r"\Train\x_qry_mdl.npy"

if(not os.path.isfile(TRAIN_DATA)):
    os.system("python local\VSM.py  --qry_dataset "+ test_qry + " --rel_dataset " + test_rel + " \
                                    --data_storage " + DATA +"\Test --is_train False")
    os.system("python local\VSM.py --qry_dataset " + train_qry + " --rel_dataset " + train_rel + " \
                                    --data_storage " + DATA + "\Train --is_train True")


MODEL_PATH=EXPPATH + r"\final.h5"

if(not os.path.isfile(MODEL_PATH)):
    os.system("python Train.py --learn_rate 0.001 --batch_size 32 --epochs 21 --num_hids 1 \
                --embed_dim 64 --exp_path " + EXPPATH + " --data_path " + DATA + "\Train  --save_best_only True")

if(os.path.isfile(MODEL_PATH)):
    print("")
    os.system("python Test.py --exp_path exp --model_name final.h5 --isTraining True")
    print("")
    os.system("python Test.py --exp_path exp --model_name final.h5 --isTraining False")
