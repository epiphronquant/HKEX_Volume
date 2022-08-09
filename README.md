# HKEX_Volume
[![HKEX_Volume Updater](https://github.com/epiphronquant/HKEX_Volume/actions/workflows/main.yml/badge.svg)](https://github.com/epiphronquant/HKEX_Volume/actions/workflows/main.yml)

Streamlit App that visualizes volume data for stocks on HKEX

Follow the link to access the app: https://epiphronquant-hkex-volume-volume-data-knj864.streamlitapp.com/

This app visualizes volume data on HKEX stocks. The app utilizes our homemade index methodology for charts 2 and 3 to summarize the data. The method suffers from bias due to the first few days of IPO trading volume being significantly higher than the rest. It utilizes data from HKEX and yfinance.

**Data Sources**
1. HKEX: List of all the stocks, listing on main board or GEM. 
2. yfinance: Sector and Industry for old stocks
3. HKEX-IPO-app: Sector, Industry, Market Cap for updated stocks. Sector, Industry comes from yfinance, Market Cap from AA stocks.
4. Microsoft Excel: Market Cap for stocks (manual update).

**Chart by Chart Explanation**
1. Displays a stock's adjusted close and their 20, 40, 60 average trading day volume. Can be selected based on ticker or English stock name.
2. Displays a industry's homemade index weighted adjusted close and homemade index weighted 20, 40, 60 average trading day volume data. 
3. Displays all the stocks used in chart 2 and includes their market cap and latest 20, 40, 60 average trading day volume. The slider above chart 3 is used to filter out stocks inside chart 3. 
4. Same chart as chart 2 but visualizes data based on filtered stocks in chart 3.

**Homemade Index Methodology**

Weights are applied on the daily percentage change for the creation of the adjusted close index and volume index
Homemade Index calculates weights using Market Cap as follows:
![image](https://user-images.githubusercontent.com/91112822/180348879-d96a6752-4049-40e5-bb3d-55d0c9f5d05b.png)
Excel example for only 3 stocks is here: https://github.com/epiphronquant/HKEX_Volume/blob/main/Homemade%20Index%20Excel%20Example.xlsx?raw=true
