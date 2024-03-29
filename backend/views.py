import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, preprocessing
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from diffprivlib.models import GaussianNB as GNB
from diffprivlib import tools as tools

import warnings
from sys import maxsize
import diffprivlib as dp
from diffprivlib.accountant import BudgetAccountant
from diffprivlib.mechanisms import GeometricTruncated
from diffprivlib.utils import PrivacyLeakWarning, warn_unused_args
# Create your views here.
def histWithdp(dataset,attribute):
    dp_hist, dp_bins = tools.histogram(dataset[attribute],bins=len(dataset[attribute].unique()))
    #print('dp-bins',dataset[attribute].unique())
    return dp_hist.tolist(), dp_bins.tolist()

def histWithoutdp(dataset,attribute):
    hist,bins = np.histogram(dataset[attribute],bins=len(dataset[attribute].unique()))
    return hist.tolist(), bins.tolist()

@csrf_exempt 
def visualizeattributes(request):
    
    if request.method == 'POST':
        data = json.loads(request.body)
        print("type of data",json.loads(request.body))
        attribute = data['selected']
        print('Attri',attribute)
        dp_bool = data['dpcheck']
        grph_type = data['grph_type']
        print(grph_type)
        request.session['attribute'] = attribute
        print(request.session.get('attribute'))
        #print('records',dataset[attribute][:50])
        dataset=preprocess()
        category_names=dataset[attribute].unique()
        dataset=labelencode(dataset)
        categories=dataset[attribute].unique()        
        attributelist=dataset[attribute].tolist()
        
        if(dp_bool==True):
            if grph_type == 'Scatter plot':
                y_num = dataset[attribute].tolist()[:100]
                x_num = list(range(0,100))
                print(y_num)
                acc = dp.BudgetAccountant(epsilon=5.5, delta=0)
                accountant = BudgetAccountant.load_default(acc)
                res = scatter(y_num,epsilon=1,delta = 0,accountant = accountant)
                print(res)
                '''
                res uses ynum containing 100 data points
                '''
            else:
                res, bins = histWithdp(dataset,attribute)
                y_num = res
                x_num = list(range(0,len(y_num)))
                print('x',x_num,'y:',y_num)
            x_axis = list(range(0,len(res)))
            
            print('end of function visualizeattributes')
            return JsonResponse({'x': x_axis,'y':res,'x_labels':category_names.tolist(),'x_num':x_num,'y_num':res})
        else:
            if(grph_type=='Scatter plot'):
                #res, bins = histWithoutdp(dataset,attribute)
                #x_axis = list(range(0,len(res)))
                
                x_num = list(range(0,100))
                y_num = dataset[attribute].tolist()[:100]
                res=y_num
                        
            else:
                res, bins = histWithoutdp(dataset,attribute)
                #print(res)
                y_num=res
                
                #x_num = list(range(0,100))
                #y_num = dataset[attribute].tolist()[:100]
                x_num = list(range(0,len(y_num)))
                #print(x_num)
            x_axis = list(range(0,len(res)))
            return JsonResponse({'x': x_axis,'y':res,'x_labels':category_names.tolist(),'x_num':x_num,'y_num':y_num})
        
@csrf_exempt 
def dashboardApi(request):
    
    if request.method == 'POST':
        data = request.POST
        epsilon = list(data.keys())[0]
        request.session['epsilon'] = epsilon
        y,y_dp,res,res_dp,actual,ac_score,ac_score_dp=plot_predictions(epsilon)
        x_axis = list(range(0,100))
        return JsonResponse({'x':x_axis,'y':y,'y_dp':y_dp,'acc_dp':ac_score_dp,'acc':ac_score,'res': res, 'res_dp': res_dp,'actual': actual,'rem':100-(ac_score),'rem_dp':100-(ac_score_dp)})
    if request.method == 'GET':
        eps = request.session.get('epsilon')

        print("gettttt methhoddd",eps)
        y,y_dp,res,res_dp,actual,ac_score,ac_score_dp=plot_predictions(1)
        x_axis = list(range(0,100))
        
        return JsonResponse({'x':x_axis,'y':y,'y_dp':y_dp,'acc_dp':ac_score_dp,'acc':ac_score,'res': res, 'res_dp': res_dp,'actual': actual,'rem':100-(ac_score),'rem_dp':100-(ac_score_dp)})

