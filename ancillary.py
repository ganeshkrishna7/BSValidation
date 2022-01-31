import pandas as pd

def clean(df):
    df = df.dropna(subset=['Year1', 'Year2','Predicted_Year1','Predicted_Year2'], how='all')
    df = df.reset_index(drop=True)
    df['Year1'] = df['Year1'].fillna(0)
    df['Year2'] = df['Year2'].fillna(0)
    df['Predicted_Year1'] = df['Predicted_Year1'].fillna(0)
    df['Predicted_Year2'] = df['Predicted_Year2'].fillna(0)
    return(df)

def subset(groundTruth,predicted):
   
    groundTruth.rename(columns={groundTruth.columns[4]: "LineItem",
    groundTruth.columns[5]: "Year1",
    groundTruth.columns[6]: "Year2",}, inplace = True)

    '''
    1) GroundTruth PL - subsetting PL from the Accounts sheet
    3) GroundTruth BS - subsetting BS from the Accounts sheet
    ''' 

    groundTruth_PL=groundTruth.loc[23:85, 'LineItem':'Year2']
    groundTruth_BS = groundTruth.loc[88:227, 'LineItem':'Year2']


    predicted.rename(columns={predicted.columns[4]: "LineItem",
    predicted.columns[5]: "Year1",
    predicted.columns[6]: "Year2",}, inplace = True)
    '''
    1) Predicted PL - subsetting PL from the Accounts sheet
    2) Predicted BS - subsetting BS from the Accounts sheet

    '''   
    predicted_PL=predicted.loc[23:85, 'LineItem':'Year2']
    predicted_BS = predicted.loc[88:227, 'LineItem':'Year2']
         
 
    return(groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL)


def comparePL(groundTruth_PL,predicted_PL):
    groundTruth_PL['Predicted_Year1']=predicted_PL['Year1']
    groundTruth_PL['Predicted_Year2']=predicted_PL['Year2']
    groundTruth_PL=clean(groundTruth_PL)

    groundTruth_PL['Difference_Year1']=groundTruth_PL.loc[:,'Year1'] - groundTruth_PL['Predicted_Year1']
    groundTruth_PL['Difference_Year2']=groundTruth_PL.loc[:,'Year2'] - groundTruth_PL['Predicted_Year2']

    comparePL_df_y1=groundTruth_PL[abs(groundTruth_PL['Difference_Year1'])>0]
    comparePL_df_y1.rename(columns={'Year1':'GroundTruth','Predicted_Year1':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    comparePL_df_y1=comparePL_df_y1[['LineItem','GroundTruth','Predicted','Difference']]

    comparePL_df_y2=groundTruth_PL[abs(groundTruth_PL['Difference_Year2'])>0]
    comparePL_df_y2.rename(columns={'Year2':'GroundTruth','Predicted_Year2':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    comparePL_df_y2=comparePL_df_y2[['LineItem','GroundTruth','Predicted','Difference']]

    groundTruth_PL.rename(columns={'Year1':'GroundTruth_Year1','Year2':'GroundTruth_Year2'}, inplace = True)
           
    return(comparePL_df_y1,comparePL_df_y2,groundTruth_PL)

def compareBS(groundTruth_BS,predicted_BS):
    groundTruth_BS['Predicted_Year1']=predicted_BS['Year1']
    groundTruth_BS['Predicted_Year2']=predicted_BS['Year2']
    groundTruth_BS=clean(groundTruth_BS)

    groundTruth_BS['Difference_Year1']=groundTruth_BS.loc[:,'Year1'] - groundTruth_BS['Predicted_Year1']
    groundTruth_BS['Difference_Year2']=groundTruth_BS.loc[:,'Year2'] - groundTruth_BS['Predicted_Year2']

    compareBS_df_y1=groundTruth_BS[abs(groundTruth_BS['Difference_Year1'])>0]
    compareBS_df_y1.rename(columns={'Year1':'GroundTruth','Predicted_Year1':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    compareBS_df_y1=compareBS_df_y1[['LineItem','GroundTruth','Predicted','Difference']]

    compareBS_df_y2=groundTruth_BS[abs(groundTruth_BS['Difference_Year2'])>0]
    compareBS_df_y2.rename(columns={'Year2':'GroundTruth','Predicted_Year2':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    compareBS_df_y2=compareBS_df_y2[['LineItem','GroundTruth','Predicted','Difference']]

    groundTruth_BS.rename(columns={'Year1':'GroundTruth_Year1','Year2':'GroundTruth_Year2'}, inplace = True)
 
    
    return(compareBS_df_y1,compareBS_df_y2,groundTruth_BS)

def matchRate(df,year):
    if year=='Year1':
        df['matchYear']=df['GroundTruth_Year1']==df['Predicted_Year1']
    else: 
        df['matchYear']=df['GroundTruth_Year2']==df['Predicted_Year2']
    c=df.groupby(['LineItem'],sort=False).agg({'matchYear':['sum','count']})
    c.columns = ['_'.join(col) for col in c.columns.values]
    c['matchRate']=c['matchYear_sum']/c['matchYear_count']
    c.rename(columns={"matchYear_sum": "Year_matches"}, inplace=True)
    sum_of_matches = c["Year_matches"].sum()
    sum_of_counts = c['matchYear_count'].sum()
    average = round(sum_of_matches*100/sum_of_counts,2)
    return(average)

def subset_agg(groundTruth,predicted):
    
    if (groundTruth is not None and predicted is None) or (groundTruth is not None and predicted is not None):
        groundTruth.rename(columns={groundTruth.columns[4]: "LineItem",
        groundTruth.columns[5]: "Year1",
        groundTruth.columns[6]: "Year2",}, inplace = True)

        '''
        1) GroundTruth PL - subsetting PL from the Accounts sheet
        3) GroundTruth BS - subsetting BS from the Accounts sheet
        ''' 

        groundTruth_PL=groundTruth.loc[23:85, 'LineItem':'Year2']
        groundTruth_BS = groundTruth.loc[88:227, 'LineItem':'Year2']

    if (groundTruth is None and predicted is not None) or (groundTruth is not None and predicted is not None):
        predicted.rename(columns={predicted.columns[4]: "LineItem",
        predicted.columns[5]: "Year1",
        predicted.columns[6]: "Year2",}, inplace = True)
        '''
        1) Predicted PL - subsetting PL from the Accounts sheet
        2) Predicted BS - subsetting BS from the Accounts sheet

        '''   
        predicted_PL=predicted.loc[23:85, 'LineItem':'Year2']
        predicted_BS = predicted.loc[88:227, 'LineItem':'Year2']
    
    if predicted is None:
        predicted_PL=None
        predicted_BS=None
    if groundTruth is None:
        groundTruth_PL=None
        groundTruth_BS=None
 
    return(groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL)

def clean_agg(df,Year):
    df['filename']=df['filename'].str[0:3]
    if(Year=='Year1'):
        df1=df.pivot(index='uniqueid',columns='filename')[['Difference_Year1']].reset_index()
    else:
        df1=df.pivot(index='uniqueid',columns='filename')[['Difference_Year2']].reset_index()
    df1 = df1.fillna(0)
    temp=df1['uniqueid'].str[1:100]
    df1.columns = df1.columns.droplevel()
    df1.insert(loc=0,column='LineItem',value=temp)
    del df1['']
    df1 = df1.rename_axis(None, axis=1)
    return(df1)