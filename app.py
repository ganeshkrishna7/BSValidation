from flask import Flask,render_template,request,session
import pandas as pd
import glob
import os
from ancillary import *
import numpy as np
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
  groundTruth=pd.read_excel("../Groundtruth_Temp/"+text+".xlsx",engine='openpyxl',sheet_name="Accounts",header=None)
  predicted=pd.read_excel("../Predicted_Temp/"+text+".xlsx",engine='openpyxl',sheet_name="Accounts",header=None)
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
  groundTruth=pd.read_excel("../Groundtruth/"+text+".xlsx",engine='openpyxl',sheet_name="Accounts",header=None)
  predicted=pd.read_excel("../Predicted/"+text+".xlsx",engine='openpyxl',sheet_name="Accounts",header=None)
  groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(groundTruth,predicted)
  ResultscompareBS_Y1,ResultscompareBS_Y2,groundTruth_BS=compareBS(groundTruth_BS,predicted_BS)
  groundTruth_BS=groundTruth_BS[['LineItem','GroundTruth_Year1','Predicted_Year1','Difference_Year1','GroundTruth_Year2','Predicted_Year2','Difference_Year2']]

  matchrate_res1=matchRate(groundTruth_BS,'Year1')
  matchrate_res2=matchRate(groundTruth_BS,'Year2')
  del groundTruth_BS['matchYear']
  return render_template('ResultsBS.html',ResultscompareBS_Y1=ResultscompareBS_Y1.to_html(index=False),ResultscompareBS_Y2=ResultscompareBS_Y2.to_html(index=False),FullBS=groundTruth_BS.to_html(table_id="FullBS",index=False),filename=text,matchrate_res1=matchrate_res1,matchrate_res2=matchrate_res2)

@app.route("/aggregate", methods =["GET", "POST"])
def aggregate():
  path = "../Groundtruth_Temp/"
  xls_files = glob.glob(os.path.join(path, "*.xlsx"))
  
  groundTruth_BS_final=pd.DataFrame()
  groundTruth_PL_final=pd.DataFrame()
  for f in xls_files:
    # read the xlsx file
    df = pd.read_excel(f,engine='openpyxl',sheet_name="Accounts",header=None)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(df,None)
    groundTruth_BS['filename']=f.split("\\")[-1]
    groundTruth_PL['filename']=f.split("\\")[-1]
    groundTruth_BS_final=pd.concat([groundTruth_BS_final,groundTruth_BS])
    groundTruth_PL_final=pd.concat([groundTruth_PL_final,groundTruth_PL])

  path = "../Predicted_Temp/"
  xls_files = glob.glob(os.path.join(path, "*.xlsx"))

  predicted_BS_final=pd.DataFrame()
  predicted_PL_final=pd.DataFrame()
  for f in xls_files:
    # read the xlsx file
    df = pd.read_excel(f,engine='openpyxl',sheet_name="Accounts",header=None)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(None,df)
    predicted_BS['filename']=f.split("\\")[-1]
    predicted_PL['filename']=f.split("\\")[-1]
    predicted_BS_final=pd.concat([predicted_BS_final,predicted_BS])
    predicted_PL_final=pd.concat([predicted_PL_final,predicted_PL])

  #print(predicted_BS_final.columns)
  temp=predicted_BS_final.isnull()
  temp=temp.any(axis=1)
  temp=predicted_BS_final[temp]
  temp.to_csv("NAValues.csv")

  ResultscomparePL_Y1,ResultscomparePL_Y2,groundTruth_PL=comparePL(groundTruth_PL_final,predicted_PL_final)
  ResultscompareBS_Y1,ResultscompareBS_Y2,groundTruth_BS=compareBS(groundTruth_BS_final,predicted_BS_final)
  #print(groundTruth_PL.head(10))
  groundTruth_PL['count']=groundTruth_PL.groupby(['LineItem','filename']).cumcount().astype(str)
  groundTruth_PL['uniqueid']=groundTruth_PL['count']+groundTruth_PL['LineItem']
  groundTruth_BS['count']=groundTruth_BS.groupby(['LineItem','filename']).cumcount().astype(str)
  groundTruth_BS['uniqueid']=groundTruth_BS['count']+groundTruth_BS['LineItem']

  PL_diff1=clean_agg(groundTruth_PL,'Year1')
  PL_diff2=clean_agg(groundTruth_PL,'Year2')
  BS_diff1=clean_agg(groundTruth_BS,'Year1')
  #BS_diff2=clean_agg(groundTruth_BS,'Year2')
  #BS_diff1 = BS_diff1.to_dict()
  #session['BS_diff1'] = BS_diff1

  #temp.to_csv("grouped.csv")
  
  return render_template('Aggregate.html',PL_diff1=PL_diff1.to_html(index=False,table_id="AggPL"),BS_diff1=BS_diff1.to_html(index=False,table_id="AggBS"))

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == "__main__":
  app.run()