def preprocess():
    GENETICS_DATASET = pd.read_csv(r"C:\Users\Aditi Joshi\Documents\IBM_Group8_DifferentialPrivacy\archive (4)\train.csv")
    dataset = GENETICS_DATASET.copy()
    # Drop unwanted fields
    dataset.drop(["Test 1","Test 2","Test 3","Test 4","Test 5","Status","Parental consent","Place of birth","Follow-up",
                           "Patient Id", "Patient First Name", "Family Name","Father's name",
              "Location of Institute", "Institute Name"], axis = 1, inplace = True)
    dataset["Birth asphyxia"] = dataset["Birth asphyxia"].replace("No record",np.NaN)
    dataset["Birth asphyxia"] = dataset["Birth asphyxia"].replace("Not available",np.NaN)

    dataset["Autopsy shows birth defect (if applicable)"] = dataset["Autopsy shows birth defect (if applicable)"].replace("None",np.NaN)
    dataset["Autopsy shows birth defect (if applicable)"] = dataset["Autopsy shows birth defect (if applicable)"].replace("Not applicable",np.NaN)

    dataset["H/O radiation exposure (x-ray)"] = dataset["H/O radiation exposure (x-ray)"].replace("Not applicable",np.NaN)
    dataset["H/O radiation exposure (x-ray)"] = dataset["H/O radiation exposure (x-ray)"].replace("-",np.NaN)

    dataset["H/O substance abuse"] = dataset["H/O substance abuse"].replace("Not applicable",np.NaN)
    dataset["H/O substance abuse"] = dataset["H/O substance abuse"].replace("-",np.NaN)

    dataset["Inherited from father"].fillna(dataset["Inherited from father"].mode()[0], inplace=True)
    dataset["Maternal gene"].fillna(dataset["Maternal gene"].mode()[0], inplace=True)
    dataset["Respiratory Rate (breaths/min)"].fillna(dataset["Respiratory Rate (breaths/min)"].mode()[0], inplace=True)
    dataset["Heart Rate (rates/min"].fillna(dataset["Heart Rate (rates/min"].mode()[0], inplace=True)
    dataset["Gender"].fillna(dataset["Gender"].mode()[0], inplace=True)
    dataset["Folic acid details (peri-conceptional)"].fillna(dataset["Folic acid details (peri-conceptional)"].mode()[0], inplace=True)
    dataset["H/O serious maternal illness"].fillna(dataset["H/O serious maternal illness"].mode()[0], inplace=True)
    dataset["Assisted conception IVF/ART"].fillna(dataset["Assisted conception IVF/ART"].mode()[0], inplace=True)
    dataset["History of anomalies in previous pregnancies"].fillna(dataset["History of anomalies in previous pregnancies"].mode()[0], inplace=True)
    dataset["Birth defects"].fillna(dataset["Birth defects"].mode()[0], inplace=True)
    dataset["Blood test result"].fillna(dataset["Blood test result"].mode()[0], inplace=True)

    dataset["Patient Age"].fillna(dataset["Patient Age"].mode()[0], inplace=True)
    #dataset["Patient Age"].fillna(dataset.groupby(["Disorder Subclass"])["Patient Age"].transform("mean"),inplace=True)
    dataset["Mother's age"].fillna(dataset.groupby(["Disorder Subclass"])["Mother's age"].transform("mean"),inplace=True)
    dataset["Father's age"].fillna(dataset.groupby(["Disorder Subclass"])["Father's age"].transform("mean"),inplace=True)
    dataset["No. of previous abortion"].fillna(dataset.groupby(["Disorder Subclass"])["No. of previous abortion"].transform("mean"),inplace=True)
    dataset["White Blood cell count (thousand per microliter)"].fillna(dataset.groupby(["Disorder Subclass"])["White Blood cell count (thousand per microliter)"].transform("mean"),inplace=True)

    dataset["Symptom 1"].fillna(dataset["Symptom 1"].mode()[0], inplace=True)
    dataset["Symptom 2"].fillna(dataset["Symptom 2"].mode()[0], inplace=True)
    dataset["Symptom 3"].fillna(dataset["Symptom 3"].mode()[0], inplace=True)
    dataset["Symptom 4"].fillna(dataset["Symptom 4"].mode()[0], inplace=True)
    dataset["Symptom 5"].fillna(dataset["Symptom 5"].mode()[0], inplace=True)

    dataset["Birth asphyxia"].fillna(dataset["Birth asphyxia"].mode()[0], inplace=True)
    dataset["Autopsy shows birth defect (if applicable)"].fillna(dataset["Autopsy shows birth defect (if applicable)"].mode()[0], inplace=True)
    dataset["H/O radiation exposure (x-ray)"].fillna(dataset["H/O radiation exposure (x-ray)"].mode()[0], inplace=True)
    dataset["H/O substance abuse"].fillna(dataset["H/O substance abuse"].mode()[0], inplace=True)

    dataset.dropna(inplace=True,axis=0)
    return dataset

