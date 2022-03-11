from flask import Flask,render_template,request,session,flash,redirect,url_for,abort,Response
import pandas as pd
import glob
import os
from ancillary import *
import numpy as np
from werkzeug.utils import secure_filename

pd.options.mode.chained_assignment = None 
app = Flask(__name__,static_url_path='/static_comparator', static_folder='static_comparator')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/comparator/", methods =["GET", "POST"])
def getFile():
  #print()
  session.clear()
  if request.method == 'POST':
    text = request.form['text_gt']
    session['text']=text

    filelist = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'],'gt', "*"))
    for f in filelist:
      os.remove(f)
    filelist = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'],'pred', "*"))
    for f in filelist:
      os.remove(f)
      # check if the post request has the file part
    if 'gt_file' not in request.files:
        flash('No file part') 
    file = request.files["gt_file"]
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],'gt', file.filename))
        path_gt=os.path.join(app.config['UPLOAD_FOLDER'],'gt', file.filename)
        session['path_gt']=path_gt

    file = request.files["pred_file"]
    if file.filename == '':
        flash('No selected file')
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],'pred', file.filename))
        path_pred=os.path.join(app.config['UPLOAD_FOLDER'],'pred', file.filename)
        session['path_pred']=path_pred
	
       
    if request.form['BS_PL']=="PL":
      #return redirect("http://182.66.232.170:4055/PL")

      return redirect(url_for('callComparePL', _external=True))	
    else:
      #return redirect("http://182.66.232.170:4055/BS")
      return redirect(url_for('callCompareBS'))
	
  return render_template('Home_v2.html')


def commonCode():
    if request.method == "POST":
      text = request.form['text'] 
      text=text+'.xlsx'
      path_pred = os.path.join(os.path.dirname(app.instance_path),'Database','x_out_formulas')
      path_gt = os.path.join(os.path.dirname(app.instance_path),'Database','groundTruthCorrected')
      final_gt=os.path.join(path_gt,text)
      final_pred=os.path.join(path_pred,text)
      session['path_gt']=final_gt # for same file to be viewed in both PL and BS
      session['path_pred']=final_pred
      
    elif session.get('path_pred') is None and session.get('path_gt') is None:
      path_pred = os.path.join(os.path.dirname(app.instance_path),'Database','x_out_formulas')
      path_gt = os.path.join(os.path.dirname(app.instance_path),'Database','groundTruthCorrected')
      text = session.get('text')
      text=text+'.xlsx'
      final_gt=os.path.join(path_gt,text)
      final_pred=os.path.join(path_pred,text)

    elif session.get('path_pred') is not None and session.get('path_gt') is None:
      path_pred = session.get('path_pred')
      text=os.path.basename(path_pred)
      path_gt = os.path.join(os.path.dirname(app.instance_path),'Database','groundTruthCorrected')
      final_gt=os.path.join(path_gt,text)
      final_gt = final_gt.replace("XLSX","xlsx")
      final_pred=path_pred

    elif session.get('path_pred') is not None and session.get('path_gt') is not None:
      final_pred = session.get('path_pred')
      final_gt=session.get('path_gt')
      text=os.path.basename(final_gt)
  
    #print(final_gt)
    #print(final_pred)
    final_pred = final_pred.replace("xlsx","XLSX")
    predicted=None
    groundTruth=pd.read_excel(final_gt,engine='openpyxl',sheet_name="Accounts",header=None)
    bsdebug,bsdetailed,pldebug,pldetailed=pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),pd.DataFrame()
    
    try:
      predicted=pd.read_excel(final_pred, engine='openpyxl',sheet_name='ACCOUNTS',header=None) 
    except: 
      predicted=pd.read_excel(final_pred.replace("XLSX","xlsx"), engine='openpyxl',sheet_name='Accounts',header=None)
      bsdebug=pd.read_excel(final_pred.replace("XLSX","xlsx"), engine='openpyxl',sheet_name='debug_bs')
      bsdetailed=pd.read_excel(final_pred.replace("XLSX","xlsx"), engine='openpyxl',sheet_name='debugbsdetailed')
      pldebug=pd.read_excel(final_pred.replace("XLSX","xlsx"), engine='openpyxl',sheet_name='debug_pl')
      pldetailed=pd.read_excel(final_pred.replace("XLSX","xlsx"), engine='openpyxl',sheet_name='debugpldetailed')
    
      bsdebug,bsdetailed,pldebug,pldetailed=other_info(bsdebug,bsdetailed,pldebug,pldetailed)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset(groundTruth,predicted)
    return(groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL,text,bsdebug,bsdetailed,pldebug,pldetailed)    

