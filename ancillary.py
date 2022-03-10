import pandas as pd
import itertools

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

    groundTruth_PL=groundTruth.loc[:, 'LineItem':'Year2']
    groundTruth_PL=groundTruth_PL.iloc[23:85,:]
    groundTruth_BS = groundTruth.loc[:, 'LineItem':'Year2']
    groundTruth_BS=groundTruth_BS.iloc[88:227,:]

    predicted.rename(columns={predicted.columns[4]: "LineItem",
    predicted.columns[5]: "Year1",
    predicted.columns[6]: "Year2",}, inplace = True)

    '''
    1) Predicted PL - subsetting PL from the Accounts sheet
    2) Predicted BS - subsetting BS from the Accounts sheet

    '''   
    predicted_PL=predicted.loc[:, 'LineItem':'Year2']
    predicted_PL=predicted_PL.iloc[23:85,:]
    predicted_BS =predicted.loc[:, 'LineItem':'Year2']
    predicted_BS=predicted_BS.iloc[88:227,:]
        
 
    return(groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL)

def FindIssues(df):
    df['count']=df.groupby(['LineItem']).cumcount().astype(str)
    df['uniqueid']=df['count']+df['LineItem']
    #mapping_file=pd.read_excel("../mappingFile.xlsx",engine='openpyxl',sheet_name="BS_Mapping")
    #mapping_file=mapping_file.drop(['LineItem','Header'],axis=1)
    #df=pd.merge(df,mapping_file,on="uniqueid",how='left')

    df['negative_diff']=-df['Difference_Year1']
    matches=df.loc[(df['Difference_Year1'].isin(df['negative_diff'])) & (df['Difference_Year1']!=0)]
    matches=matches.reset_index(drop=True)
    #print(matches[['Difference_Year1','negative_diff','LineItem']])
    match_LineItem={}
    for i in range(0,len(matches),1):
        for j in range(0,len(matches),1):
            if(matches.loc[i,'Difference_Year1']==matches.loc[j,'negative_diff']):
                data={matches.loc[i,'LineItem'] : [matches.loc[j,'LineItem']]}
                if len(match_LineItem) == 0:
                    match_LineItem.update(data)
                elif(list(data.keys())[0] in match_LineItem):
                        match_LineItem[list(data.keys())[0]].append(matches.loc[j,'LineItem'])
                else:
                    match_LineItem.update(data)
    
    for i in match_LineItem:
        match_LineItem[i]=','.join(match_LineItem[i])

    temp=pd.DataFrame.from_dict(match_LineItem,orient ='index')
    
    if len(temp)==0:
        df['LineItem to be Mapped'] = ''
    else:    
        temp['LineItem'] = temp.index
        temp=temp.reset_index(drop=True)
        temp.rename(columns={0:'LineItem to be Mapped'}, inplace = True)
        print(temp)
        temp=temp[['LineItem','LineItem to be Mapped']]
        #print(temp)

        df=pd.merge(df,temp,on="LineItem",how='left')
        df.drop(['uniqueid', 'negative_diff','count'],axis=1)
        df['LineItem to be Mapped'] = df['LineItem to be Mapped'].fillna('')
    

    temp=df[(df['Difference_Year1']!=0) & (~df['LineItem'].isin(matches['LineItem']))].reset_index(drop=True) 
    temp0=temp[['LineItem']]

    base_list=[]
    for i in range(3, 0, -1):
        for seq in itertools.combinations(enumerate(temp['Difference_Year1']), i):
            base_list.append(seq)    

    final_list=[]    
    for i in base_list:
        if(len(i)==2):
            if(i[0][1]+i[1][1])==0:
                final_list.append(i)  
        if(len(i)==3):
            if(i[0][1]+i[1][1]+i[2][1])==0:
                final_list.append(i)
    
    matches_2=None
    if(len(final_list)!=0):
        index_list=[]
        for i in final_list:
            index_tuple=()
            for j in i:
                index_tuple=index_tuple+tuple([j[0]])
            index_list.append(index_tuple)

        LineItem=[]
        for i in index_list:
            temp_list=[]
            for j in i:
                temp_list.append(temp0.iloc[j,].to_string(index=False))
            LineItem.append(temp_list)
        
        matches_2=pd.DataFrame( LineItem)
        matches_2.rename(columns={matches_2.columns[0]:'LineItem1',
                        matches_2.columns[1]:'LineItem2',
                        matches_2.columns[2]:'LineItem3'}, inplace = True)

    return(df,matches_2)

