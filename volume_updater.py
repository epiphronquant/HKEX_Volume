###/usr/bin/env python
###  coding: utf-8

import pandas as pd

df_main = pd.read_excel(r'Volume.xlsx')

## compare with HKEX-IPO-app data
df = pd.read_excel(r'https://github.com/epiphronquant/HKEX-IPO-app/blob/main/RawData.xlsx?raw=true')

df_IPO = df[~df['Code'].isin(df_main['Yf Ticker'])] ### filters out rows in HKEX data that needs to be added to df_main
df_IPO = df_IPO[7:] ### we have to filter out tickers that have changed or gotten delisted from the RawData dataset relative to the Volume dataset
rows  = len(df_IPO)
if rows ==0: ### if there is no new data to add then skip all the code
    pass
else:
    ### clean data
    df_IPO = df_IPO[['Code', 'Name', 'Name CN', 'Industry', 'Sector', 'Market Cap(B)']] 
    df_IPO = df_IPO.dropna() ### sometimes RawData doesn't have Industry or Sector data; thus we drop it and it will automatically get added back in when we manually add it in later on
    df_IPO = df_IPO.rename(columns = {'Code':'Yf Ticker', 'Market Cap(B)':'Mkt Cap (Jul 8)', 'Name':'Stock Name', 'Name CN':'Stock Name CN'})
    
    df_IPO ['Mkt Cap (Jul 8)'] = df_IPO ['Mkt Cap (Jul 8)']*1000000000
    
    stock_code = df_IPO ['Yf Ticker']
    stock_code = stock_code.str.replace('.HK','', regex = True)
    stock_code = stock_code.astype(int)
    df_IPO ['Stock Code'] = stock_code
    
    ### determine if a stock is 18A listed based on its last 2 characters being -B. 
    biotech = df_IPO ['Stock Name']
    biotech = biotech.str [-2:]
    # red hot encoding
    biotech = biotech.str.replace('-B','1', regex = True) 
    biotech.loc[biotech != '1'] = '0'
    biotech = biotech.astype(int)
    df_IPO ['18A Listed'] = biotech    
    
    ### add main board data from HKEX 
    df = pd.read_excel(r'https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx', header = 2)
    df_hkex = df[df['Stock Code'].isin(df_IPO['Stock Code'])]
    df_hkex = df_hkex [['Stock Code', 'Sub-Category']]
    df_hkex = df_hkex.rename(columns = {'Sub-Category':'Main Board'})
    
    main_board = df_hkex ['Main Board']
    # red hot encoding
    main_board = main_board.str.replace('Equity Securities (Main Board)','1', regex = False) 
    main_board = main_board.str.replace('Equity Securities (GEM)','0', regex = False)
    main_board = main_board.astype(int)
    df_hkex ['Main Board'] = main_board
    
    df_IPO = df_IPO.merge(df_hkex, on = ['Stock Code'], how = 'left') ### merge hkex data and df_IPO based on Stock Code (int)
    df_main = pd.concat ([df_main, df_IPO], axis=0) ### add df_IPO data to df_main

df_main.to_excel('Volume.xlsx', index = False)