@app.route("/comparator/PL", methods =["GET", "POST"])
def callComparePL():
#try:
  groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL,text,bsdebug,bsdetailed,pldebug,pldetailed=commonCode()
  ResultscomparePL_Y1,ResultscomparePL_Y2,groundTruth_PL=comparePL(groundTruth_PL,predicted_PL)
  groundTruth_PL=groundTruth_PL[['LineItem','GroundTruth_Year1','Predicted_Year1','Difference_Year1','GroundTruth_Year2','Predicted_Year2','Difference_Year2']]
  
  if pldebug.shape[0] ==0:
    pldebug = None
  else:
    pldetailed=pldetailed.to_html(index=False)
    pldebug=pldebug.to_html(index=False)
  
  matchrate_res1=matchRate(groundTruth_PL,'Year1')
  matchrate_res2=matchRate(groundTruth_PL,'Year2')
  del groundTruth_PL['matchYear']  
  
  return render_template('Results.html',ResultscomparePL_Y1=ResultscomparePL_Y1.to_html(index=False),ResultscomparePL_Y2=ResultscomparePL_Y2.to_html(index=False),FullPL=groundTruth_PL.to_html(table_id="FullPL",index=False),filename=text,matchrate_res1=matchrate_res1,matchrate_res2=matchrate_res2,pldebug=pldebug,pldetailed=pldetailed)
#except:
#    return redirect(url_for('getFile'))

@app.route("/comparator/BS", methods =["GET", "POST"])
def callCompareBS():
#try:
  groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL,text,bsdebug,bsdetailed,pldebug,pldetailed=commonCode()
  ResultscompareBS_Y1,ResultscompareBS_Y2,groundTruth_BS,match2=compareBS(groundTruth_BS,predicted_BS)
  groundTruth_BS=groundTruth_BS[['LineItem','GroundTruth_Year1','Predicted_Year1','Difference_Year1','GroundTruth_Year2','Predicted_Year2','Difference_Year2','LineItem to be Mapped']]

  if bsdebug.shape[0] ==0:
    bsdebug = None
  else:
    bsdetailed=bsdetailed.to_html(index=False)
    bsdebug=bsdebug.to_html(index=False)

  matchrate_res1=matchRate(groundTruth_BS,'Year1')
  matchrate_res2=matchRate(groundTruth_BS,'Year2')
  del groundTruth_BS['matchYear']
  if match2 is not None:
    return render_template('ResultsBS.html',ResultscompareBS_Y1=ResultscompareBS_Y1.to_html(index=False),ResultscompareBS_Y2=ResultscompareBS_Y2.to_html(index=False),FullBS=groundTruth_BS.to_html(table_id="FullBS",index=False),filename=text,matchrate_res1=matchrate_res1,matchrate_res2=matchrate_res2,match2=match2.to_html(index=False),bsdebug=bsdebug,bsdetailed=bsdetailed)
  else:
      return render_template('ResultsBS.html',ResultscompareBS_Y1=ResultscompareBS_Y1.to_html(index=False),ResultscompareBS_Y2=ResultscompareBS_Y2.to_html(index=False),FullBS=groundTruth_BS.to_html(table_id="FullBS",index=False),filename=text,matchrate_res1=matchrate_res1,matchrate_res2=matchrate_res2,bsdebug=bsdebug,bsdetailed=bsdetailed)