def comparePL(groundTruth_PL,predicted_PL):
    groundTruth_PL=groundTruth_PL.assign(Predicted_Year1=predicted_PL['Year1'])
    groundTruth_PL=groundTruth_PL.assign(Predicted_Year2=predicted_PL['Year2'])
    groundTruth_PL=clean(groundTruth_PL)

    groundTruth_PL['Difference_Year1']=round(groundTruth_PL.loc[:,'Year1'] - groundTruth_PL['Predicted_Year1'],0)
    groundTruth_PL['Difference_Year2']=round(groundTruth_PL.loc[:,'Year2'] - groundTruth_PL['Predicted_Year2'],0)

    comparePL_df_y1=groundTruth_PL[abs(groundTruth_PL['Difference_Year1'])>0]
    comparePL_df_y1.rename(columns={'Year1':'GroundTruth','Predicted_Year1':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    comparePL_df_y1=comparePL_df_y1[['LineItem','GroundTruth','Predicted','Difference']]

    comparePL_df_y2=groundTruth_PL[abs(groundTruth_PL['Difference_Year2'])>0]
    comparePL_df_y2.rename(columns={'Year2':'GroundTruth','Predicted_Year2':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    comparePL_df_y2=comparePL_df_y2[['LineItem','GroundTruth','Predicted','Difference']]

    groundTruth_PL.rename(columns={'Year1':'GroundTruth_Year1','Year2':'GroundTruth_Year2'}, inplace = True)
           
    return(comparePL_df_y1,comparePL_df_y2,groundTruth_PL)

def compareBS(groundTruth_BS,predicted_BS):
    groundTruth_BS=groundTruth_BS.assign(Predicted_Year1=predicted_BS['Year1'])
    groundTruth_BS=groundTruth_BS.assign(Predicted_Year2=predicted_BS['Year2'])

    groundTruth_BS=clean(groundTruth_BS)

    groundTruth_BS['Difference_Year1']=round(groundTruth_BS.loc[:,'Year1'] - groundTruth_BS['Predicted_Year1'],0)
    groundTruth_BS['Difference_Year2']=round(groundTruth_BS.loc[:,'Year2'] - groundTruth_BS['Predicted_Year2'],0)

    compareBS_df_y1=groundTruth_BS[abs(groundTruth_BS['Difference_Year1'])>0]
    compareBS_df_y1.rename(columns={'Year1':'GroundTruth','Predicted_Year1':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    compareBS_df_y1=compareBS_df_y1[['LineItem','GroundTruth','Predicted','Difference']]

    compareBS_df_y2=groundTruth_BS[abs(groundTruth_BS['Difference_Year2'])>0]
    compareBS_df_y2.rename(columns={'Year2':'GroundTruth','Predicted_Year2':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    compareBS_df_y2=compareBS_df_y2[['LineItem','GroundTruth','Predicted','Difference']]

    groundTruth_BS.rename(columns={'Year1':'GroundTruth_Year1','Year2':'GroundTruth_Year2'}, inplace = True)
    
    groundTruth_BS,match2=FindIssues(groundTruth_BS)
    return(compareBS_df_y1,compareBS_df_y2,groundTruth_BS,match2)

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

        groundTruth_PL=groundTruth.loc[:, 'LineItem':'Year2']
        groundTruth_PL=groundTruth_PL.iloc[23:85,:]
        groundTruth_BS = groundTruth.loc[:, 'LineItem':'Year2']
        groundTruth_BS=groundTruth_BS.iloc[88:227,:]

        groundTruth_BS=groundTruth_BS.reset_index(drop=True)
        groundTruth_PL=groundTruth_PL.reset_index(drop=True)


    if (groundTruth is None and predicted is not None) or (groundTruth is not None and predicted is not None):
        predicted.rename(columns={predicted.columns[4]: "LineItem",
        predicted.columns[5]: "Year1",
        predicted.columns[6]: "Year2",}, inplace = True)
        '''
        1) Predicted PL - subsetting PL from the Accounts sheet
        2) Predicted BS - subsetting BS from the Accounts sheet

        '''   
        predicted_PL=predicted.loc[:, 'LineItem':'Year2']
        predicted_PL=predicted_PL.iloc[23:85,:]
        predicted_BS =predicted.loc[:, 'LineItem':'Year2']
        predicted_BS=predicted_BS.iloc[88:227,:]

        predicted_BS=predicted_BS.reset_index(drop=True)
        predicted_PL=predicted_PL.reset_index(drop=True)

    
    if predicted is None:
        predicted_PL=None
        predicted_BS=None
    if groundTruth is None:
        groundTruth_PL=None
        groundTruth_BS=None
 
    return(groundTruth_BS,groundTruth_PL,predicted_BS,predicted_PL)

def reshape_agg(df,Year):
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

def comparePL_agg(groundTruth_PL,predicted_PL):
    groundTruth_PL=groundTruth_PL.assign(Predicted_Year1=predicted_PL['Year1'])
    groundTruth_PL=groundTruth_PL.assign(Predicted_Year2=predicted_PL['Year2'])
    groundTruth_PL=clean(groundTruth_PL)

    groundTruth_PL['Difference_Year1']=round(groundTruth_PL.loc[:,'Year1'] - groundTruth_PL['Predicted_Year1'],0)
    groundTruth_PL['Difference_Year2']=round(groundTruth_PL.loc[:,'Year2'] - groundTruth_PL['Predicted_Year2'],0)

    comparePL_df_y1=groundTruth_PL[abs(groundTruth_PL['Difference_Year1'])>0]
    comparePL_df_y1.rename(columns={'Year1':'GroundTruth','Predicted_Year1':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    comparePL_df_y1=comparePL_df_y1[['LineItem','GroundTruth','Predicted','Difference']]

    comparePL_df_y2=groundTruth_PL[abs(groundTruth_PL['Difference_Year2'])>0]
    comparePL_df_y2.rename(columns={'Year2':'GroundTruth','Predicted_Year2':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    comparePL_df_y2=comparePL_df_y2[['LineItem','GroundTruth','Predicted','Difference']]

    groundTruth_PL.rename(columns={'Year1':'GroundTruth_Year1','Year2':'GroundTruth_Year2'}, inplace = True)
           
    return(comparePL_df_y1,comparePL_df_y2,groundTruth_PL)

def comparePL_agg(groundTruth_BS,predicted_BS):
    groundTruth_BS=groundTruth_BS.assign(Predicted_Year1=predicted_BS['Year1'])
    groundTruth_BS=groundTruth_BS.assign(Predicted_Year2=predicted_BS['Year2'])

    groundTruth_BS=clean(groundTruth_BS)

    groundTruth_BS['Difference_Year1']=round(groundTruth_BS.loc[:,'Year1'] - groundTruth_BS['Predicted_Year1'],0)
    groundTruth_BS['Difference_Year2']=round(groundTruth_BS.loc[:,'Year2'] - groundTruth_BS['Predicted_Year2'],0)

    compareBS_df_y1=groundTruth_BS[abs(groundTruth_BS['Difference_Year1'])>0]
    compareBS_df_y1.rename(columns={'Year1':'GroundTruth','Predicted_Year1':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    compareBS_df_y1=compareBS_df_y1[['LineItem','GroundTruth','Predicted','Difference']]

    compareBS_df_y2=groundTruth_BS[abs(groundTruth_BS['Difference_Year2'])>0]
    compareBS_df_y2.rename(columns={'Year2':'GroundTruth','Predicted_Year2':'Predicted','Difference_Year1':'Difference'}, inplace = True)
    compareBS_df_y2=compareBS_df_y2[['LineItem','GroundTruth','Predicted','Difference']]

    groundTruth_BS.rename(columns={'Year1':'GroundTruth_Year1','Year2':'GroundTruth_Year2'}, inplace = True)
    
    return(compareBS_df_y1,compareBS_df_y2,groundTruth_BS)

def onetomany(df):
    df=df.set_index('excelmapping').T.to_dict('list')
    print(df)
    return df
