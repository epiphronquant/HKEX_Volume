# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 09:53:20 2022

@author: Angus
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import investpy
import yfinance as yf
import datetime as dt

st.set_page_config(layout="wide")
st.title('HKEX Volume Analysis')

@st.cache(ttl= 1800) ## Data would need to get reloaded every 30 minutes
def load_data(link):
    df = pd.read_excel(link,sheet_name='Sheet1', header = 0, engine = 'openpyxl', parse_dates = False)
    return df
link = r'Volume.xlsx'
df = load_data(link)

### select sector, select main board, 18A listed 
column_1, column_2,column_3 = st.columns(3) ### Divides page into 2 columns
with column_1:## dropdown box for sector selection
    sectors = df['Sector']
    sectors = sectors.tolist()
    sectors = list(dict.fromkeys(sectors))
    # healthcare = sectors [3]
    sectors.append('All')### adds an option for All IPOs
    sectors.remove ('Healthcare')
    sectors.append('Healthcare') 
    sectors = sectors [::-1]
    sector = st.selectbox(
        'Which sector are you interested in?',
          sectors)
    'You selected: ', sector
    if sector == 'All':
        pass
    else:
        df = df.loc[df['Sector'] == sector]
        
with column_2: ### Dropdown box for filtering board/boards
    boards = ['Main Board',  'Both', 'GEM']
    board = st.selectbox(
        'Which board are you interested in?',
          boards)
    'You selected: ', board
    if board == 'Main Board': 
        df = df.loc[df['Main Board'] == 1]
    elif board == 'GEM':
        df = df.loc[df['Main Board'] == 0]
    else:
        df = df
with column_3: ### Dropdown box for filtering whether company is 18A or Not
    biotech_listings = ['18A Listed', 'All', 'Not 18A Listed']
    biotech_listing = st.selectbox(
        'Which type of listing are you interested in?',
          biotech_listings)
    'You selected: ', biotech_listing
    if biotech_listing == '18A Listed': 
        df = df.loc[df['18A Listed'] == 1]
    elif biotech_listing == 'Not 18A Listed':
        df = df.loc[df['18A Listed'] == 0]
    else:
        df = df

### chart 1 that shows data on stock price and volume 
# filter data for chart 1      
companies = df['Stock Name']
companies = companies.tolist()
companies = list(dict.fromkeys(companies))
tickers = df['Stock Code']
tickers = tickers.tolist()
tickers = list(dict.fromkeys(tickers))
companies.extend(tickers)
company = st.selectbox( ### can select tickers and company name for individual company chart
    'Which company/stock code are you interested in?',
      companies)
'You selected: ', company

if type(company) == int: ## if input is a ticker
    company = df.loc[df['Stock Code'] == company, 'Stock Name'] 
    company = company.iloc[0]

else:
    pass  

### function that appends average trading days column to df given number of days in a list and respective column
def average_trading (df2, trading_days, column_of_interest):
    #input dataframe that includes a column named "column_of_interest"(str) that includes respective data (df), number of observations to average (int)
    #output, dataframe with calculated volume data (df)
    df_vol = df2 [column_of_interest]
    df3 = df_vol.rolling(trading_days, min_periods=trading_days).mean() ### this function is key to calculating trading days
    df3 = df3.rename("Average " + str (trading_days) + " Trading Days "+ column_of_interest)
    df2 = pd.concat ([df2, df3], axis = 1)
    return df2

@st.cache(ttl= 1800, allow_output_mutation=True) ## input holds for 30 mins before getting refreshed
def chart_1 (company, df):
    ticker = df.loc[df['Stock Name'] == company]
    ticker = ticker ['Yf Ticker']
    ticker = list (ticker )
    ticker = ticker [0]
    
    # download and calculate data for chart 1
    df2 = yf.download(ticker, period = 'max')   
    
    # visualize chart 1
    fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
    fig.add_trace(go.Scatter(x= df2.index, y= df2 ['Adj Close'], name= 'Adjusted Close' ),
        secondary_y=False)
    
    trading_days = [20, 40, 60] ### trading days that are being calculated
    for day in trading_days:
        df2 = average_trading(df2, day, 'Volume')
        fig.add_trace(go.Scatter(x = df2.index, y= df2['Average '+str (day) +' Trading Days Volume'], name= 'Average '+str (day) +' Trading Days Volume'),
                      secondary_y=True)
        # Add figure title
    fig.update_layout(title_text= company + ' Price and Average Volume Chart')
        # Set x-axis title
    fig.update_xaxes(title_text="Date")
        # Set y-axes titles
    fig.update_yaxes(title_text= 'Adjusted Closing Price', secondary_y=False)
    fig.update_yaxes(title_text="Volume", secondary_y=True)
    return fig

fig = chart_1(company, df)
st.plotly_chart(fig, use_container_width=True)

### filter data by industry using dropdown box
industries = df['Industry']
industries = industries.tolist()
industries = list(dict.fromkeys(industries))
 # healthcare = sectors [3]
