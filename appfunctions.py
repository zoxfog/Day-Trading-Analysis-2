
import os 

import pandas as pd
import datetime
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt #for data visualization

import appfunctions as ap




# calculates bar vwap and adds it to the data.
def addVwap (data=None):

    price = 0
    vwap = 0
    sum_volume = 0
    sum_price_times_volume = 0
    data['VWAP'] = None
            
    for i, row in data.iterrows():
        price = (row['High'] + row['Low'] + row['Close'])/3
        sum_volume+=row['Volume']
        sum_price_times_volume += price*row['Volume']
                
        #get an approximation
        if sum_volume ==0:
            sum_volume = 0.0001
                    
        vwap = float(sum_price_times_volume/sum_volume)

        data.loc[i:i,"VWAP"] = round(vwap,3)


    return  data 


#calculate gap percent change of a given trading day and add it to the data
def addGap(data):  
    data["Gap"]=None
    length = len(data)
    data_copy = data.copy()
    while length>1:
        temp = data_copy[:length]
        gap_data = temp.tail(2).reset_index()
        gap =(gap_data['Open'][1] - gap_data['Close'][0])
        gap_percent = (gap/gap_data['Close'][0])*100
        
        length = length-1
        data.loc[length,"Gap"]=float(gap_percent)
        
    return data


#get an assets bar relative volume
#period (optional): the period for calculating the average for the relative volume ratio, default is 9.
def addRelativeVolume(data,period = None): 
    if period is None:
        period = 9
    data["RV"]=None
    length = len(data)
    while(length >0):
        temp = data[:length]
        
        temp = temp.tail(period)

        bar_volume = temp['Volume'].values[-1]
        data_mean = temp['Volume'].mean()
        
        #if is 0 get an approximation
        if data_mean == 0 :
            data_mean = 0.0001

        #calculate the price change and round the result
        rv =round(bar_volume/data_mean,3)

        length=length-1
        data.loc[length,"RV"]=float(rv)
    return data



# Classify the bar of a given time with a matching bar tag resembling its appearance.
#period (optional): changes the default period to a custom one
def addBarTag(data,date=None, time = None, period = None): 
    
    if period is None:
        period = 30 
        
    data["Bar Tag"] = None           

    # create a copy to avoid aliasing
    data_copy = data.copy()
    # Get open-close ranges
    data_copy['OC Range'] = data_copy.apply(lambda x: abs(x['Open']-x['Close']),axis = 1)
    # Get high-low ranges
    data_copy['HL Range'] = data_copy.apply(lambda x: abs(x['High']-x['Low']),axis = 1)
    
    length = len(data_copy)
    
    while length>0:  
    
        temp = data_copy[:length]   
        temp = temp.tail(period)
    

        selected_bar= temp.iloc[-1].copy()
        
        OC_mean = temp['OC Range'].mean()
        HL_mean = temp['HL Range'].mean()
        
        # avoid getting 0 by getting an approximation 0.0001
        if selected_bar['OC Range']==0:
            selected_bar['OC Range'] = 0.0001
        if selected_bar['HL Range']==0:
            selected_bar['HL Range'] = 0.0001
            
        if OC_mean == 0:
            OC_mean =0.0001
        if HL_mean == 0:
            HL_mean =0.0001

        
        open_close_r =selected_bar['OC Range']/OC_mean
        high_low_r = selected_bar['HL Range']/HL_mean

        High = selected_bar['High']
        Low = selected_bar['Low']
        Open = selected_bar['Open']
        Close = selected_bar['Close']
         
        mid_range = (High-Low)/2 + Low 
        quarter_range = (High-Low)/4 + Low
        three_quarter_range = 3*(High-Low)/4 + Low
        low_of_range = (High-Low)*0.1 + Low 
        high_of_range = (High-Low)*0.9 + Low 
            
        if Open < Close:
            if Open>mid_range and Close>three_quarter_range and high_low_r >0.9:
                candle = "strong green pinbar"
            elif Open>mid_range and Close>mid_range:
                candle = "green pinbar"
            elif (Open<= low_of_range and Close>=high_of_range and open_close_r>0.7) or (Open<= quarter_range and Close>=three_quarter_range and open_close_r>1.5):
                    candle = 'strong green bar'
                    
            elif (Open<=mid_range) and (Close<=quarter_range) and (high_low_r >= 1):
                candle = 'bearish green bar'
            else: 
                candle = 'green bar'
        else:
            if (Close<quarter_range) and (Open<mid_range) and (high_low_r >0.9):
                candle = "strong red pinbar"
            elif (Close<mid_range) and (Open<mid_range):
                candle = "red pinbar"
            elif (Close<=low_of_range and Open>=high_of_range and open_close_r>0.7) or (Close<=quarter_range and Open>=three_quarter_range and open_close_r>1.5):
                    
                candle = "strong red bar"
                
            elif (Close>= three_quarter_range) and (Open>=three_quarter_range  ) and (high_low_r>=1):
                candle = "bullish red bar"
            else:
                candle = "red bar"
            
        length = length-1

        data.loc[length,"Bar Tag"]=candle

    return data