def labelencode(dataset):
    label_encoder = preprocessing.LabelEncoder()
    dataset["Genes in mother's side"]= label_encoder.fit_transform(dataset["Genes in mother's side"])
    dataset["Inherited from father"]= label_encoder.fit_transform(dataset["Inherited from father"])
    dataset["Maternal gene"]= label_encoder.fit_transform(dataset["Inherited from father"])
    dataset["Paternal gene"]= label_encoder.fit_transform(dataset["Inherited from father"])
    dataset['Respiratory Rate (breaths/min)']= label_encoder.fit_transform(dataset['Respiratory Rate (breaths/min)'])
    dataset['Heart Rate (rates/min']= label_encoder.fit_transform(dataset['Heart Rate (rates/min'])
    dataset['Folic acid details (peri-conceptional)']= label_encoder.fit_transform(dataset['Folic acid details (peri-conceptional)'])
    dataset['H/O serious maternal illness']= label_encoder.fit_transform(dataset['H/O serious maternal illness'])
    dataset['Assisted conception IVF/ART']= label_encoder.fit_transform(dataset['Assisted conception IVF/ART'])
    dataset['History of anomalies in previous pregnancies']= label_encoder.fit_transform(dataset['History of anomalies in previous pregnancies'])
    dataset['Birth defects']= label_encoder.fit_transform(dataset['Birth defects'])
    dataset['Blood test result']= label_encoder.fit_transform(dataset['Blood test result'])

    dataset['Birth asphyxia']= label_encoder.fit_transform(dataset['Birth asphyxia'])
    dataset['Autopsy shows birth defect (if applicable)']= label_encoder.fit_transform(dataset['Autopsy shows birth defect (if applicable)'])
    dataset['H/O radiation exposure (x-ray)']= label_encoder.fit_transform(dataset['H/O radiation exposure (x-ray)'])
    dataset['H/O substance abuse']= label_encoder.fit_transform(dataset['H/O substance abuse'])
    dataset["Genetic Disorder"]= label_encoder.fit_transform(dataset["Genetic Disorder"])
    dataset["Disorder Subclass"]= label_encoder.fit_transform(dataset["Disorder Subclass"])
    dataset["Gender"]= label_encoder.fit_transform(dataset["Gender"])

    return dataset

def plot_predictions(eps):
    print("epsiiiiiillllon",eps)
    dataset=preprocess()
    dataset=labelencode(dataset)
    x=dataset.iloc[:,:-2]
    y = dataset[['Genetic Disorder']]
    #x["sum of Mother's and fathers age avg"]=(x["Mother's age"]+x["Father's age"]) / 2
    x["total symptom"]=(x["Symptom 1"]+x["Symptom 2"]+x["Symptom 3"]+x["Symptom 4"]+x["Symptom 5"]) / 5
    x = x.apply(pd.to_numeric,downcast="float")
    y = y.apply(pd.to_numeric,downcast="float")

    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size = 0.3,random_state = 1)
    
    clf = GaussianNB()
    clf.fit(x_train, y_train)
    y_pred=clf.predict(x_test)
    acc_score=clf.score(x_test, y_test)

   
    # differential privacy
    print("int of epsiln",int(eps))
    clf = GNB(epsilon = int(eps))
    clf.fit(x_train, y_train)
    y_pred_dp=clf.predict(x_test)
    acc_score_dp= clf.score(x_test, y_test)
    print("acc",acc_score_dp)
    y_pred_list = y_pred.tolist()[:100]
    y_pred_dp_list = y_pred_dp.tolist()[:100]
    results = [y_pred_list.count(0), y_pred_list.count(1), y_pred_list.count(2)]
    results_dp=[y_pred_dp_list.count(0), y_pred_dp_list.count(1), y_pred_dp_list.count(2)]
    disease = [0,1,2]

    y_test_list = y_test['Genetic Disorder'].tolist()[:100]
    actual = [y_test_list.count(0), y_test_list.count(1), y_test_list.count(2)]
    #plt.bar(disease, results)
    #plt.show()
    return y_pred_list , y_pred_dp_list, results,results_dp, actual,acc_score*100,acc_score_dp*100

def scatter(sample, epsilon=1.0, delta=0, accountant=None, **unused_args):
    """
    epsilon : float, default: 1.0
        Privacy parameter :math:`\epsilon` to be applied.
        
    sample: y co-ordinates 
    
    accountant : BudgetAccountant, optional
        Accountant to keep track of privacy budget.
        
    Returns:
    
    y-co-ordinates: array
    """
    warn_unused_args(unused_args)
    accountant = BudgetAccountant.load_default(accountant)
    accountant.check(epsilon, delta)
    dp_mech = GeometricTruncated(epsilon=epsilon, sensitivity=1, lower=0, upper=maxsize)
    dp_scatter = np.zeros_like(sample)

    for i in np.arange(dp_scatter.shape[0]):
        dp_scatter[i] = dp_mech.randomise(int(sample[i]))
        
    accountant.spend(epsilon, 0)
    
    return dp_scatter.tolist()

