from fuzzywuzzy import fuzz
temp0="Deferred income tax asset"
temp0=temp0.lower()

temp1="Deferred charges"
temp1=temp1.lower()

temp2="Deferred Tax Asset"
temp2=temp2.lower()

print(fuzz.token_sort_ratio(temp0,temp1)) #incorrect
print(fuzz.token_sort_ratio(temp0,temp2)) #correct

                    temp=[]
                    if type(match_LineItem[list(data.keys())[0]] is list):
                        match_LineItem[list(data.keys())[0]].append(matches.loc[j,'LineItem'])
                    else:
                        match_LineItem[list(data.keys())[0]] = [match_LineItem[list(data.keys())[0]]]
                        [match_LineItem[list(data.keys())[0]]].append(matches.loc[j,'LineItem'])