#  except:
#    return redirect(url_for('getFile'))

@app.route("/comparator/aggregate", methods =["GET", "POST"])
def aggregate():
  path_pred = os.path.join(os.path.dirname(app.instance_path),'Database','x_out_formulas')
  path_gt = os.path.join(os.path.dirname(app.instance_path),'Database','groundTruthCorrected')

  xls_files_gt = glob.glob(os.path.join(path_gt, "*.xlsx"))
  xls_files_gt = [os.path.basename(i).lower() for i in xls_files_gt]
  xls_files_gt=set(xls_files_gt)

  
  xls_files_pred = glob.glob(os.path.join(path_pred, "*.XLSX"))
  xls_files_pred = [os.path.basename(i).lower() for i in xls_files_pred]
  xls_files_pred=set(xls_files_pred)

  xls_files=list(xls_files_gt.intersection(xls_files_pred))
  xls_files_gt=[os.path.join(path_gt,i) for i in xls_files]
  xls_files_pred=[os.path.join(path_pred,i) for i in xls_files]
  xls_files_pred=[i.replace("xlsx","XLSX") for i in xls_files_pred]

    
  groundTruth_BS_final=pd.DataFrame()
  groundTruth_PL_final=pd.DataFrame()
  for f in xls_files_gt:
    # read the xlsx file
    try: 
      df=pd.read_excel(f, sheet_name='ACCOUNTS',engine='openpyxl',header=None)
    except: 
      df=pd.read_excel(f.replace("XLSX","xlsx"), sheet_name='Accounts',engine='openpyxl',header=None)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(df,None)
    groundTruth_BS['filename']=os.path.basename(f)
    groundTruth_PL['filename']=os.path.basename(f)
    groundTruth_BS_final=pd.concat([groundTruth_BS_final,groundTruth_BS])
    groundTruth_PL_final=pd.concat([groundTruth_PL_final,groundTruth_PL])
  #.sort_values(by=['filename','LineItem']) 
  groundTruth_BS_final=groundTruth_BS_final.reset_index(drop=True)
  groundTruth_PL_final=groundTruth_PL_final.reset_index(drop=True)

  predicted_BS_final=pd.DataFrame()
  predicted_PL_final=pd.DataFrame()
  for f in xls_files_pred:
    # read the xlsx file  
    try:
      df = pd.read_excel(f,engine='openpyxl',sheet_name="ACCOUNTS",header=None)
    except:
      df = pd.read_excel(f,engine='openpyxl',sheet_name="Accounts",header=None)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset_agg(None,df)
    predicted_BS['filename']=os.path.basename(f)
    predicted_PL['filename']=os.path.basename(f)
    predicted_BS_final=pd.concat([predicted_BS_final,predicted_BS])
    predicted_PL_final=pd.concat([predicted_PL_final,predicted_PL])

  predicted_BS_final=predicted_BS_final.reset_index(drop = True)
  predicted_PL_final=predicted_PL_final.reset_index(drop = True)
  #print(predicted_PL_final)
  print(groundTruth_BS_final.shape[0])
  print(predicted_BS_final.shape[0])
  
  ResultscomparePL_Y1,ResultscomparePL_Y2,groundTruth_PL=comparePL_agg(groundTruth_PL_final,predicted_PL_final)
  ResultscompareBS_Y1,ResultscompareBS_Y2,groundTruth_BS=comparePL_agg(groundTruth_BS_final,predicted_BS_final)

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


with app.test_request_context():
  print(url_for('callCompareBS'))
  print(url_for('callComparePL'))
  print(url_for('getFile'))


app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

UPLOAD_FOLDER = os.path.join(os.path.dirname(app.instance_path),'upload')
ALLOWED_EXTENSIONS = {'xls','xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == "__main__":
  app.run(port=5566)