# FILL 
def fillMissingBar(data):
    
    # generate a full 390 390 bars per day generic data frame for outer merge
    s1= pd.DataFrame(columns = ["Time"])


    time = datetime.time(9,30)

    while time<datetime.time(16,0):
        s1=s1.append({'Time': time}, ignore_index=True)
    
        time = datetime.datetime.combine(datetime.date(2000,1,1),time)
        time = time + datetime.timedelta(minutes = 1)
        time = time.time()
    data = data.merge(s1, on =["Time"],how = "outer")
    
    data=data.sort_values(by=["Time"]).reset_index()
    
    for index, row in data.iterrows():
        i = 1   
        j = 1
        
        #if is first minute of the trading day smooth most of the information with the following bar
        # ,0 for volume related columns and "green bar" as a default bar.
        if np.isnan(row["Open"]):

            if row["Time"]==datetime.time(9,30):

                while np.isnan(data.loc[index+i,"Open"]):
                    i = 1+i


                data.loc[index,"Open"] = data.loc[index+i,"Open"]
                data.loc[index,"High"] = data.loc[index+i,"Open"]
                data.loc[index,"Low"] = data.loc[index+i,"Open"]
                data.loc[index,"Close"] = data.loc[index+i,"Open"]
                data.loc[index,"VWAP"] = data.loc[index+i,"VWAP"]    
                data.loc[index,"Date"] = data.loc[index+i,"Date"] 
                data.loc[index,"Symbol"] = data.loc[index+i,"Symbol"] 
    
            else :
                while np.isnan(data.loc[index-i,"Open"]):
                    i = 1+i
        
                data.loc[index,"Open"] = data.loc[index-i,"Close"]
                data.loc[index,"High"] = data.loc[index-i,"Close"]
                data.loc[index,"Low"] = data.loc[index-i,"Close"]
                data.loc[index,"Close"] = data.loc[index-i,"Close"]
                data.loc[index,"VWAP"] = data.loc[index-i,"VWAP"]
                data.loc[index,"Date"] = data.loc[index-i,"Date"]
                data.loc[index,"Symbol"] = data.loc[index-i,"Symbol"]


        
            data.loc[index,"Bar Tag"] = "no action"
            data.loc[index,"Volume"] = 0
            data.loc[index,"RV"] = 0

    return data


# Create subplots and mention plot grid size