industries.append('All')### adds an option for All IPOs
try:
    industries.remove ('Biotechnology')
    industries.append('Biotechnology') 
except ValueError:
    pass
industries = industries [::-1]
industry = st.selectbox(
    'Which Industry are you interested in?',
      industries)
'You selected: ', industry

if industry == 'All':
    pass
else:
    df = df.loc[df['Industry'] == industry]


# df为要分析的结果的数据, This is code for making the homemade index
def homemade_index(df, column):
    ### input a dataframe with a column 'Yf Ticker', 'Stock Name' and 'Mkt Cap (Jul 8)', and a column of interest (str)
    ### output a dataframe showing the homemade index value###    
    df0 = df.copy()
    
    ## develop code for homemade index based on mkt cap
    #### This was for generating the index ret sheet in the index_correlations project ######
    ## need to gather all the tickers and calculate the returns
    # 构造表格1
    etl_col=df['Yf Ticker'].tolist()
    # etl_col=['2157.HK','2185.HK','2257.HK']
    # 成功下载的
    etl_col_2=[]
    df_1 = pd.DataFrame()
    for i, col in enumerate(etl_col):  ### this can be modified to download tickers faster. yf.download has threading when everything is inputted at once
        try:
            print('下载进度{}/{}'.format(i+1,len(etl_col)))
            tmp_t = yf.download(col,period = 'max')[column]
            tmp_t = tmp_t.replace(to_replace=0,method='ffill') ## replaces 0 volume with previous day volume
            etl_col_2.append(col)
            df_1 = pd.concat([df_1, tmp_t], axis=1)
        except Exception as e:
            pass
    df_1.columns = [col + ' ' + column for col in etl_col]
    df_1.index = df_1.index.map(lambda x: str(x)[0:10])
    df_1.sort_index(inplace=True)
    # df_1
    
    
    # 构建表格2，求return，计算每个return
    df_2 = pd.DataFrame()
    for col in df_1.columns:
        df_2[col + ' Return'] = df_1[col].shift(-1) / df_1[col] - 1
    # df_2
    
    #
    # 第三表需要拆成2张表3——1，修改  公司  weigh。
    # 3——2  日期。 公司1比例 公司2比例 公司三比例 横加起来为1
    all_mkt = df0['Mkt Cap (Jul 8)'].sum()
    df_3 = df0.groupby('Stock Name')['Mkt Cap (Jul 8)'].sum() / all_mkt * 100
    # df_3
    
    # 构造一个新的df
    mydict1 = {}
    mydict2 = {}
    stick_name = df0['Stock Name'].tolist()
    Yf_Ticker = df0['Yf Ticker'].tolist()
    mkt = df0['Mkt Cap (Jul 8)'].tolist()
    for k, v in zip(stick_name, mkt):
        mydict1[k] = v
    for k, v in zip(Yf_Ticker, stick_name):
        mydict2[k] = v
    
    
    # df_4 计算市场比重,如果收益不为空
    df_2_flag = df_2.notna() * 1
    # print(df_2_flag)
    ret = []
    i = 0
    for time in df_2.index:
        TT = []
        # 找到不为0的公司名称
        TT.append(time)
    
        # 处理每一类列
        tt = df_2.loc[time, :]
        for elem in tt.index:
            # 解析出来Yf Ticker
            ticker_name = elem.split(' ')[0]
            # 获取器对应的市场规模
    
            if df_2_flag.loc[time,elem]==0:
                TT.append(0)
            else:
                value = mydict1.get(mydict2.get(ticker_name, 0), 0)
                TT.append(value)
        # 计算比重
        if sum(TT[1:]) != 0:
            TT[1:] = [elem / sum(TT[1:]) * 100 for elem in TT[1:]]
        else:
            TT[1:] = [0] * len(TT[1:])
        ret.append(TT)
    df_4 = pd.DataFrame(ret, columns=['time'] + [mydict2.get(elem.split(' ')[0], 0) for elem in df_2.iloc[0].index])
    df_4=df_4.set_index('time')
    df_4.sort_index(inplace=True)
    # df_4
         
    # 计算对应的return all
    df_3_flag = df_2.notna() * 1
    ret = []
    i = 0
    start=100
    for i,time in enumerate(df_2.index):
        TT = []
        TT.append(time)
        all_return=0
        # 处理每一类列
        tt = df_2.loc[time, :]
        for  j,_ in enumerate(tt.index):
            # 解析出来Yf Ticker
            #计算总收入
            b1=df_4.iloc[i,j]  #比重
            b2=df_2.fillna(0).iloc[i,j] #df_2
    
            all_return=all_return+b1*b2
        #print(i,j,all_return)
        TT.append(all_return)
        TT.append(start)
        start=start*(1+TT[1]/100)
        ret.append(TT)
    df_5 = pd.DataFrame(ret, columns=['time'] + ['homemade_index','Return%'])
    df_5.set_index('time')
    df_5.sort_index(inplace=True)
    return df_5

