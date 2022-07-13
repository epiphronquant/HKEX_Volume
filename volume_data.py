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
link = r'C:\Users\Angus\OneDrive - epiphroncapital.com\文件\Research\18A Status\Volume.xlsx'
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
df

## develop code for homemade index based on mkt cap    
#### This was for generating the index ret sheet in the index_correlations project ######

## need to gather all the tickers and calculate the returns

# tickers = df ['Yf Ticker']
# ticker = ['2185.HK', '2257.HK', '2157.HK']
# df2 = yf.download(ticker, period = 'max') ['Adj Close']


# ## calculate industry return

## Create a transposed mnt ret to divide the data


# df = df [{'Industry', 'Ticker'}]
# df = df.set_index('Ticker')

# df3 = pd.read_excel(file, sheet_name = 'mnt ret', header = 0)
# df3 = df3.transpose()

# new_header = df3.iloc[0] #grab the first row for the header
# df3 = df3[1:] #take the data less the header row
# df3.columns = new_header #set the header row as the df header

# df4 = pd.concat ([df,df3], axis = 1, ignore_index = True)
# df4.rename(columns={ df4.columns[0]: "Industry" }, inplace = True)

# mnt_retT = df4

# ### create industry index
# df = pd.read_excel(file, sheet_name = sheet_name, header = header)
# df = df[{weight, 'Industry'}]
# df = df.rename({weight:'Weight'}, axis =1)

# df = df.dropna()

# df_count = df.groupby(['Industry']).count()
# df_count = df_count.rename({weight:'Count'}, axis = 1)
# df_weight = df.groupby(['Industry']).sum()
# df_weight = df_weight.rename({weight:'Weight'}, axis = 1)


# def get_index(industry, df, df_weight): ## This gathers the weights for the respective industry
#     df2 = df.loc[df['Industry'] == industry]
#     df2 = df2.set_index('Industry')
#     df3  = df_weight.loc[ [industry] , : ]
    
#     df4 = df2/df3
#     return df4

# def period_return (industry, column, df_weight, df_df, df3): ### This calculates the return for 1 period
#     df2 = df3.loc[df3['Industry'] == industry]
#     df4 = get_index(industry,df_df, df_weight)
#     df2 = df2[df2.columns[column]]
#     df2 = df2.reset_index(inplace=False, drop=True)
#     df4 = df4.reset_index(inplace=False, drop=True)
        
#     df5 = pd.concat ([df2,df4], axis = 1)
#     df6 = df5.dropna()
    
#     df7 = df6 ['Weight']
#     df8 = df7.sum()
    
#     df9 = df7/df8
    
#     df10 = df9 * df6.iloc[:,0]
#     df10 = df10.sum()
#     return df10

# industries = df_count.index.tolist()

# df88 = []

# for industry in industries:

#     periods = list(range(1,41))
    
#     df8 = [industry]
#     for period in periods:
#         df10 = period_return(industry, period, df_weight, df, df4)
#         df8.append(df10)

#     df88.append(df8)
    
# df_index = pd.DataFrame(df88)
# df_index = df_index.replace({'0':np.nan, 0:np.nan})

# df_index = df_index.set_index(df_index.columns[0])

### code for calculating Index level from Index Ret
# df.iloc[0] = 100
# df = df.reset_index()
# df ['Index'] = df ['Index Ret']
# for i in range(1, len(df)):
#     #prevent division by zero
#     if df.loc[i-1, 'Index Ret'] != 0:
#         df.loc[i, 'Index'] = df.loc[i-1, 'Index'] * (1+df.loc[i, 'Index Ret'])
# df = df.set_index ('Date')

#### mkt cap slider
## lower and higher end of market cap, need to adjust units into maybe 100M or B HKD
# start_date = df ['Listing Date▼'].iloc [0]
# start_date = start_date.date()
# end_date = df ['Listing Date▼'].iloc [-1]
# end_date = end_date.date()

## the slider and selecting relevant data
# slider = st.slider('Select Market Cap', min_value=start_date, value=(start_date,end_date) ,max_value=end_date, format=format)
# start_date = slider [0].strftime('%Y%m%d')
# end_date = slider [1].strftime('%Y%m%d')

## info bar showing selected market caps
# st.info('Start: **%s** End: **%s**' % (clean_time(slider[0]),clean_time(slider[1]))) ### info bar

## filter data by  market cap
# df = df[(df['Listing Date▼'] >= start_date) & (df['Listing Date▼'] <= end_date)] ### filter the data


### display df with filtered data and appropriate data
## build a loop taht gathers and reflects this data then builds it into a new df

### Chart 3: same charting excerise with homemade index and display
## ideally would use the same homemade index function as above and similar visualization techniques though with different code
