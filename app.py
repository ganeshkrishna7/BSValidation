from flask import Flask,render_template,request,session
import pandas as pd
import glob
import os
from ancillary import *
import numpy as np
pd.options.mode.chained_assignment = None 
app = Flask(__name__)

@app.route("/", methods =["GET", "POST"])
def getFile():
  if request.method == "POST":
    text = request.form['text']
    session['text']=text
  return render_template('Home.html')

@app.route("/PL", methods =["GET", "POST"])
def callComparePL():
  if request.method == "POST":
    text = request.form['text'] 
    session['text']=text 
  else:
    text = session.get('text')
  groundTruth=pd.read_excel("../groundTruthCorrected/"+text+".xlsx",engine='openpyxl',sheet_name="Accounts",header=None)
  predicted=pd.read_excel("../x_out_formulas/"+text+".XLSX",engine='openpyxl',sheet_name="ACCOUNTS",header=None)
  groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset(groundTruth,predicted)
  ResultscomparePL_Y1,ResultscomparePL_Y2,groundTruth_PL=comparePL(groundTruth_PL,predicted_PL)
  groundTruth_PL=groundTruth_PL[['LineItem','GroundTruth_Year1','Predicted_Year1','Difference_Year1','GroundTruth_Year2','Predicted_Year2','Difference_Year2']]
  matchrate_res1=matchRate(groundTruth_PL,'Year1')
  matchrate_res2=matchRate(groundTruth_PL,'Year2')
  del groundTruth_PL['matchYear']
  return render_template('Results.html',ResultscomparePL_Y1=ResultscomparePL_Y1.to_html(index=False),ResultscomparePL_Y2=ResultscomparePL_Y2.to_html(index=False),FullPL=groundTruth_PL.to_html(table_id="FullPL",index=False),filename=text,matchrate_res1=matchrate_res1,matchrate_res2=matchrate_res2)

@app.route("/BS", methods =["GET", "POST"])
def callCompareBS():
  if request.method == "POST":
    text = request.form['text'] 
    session['text']=text 
  else:
    text = session.get('text')
  groundTruth=pd.read_excel("../groundTruthCorrected/"+text+".xlsx",engine='openpyxl',sheet_name="Accounts",header=None)
  predicted=pd.read_excel("../x_out_formulas/"+text+".XLSX",engine='openpyxl',sheet_name="ACCOUNTS",header=None)
  groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(groundTruth,predicted)
  ResultscompareBS_Y1,ResultscompareBS_Y2,groundTruth_BS=compareBS(groundTruth_BS,predicted_BS)
  groundTruth_BS=groundTruth_BS[['LineItem','GroundTruth_Year1','Predicted_Year1','Difference_Year1','GroundTruth_Year2','Predicted_Year2','Difference_Year2']]

  matchrate_res1=matchRate(groundTruth_BS,'Year1')
  matchrate_res2=matchRate(groundTruth_BS,'Year2')
  del groundTruth_BS['matchYear']
  return render_template('ResultsBS.html',ResultscompareBS_Y1=ResultscompareBS_Y1.to_html(index=False),ResultscompareBS_Y2=ResultscompareBS_Y2.to_html(index=False),FullBS=groundTruth_BS.to_html(table_id="FullBS",index=False),filename=text,matchrate_res1=matchrate_res1,matchrate_res2=matchrate_res2)

@app.route("/aggregate", methods =["GET", "POST"])
def aggregate():
  path = "../groundTruthCorrected/"
  xls_files_gt = glob.glob(os.path.join(path, "*.xlsx"))
  xls_files_gt = [i.split("\\")[-1].lower() for i in xls_files_gt]
  xls_files_gt=set(xls_files_gt)

  path = "../x_out_formulas/"
  xls_files_pred = glob.glob(os.path.join(path, "*.XLSX"))
  xls_files_pred = [i.split("\\")[-1].lower() for i in xls_files_pred]
  xls_files_pred=set(xls_files_pred)

  xls_files=list(xls_files_gt.intersection(xls_files_pred))
  xls_files_gt=["../groundTruthCorrected\\"+i for i in xls_files]
  xls_files_pred=["../x_out_formulas\\"+i for i in xls_files]
  xls_files_pred=[i.replace("xlsx","XLSX") for i in xls_files_pred]

    
  groundTruth_BS_final=pd.DataFrame()
  groundTruth_PL_final=pd.DataFrame()
  for f in xls_files_gt:
    # read the xlsx file
    df = pd.read_excel(f,engine='openpyxl',sheet_name="Accounts",header=None)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(df,None)
    groundTruth_BS['filename']=f.split("\\")[-1]
    groundTruth_PL['filename']=f.split("\\")[-1]
    groundTruth_BS_final=pd.concat([groundTruth_BS_final,groundTruth_BS])
    groundTruth_PL_final=pd.concat([groundTruth_PL_final,groundTruth_PL])
  #.sort_values(by=['filename','LineItem']) 
  groundTruth_BS_final=groundTruth_BS_final.reset_index(drop=True)
  groundTruth_PL_final=groundTruth_PL_final.reset_index(drop=True)

  predicted_BS_final=pd.DataFrame()
  predicted_PL_final=pd.DataFrame()
  for f in xls_files_pred:
    # read the xlsx file
    df = pd.read_excel(f,engine='openpyxl',sheet_name="ACCOUNTS",header=None)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(None,df)
    predicted_BS['filename']=f.split("\\")[-1]
    predicted_PL['filename']=f.split("\\")[-1]
    predicted_BS_final=pd.concat([predicted_BS_final,predicted_BS])
    predicted_PL_final=pd.concat([predicted_PL_final,predicted_PL])

  predicted_BS_final=predicted_BS_final.reset_index(drop = True)
  predicted_PL_final=predicted_PL_final.reset_index(drop = True)
  #print(predicted_PL_final)
  print(groundTruth_BS_final.shape[0])
  print(predicted_BS_final.shape[0])
  
  ResultscomparePL_Y1,ResultscomparePL_Y2,groundTruth_PL=comparePL(groundTruth_PL_final,predicted_PL_final)
  ResultscompareBS_Y1,ResultscompareBS_Y2,groundTruth_BS=compareBS(groundTruth_BS_final,predicted_BS_final)

  #print(groundTruth_PL.head(10))
  groundTruth_PL['count']=groundTruth_PL.groupby(['LineItem','filename']).cumcount().astype(str)
  groundTruth_PL['uniqueid']=groundTruth_PL['count']+groundTruth_PL['LineItem']
  groundTruth_BS['count']=groundTruth_BS.groupby(['LineItem','filename']).cumcount().astype(str)
  groundTruth_BS['uniqueid']=groundTruth_BS['count']+groundTruth_BS['LineItem']

  PL_diff1=reshape_agg(groundTruth_PL,'Year1')
  PL_diff2=reshape_agg(groundTruth_PL,'Year2')
  BS_diff1=reshape_agg(groundTruth_BS,'Year1')
  #BS_diff2=reshape_agg(groundTruth_BS,'Year2')
  #BS_diff1 = BS_diff1.to_dict()

  
  return render_template('Aggregate.html',PL_diff1=PL_diff1.to_html(index=False,table_id="AggPL"),BS_diff1=BS_diff1.to_html(index=False,table_id="AggBS"))

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == "__main__":
  app.run()