@st.cache(ttl= 1800, allow_output_mutation=True) ## input holds for 30 mins before getting refreshed
def chart_2 (df):
    # download and calculate data for chart 2
    df2 = homemade_index(df, 'Adj Close')
    
    # visualize chart 2
    fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
    fig.add_trace(go.Scatter(x= df2 ['time'], y= df2 ['Return%'], name= 'Adjusted Close' ),
        secondary_y=False)
    
    df2 = homemade_index(df, 'Volume')
    trading_days = [20, 40, 60] ### trading days that are being calculated
    for day in trading_days:
        df2 = average_trading(df2, day, 'Return%')
        fig.add_trace(go.Scatter(x = df2 ['time'], y= df2['Average '+str (day) +' Trading Days Return%'], name= 'Average '+str (day) +' Trading Days Volume'),
                      secondary_y=True)
        # Add figure title
    fig.update_layout(title_text= industry + ' Homemade Index Price and Average Volume Chart')
        # Set x-axis title
    fig.update_xaxes(title_text="Date")
        # Set y-axes titles
    fig.update_yaxes(title_text= 'Adjusted Closing Price Index', secondary_y=False)
    fig.update_yaxes(title_text="Volume Index", secondary_y=True)
    return fig
fig = chart_2(df)
st.plotly_chart(fig, use_container_width=True)

#### mkt cap slider
## lower and higher end of market cap, need to adjust units into maybe 100M or B HKD
df ['Mkt Cap (Jul 8) 100M'] = df ['Mkt Cap (Jul 8)']/ 100000000
df['Mkt Cap (Jul 8) 100M'] = df['Mkt Cap (Jul 8) 100M'].astype(float)

min_mktcap = df ['Mkt Cap (Jul 8) 100M'].min()
max_mktcap = df ['Mkt Cap (Jul 8) 100M'].max()

## the slider and selecting relevant data
slider = st.slider('Select Market Cap in 100M', min_value=min_mktcap, value=(float(min_mktcap),float(max_mktcap)), max_value=max_mktcap)
lower_mktcap = slider [0]
upper_mktcap = slider [1]

## info bar showing selected market caps
st.info('Lower: **' + str(lower_mktcap) + '** Higher: **' + str(upper_mktcap) +'**') ### info bar

## filter data by  market cap
df = df[(df['Mkt Cap (Jul 8) 100M'] >= lower_mktcap) & (df['Mkt Cap (Jul 8) 100M'] <= upper_mktcap)] ### filter the data

### display df with filtered data and appropriate data
tickers = df ['Yf Ticker']
tickers = tickers.to_list()
df2  = yf.download(tickers,period = 'max') ['Volume'] ### this could be referenced with the dataset used for homemade_index()
df3 = df [['Yf Ticker', 'Stock Name', 'Stock Name CN', 'Mkt Cap (Jul 8) 100M']]

df88 = []
for ticker in tickers:
    df8 = [ticker]
    trading_days = [20,40,60]
    for day in trading_days:
        df4 = df2 [ticker]
        df5 = df4.iloc[-day:]
        df5 = df5.mean()
        df8.append(df5)
    df88.append (df8)
columns = ['Yf Ticker', '20 TD Avg Vol', '40 TD Avg Vol', '60 TD Avg Vol']
df88 = pd.DataFrame(df88, columns = columns)
df3 = df3.merge(df88, left_on='Yf Ticker', right_on='Yf Ticker')
df3 

### Chart 3: same charting excerise with homemade index and display
@st.cache(ttl= 1800, allow_output_mutation=True) ## input holds for 30 mins before getting refreshed
def chart_3 (df):
    # download and calculate data for chart 3
    df2 = homemade_index(df, 'Adj Close')
    
    # visualize chart 3
    fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
    fig.add_trace(go.Scatter(x= df2 ['time'], y= df2 ['Return%'], name= 'Adjusted Close' ),
        secondary_y=False)
    
    df2 = homemade_index(df, 'Volume')
    trading_days = [20, 40, 60] ### trading days that are being calculated
    for day in trading_days:
        df2 = average_trading(df2, day, 'Return%')
        fig.add_trace(go.Scatter(x = df2 ['time'], y= df2['Average '+str (day) +' Trading Days Return%'], name= 'Average '+str (day) +' Trading Days Volume'),
                      secondary_y=True)
        # Add figure title
    fig.update_layout(title_text= industry + ' '+ str(lower_mktcap) + ' - ' + str(upper_mktcap) + ' 100M HKD Mkt Cap Homemade Index Price and Average Volume Chart')
        # Set x-axis title
    fig.update_xaxes(title_text="Date")
        # Set y-axes titles
    fig.update_yaxes(title_text= 'Adjusted Closing Price Index', secondary_y=False)
    fig.update_yaxes(title_text="Volume Index", secondary_y=True)
    return fig
fig = chart_3(df)
st.plotly_chart(fig, use_container_width=True)
