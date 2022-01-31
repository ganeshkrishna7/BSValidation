import pandas as pd
import glob
import os
from ancillary import *


path = "../temp/"
xls_files = glob.glob(os.path.join(path, "*.xlsx"))
print(xls_files)

groundTruth_BS_final=pd.DataFrame()
groundTruth_PL_final=pd.DataFrame()
for f in xls_files:
    # read the csv file
    df = pd.read_excel(f)
    groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL=subset(df,None)
    groundTruth_BS['filename']=f.split("\\")[-1]
    groundTruth_PL['filename']=f.split("\\")[-1]
    groundTruth_BS_final=groundTruth_BS_final.append(groundTruth_BS)
    groundTruth_PL_final=groundTruth_PL_final.append(groundTruth_PL)
    print(groundTruth_BS_final.tail(5))

                