# period 'Time' or 'Date', default is 'Time'
def graphViz (data,period = "Time",volume_period = 9, start=None, end=None, point_list = None):
    
    df = data.copy()
        
    if start is not None:
        df = df[df[period]>=start]
    if end is not None:
        df = df[df[period]<=end]
        
    # create subplots with 2 rows, one for OHLC and one for volume   
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
            vertical_spacing=0.03, subplot_titles=('', 'Volume'), 
            row_width=[0.3, 0.7])

    # Plot OHLC first row subplot
    fig.add_trace(go.Candlestick(x=df[period], open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"], name="OHLC"), 
                row=1, col=1)
    
    if period =="Time":
        fig.add_trace(go.Scatter(x=df[period],y = df["VWAP"],mode='lines',name='VWAP'),
                      row=1,col=1)

    # add a trace for volume in a different subplot
    fig.add_trace(go.Bar(x=df[period], y=df['Volume'],name = "Volume"), row=2, col=1)
    
    df['Volume Average'] = df['Volume'].rolling(window=volume_period ,min_periods=1).mean()

    # add average volume
    fig.add_trace(go.Scatter(x=df[period], y=df['Volume Average'],
                             name = str(volume_period) + " Volume Average"), row=2, col=1)

    if period=="Time":
    	symbol_and_date = df["Symbol"].values[0]+" "+str(df["Date"].values[0])

    else:
    	symbol_and_date = df["Symbol"].values[0]
    # Do not show OHLC's rangeslider plot 

    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(width=1000, height=500,title={
        'text':symbol_and_date,
        'y':0.85,
        'x':0.45,
        'xanchor': 'center',
        'yanchor': 'top'})
    
    if point_list is not None:
    
        color_index = 0
        colors = ["orange","#8C564B","#AB63FA","#7F7F7F","3B6E880","#E377C2","#B68E00"]
        for p in point_list:
            points = pd.DataFrame(columns = ["Time","Price","Point"])
            if p =="SL":
                color = 'black'
                shape = "arrow-bar-right"
                time = data["Entry Time"].head(1).values[0]
                
            else:
                if p == "Entry":
                    color = "blue"
                    shape = 'arrow-right'
                elif p =="Exit":
                    color = "yellow"
                    shape = 'arrow-left'
                else:
                    color = colors[color_index]
                    shape = 'arrow-left'
                    color_index +=1
                    
                time = data[p+" Time"].head(1).values[0]
            price = data[p].head(1).values[0]
            d = {"Time":  time, "Price": price, "Point": p}
            points = points.append(d, ignore_index=True)
            fig.add_trace(go.Scatter(x=points["Time"], y=points['Price'],text = points["Point"],name = p
                            ,mode="markers",marker_symbol  =shape,marker_color = color, marker_size=10)
                                    , row=1, col=1)

    if period == "Date":       
        fig.update_layout(xaxis={'type': 'category'})

    fig.show()


def disPlot(col,data):
    
    data1 = data.sort_values(by  = [col]).copy()
    sns.set_style("whitegrid")
    f,axes=plt.subplots(1,3,figsize=(15,6))
    f.suptitle(col,fontsize=22)
    g1 = sns.countplot(x=col,data=data1,ax=axes[0])
    f.subplots_adjust(hspace=0.2)
    f.subplots_adjust(wspace=0.4)



    #plot 2

    
    g2 =sns.boxplot(x=col, y="Potential R", data=data1,ax=axes[1],showmeans=True)
    
    if len(data1[col].unique())>=5:
        for i in data1[col].values:
            if len(i)>=6:
                axes[0].tick_params(axis='x',labelrotation=75)
                axes[1].tick_params(axis='x',labelrotation=75)
                break
                
    #plot 3 
    size = 0.5
    

    outer = data1[[col,'Num']].groupby(col).count().sort_index()
    

    inner = data1[[col,'Potential R bins','Num']].groupby([col,'Potential R bins']).count().sort_index()
    x = data1[[col,'Potential R bins','Num']].groupby([col,'Potential R bins']).agg({'Potential R bins': 'sum'})
    
    x_pcts = inner.groupby(level=0).apply(lambda x:round(100 * x / float(x.sum()),2))

    inner_percent = x_pcts['Num'].values

    inner_percent = [str(x)+"%" for x in inner_percent]
    colors  = ['lemonchiffon','khaki','gold','darkgoldenrod','chocolate','maroon']

    
    inner_labels = inner.index.get_level_values(1)

    colors = colors[:len(inner_labels.unique())]
    
    axes[2].pie(outer.values.flatten(), radius=1.5,
           labels=outer.index,
           autopct='%1.1f%%',
            pctdistance = 1.1,
            labeldistance = 1.2,
           wedgeprops=dict(width=0.5, edgecolor='w'))


    ax2=axes[2].pie(inner.values.flatten(), radius=1.5-size, 
            labels = inner_percent,
            colors = colors,

            labeldistance = 0.7,
           wedgeprops=dict(width=0.7, edgecolor='w'))
    axes[2].legend(ax2[0],inner_labels.unique(),loc = (1,1))

    plt.show()
        

    
    
def regPlot(col,data):
    
    fig,ax = plt.subplots(1,3 ,figsize = (20,7))
    fig.subplots_adjust(wspace=0.6)
    fig.suptitle(col,fontsize = 22)


    #ax[0] = sns.regplot(x=col, y="Exit R", data=data,ax = ax[0],x_jitter=.2, color = "g")

    ax[0] = sns.regplot(x=col, y="Potential R", data=data,ax = ax[0],x_jitter=.2, color = "y")


    #ax[2] = sns.violinplot(x="Outcome", y=col,data=data,cut = 0,ax = ax[2])
    ax[1] = sns.barplot(x=col, y="Potential R bins", data=data,ax=ax[1])

    
    
    ax[2] = sns.distplot(a=data[[col]],bins = 20,ax = ax[2])
    #ax[3].set_xticks(np.arange(0,20,2))

    ax[2].set_ylabel('density')
    ax[2] = ax[2].set_xlabel(col)