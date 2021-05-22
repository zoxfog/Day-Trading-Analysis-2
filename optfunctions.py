#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
import datetime
import os


# ### o1- Simple Set and Forget with k-R

# In[4]:


# merged : the mergeddataframe with all the tables (including the 1 minute bars)
# simple set and forget

def o1(data,k,merged):

    k = round(k,1)
    
    data["o1-"+str(k) ] = 0
    data["o1-"+str(k)+ " R"] = 0
    data["o1-"+str(k) + " Time"]=  0

    q1 = merged[(merged["Entry Time"]<=merged["Time"])].copy()


    for num in data["Num"].unique():
    
        q2 = q1[q1["Num"] ==num].reset_index()

    
        flag_above_limit = 0
        potential = 0
        potential_index = 0
        for index, row in q2.iterrows():


            if row["High R"]>potential:
                potential = row["High R"]

                
                if potential>=k:
                    potential =k
                    break

            if (row["Low"]<=row["SL"] and index>=1) or (row["Entry Time"]==row["Exit Time"]):
                potential = -1
                
                break
                
                
            if row["Time"]==datetime.time(15,55):
                potential = row["Close R"]
                break

        if potential== -1:
            
            data.loc[data["Num"]==num,"o1-"+str(k) ]= q2.loc[index,"SL"]
            data.loc[data["Num"]==num,"o1-"+str(k) + " R"] = potential
            data.loc[data["Num"]==num,"o1-"+str(k)+ " Time"] = q2.loc[index,"Time"]
            
        elif potential !=k:

            data.loc[data["Num"]==num,"o1-"+str(k) ]= q2.loc[index,"Close"]
            data.loc[data["Num"]==num,"o1-"+str(k) + " R"] = potential
            data.loc[data["Num"]==num,"o1-"+str(k)+ " Time"] = q2.loc[index,"Time"]
            
        else:
            exit_at_k = abs(q2.loc[index,"Entry"]-q2.loc[index,"SL"])*k+q2.loc[index,"Entry"]
            data.loc[data["Num"]==num,"o1-"+str(k) ]= exit_at_k
            data.loc[data["Num"]==num,"o1-"+str(k) + " R"] = potential
            data.loc[data["Num"]==num,"o1-"+str(k)+ " Time"] = q2.loc[index,"Time"]
            
            
            
            
        
        
    mean = data["o1-"+str(k) + " R"].mean()
    std = data["o1-"+str(k) + " R"].std()
    median = data["o1-"+str(k)+ " R"].median()

    return [mean,median,std]


# ### o2- Set and forget with k-R and limit-R

# In[5]:



# notes:
#1) if a candles low is below BE and candles high is above limit,
#the result will always be BE even though the price first visited the low



def o2(data,limit,k,merged):

    k = round(k,1)
    limit = round(limit,1)

    data["o2-"+str(limit)+"-"+str(k) ] = 0
    data["o2-"+str(limit)+"-"+str(k)  + " R"] = 0
    data["o2-"+str(limit)+"-"+str(k) + " Time"]=0

    q1 = merged[(merged["Entry Time"]<=merged["Time"]) ].copy()


    for num in data["Num"].unique():
    
        q2 = q1[q1["Num"] ==num].reset_index()

    
        flag_above_limit = 0
        potential = 0
        potential_index = 0
        for index, row in q2.iterrows():


            if row["High R"]>potential:
                potential = row["High R"]

                
                if potential>=k:
                    potential =k
                    break

            #create some buffer
            if index>1:
                if potential>=limit and flag_above_limit == 0 :
                    flag_above_limit = 1

            
        
            if row["Low"]<=(row["Entry"]+0.01) and flag_above_limit == 1 :
                potential = 0
                break
            if (row["Low"]<=row["SL"] and index>=1) or (row["Exit Time"]==row["Entry Time"]):
                potential = -1
                break
            if row["Time"]==datetime.time(15,55):
                potential = row["Close R"]
                index = index
                break

        if   potential== 0:    
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k) ]= q2.loc[index,"Entry"]+0.01
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k) + " R"] = potential
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k)+ " Time"] = q2.loc[index,"Time"]
        elif potential== -1:
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k) ]= q2.loc[index,"SL"]
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k) + " R"] = potential
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k)+ " Time"] = q2.loc[index,"Time"]
        else:
            exit_at_k = abs(q2.loc[index,"Entry"]-q2.loc[index,"SL"])*k+q2.loc[index,"Entry"]
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k) ]= exit_at_k
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k) + " R"] = potential
            data.loc[data["Num"]==num,"o2-"+str(limit)+"-"+str(k)+ " Time"] = q2.loc[index,"Time"]
            
        
        
    mean = data["o2-"+str(limit)+"-"+str(k) + " R"].mean()
    std = data["o2-"+str(limit)+"-"+str(k) + " R"].std()
    median = data["o2-"+str(limit)+"-"+str(k) + " R"].median()

    return [mean,median,std]


# In[ ]:




