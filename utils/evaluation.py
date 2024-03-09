import numpy as np
import pandas as pd
from pandas.errors import SettingWithCopyWarning
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from tqdm import tqdm
import datetime

import logging
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

import warnings
warnings.simplefilter(action="ignore", category=[SettingWithCopyWarning, DeprecationWarning])

import yfinance as yf


def get_topic_all_tic_list(df):
    '''Wrapper function to get the list of 'tic' with the same topic allocation
    Input:
    df: dataframe -> dataframe with 'tic' and 'topic_allocation' columns
    ** Returns **
    same_topic_tic_lst: list -> list of 'tic' with the same topic allocation
    '''
    same_topic_tic_lst = []
    for i in df['topic_allocation'].unique():
        same_topic_tic = df[df['topic_allocation'] == i]['tic'].unique().tolist()
        same_topic_tic_lst.append(same_topic_tic)
    return same_topic_tic_lst

# get the stock price for the given 'doc_quarter' for the given 'tic's
def get_stock_price(tic_lst, start, end):
    '''Function to get the stock price for the given 'doc_quarter' for the given 'tic's
    
    ** Inputs **
    tic_lst: list -> list of 'tic's
    quarter: str -> quarter in 'YYYY-Qn' format
    
    ** Returns **
    stock_price: DataFrame -> dataframe with stock price for the given 'tic's
    '''
    stock_price = pd.DataFrame()
    for tic in tic_lst:
        try:
            stock = yf.download(tic, start=start, end=end, progress=False)['Close']
            stock = stock.rename(tic)
            stock_price = pd.concat([stock_price, stock], axis=1)
        except:
            continue
    return stock_price

## need to use 'stock_price_2014_2023.csv' instead of downloading from yahoo finance
def get_stock_price_from_csv(tic_lst, start, end):
    '''Function to get the stock price for the given 'doc_quarter' for the given 'tic's
    
    ** Inputs **
    tic_lst: list -> list of 'tic's
    start: datetime -> start date
    end: datetime -> end date
    
    ** Returns **
    stock_price: DataFrame -> dataframe with stock price for the given 'tic's
    '''
    stock_price = pd.read_csv('data/stock_price_2014_2023.csv', index_col=0).reset_index()
    # set 'Dly Cal Dt' as index and 'Ticker' as columns
    stock_price = stock_price.pivot_table(index='DlyCalDt', columns='Ticker', values='DlyClose', aggfunc='first')
    # set index to datetime
    stock_price.index = pd.to_datetime(stock_price.index)
    # ignore tic in tic_list that is not in stock_price
    tic_lst = [tic for tic in tic_lst if tic in stock_price.columns]
    stock_price = stock_price[tic_lst].loc[start:end]
    return stock_price

def get_start_end_date(df):
    '''Function to get the start and end date of the next quarter for the given 'doc_quarter'
    
    ** Inputs **
    df: DataFrame -> dataframe with 'doc_quarter' column
    
    ** Returns **
    start_date: datetime -> start date
    end_date: datetime -> end date
    '''
    end_date = datetime.datetime.strptime(df['doc_quarter'][0].strftime('%Y-%m-%d'), '%Y-%m-%d')
    end_date = end_date + pd.DateOffset(months=3)
    start_date = end_date - pd.DateOffset(months=2)
    start_date = start_date.replace(day=1)
    return start_date, end_date

# get the stock price for the given 'doc_quarter' for the given 'tic's
def get_ticker_list_stock_price(df):
    # get the stock price for the given 'tic's
    tic_list = df['tic'].unique().tolist()
    start_date, end_date = get_start_end_date(df)
    stock_price = get_stock_price_from_csv(tic_list, start_date, end_date)
    return stock_price

# get the equally weighted sum of stock price within the groups
def get_group_price(same_topic_tic_lst, stock_price):
    '''Function to get the equally weighted sum of stock price within the groups
    
    ** Inputs **
    same_topic_tic_lst: list -> list of 'tic's with the same topic allocation
    stock_price: DataFrame -> dataframe with stock price for the given 'tic's
    
    ** Returns **
    group_price: DataFrame -> dataframe with equally weighted sum of stock price within the groups
    '''
    tic_list = stock_price.columns
    group_price = pd.DataFrame()
    for i, groups in enumerate(same_topic_tic_lst):
        # get equally weighted sum of stock price within the groups
        for tic in groups:
            if tic not in tic_list:
                groups.remove(tic)
        group_mean = stock_price[groups].mean(axis=1).rename(f'group_{i}')
        group_price = pd.concat([group_price, group_mean], axis=1)
    return group_price

# get market return and quarterly risk free rate with yahoo finance
def get_mktrf_rf(start, end):
    '''Function to get the market return and quarterly risk free rate with yahoo finance
    
    ** Inputs **
    start: datetime -> start date
    end: datetime -> end date
    
    ** Returns **
    market_return: DataFrame -> dataframe with market return
    risk_free_rate: float -> quarterly risk free rate
    '''
    market_return = yf.download('^GSPC', start=start, end=end, progress=False)['Close']
    market_return = market_return.pct_change().dropna()
    risk_free_rate = yf.download('^IRX', start=start, end=end, progress=False)['Close']
    risk_free_rate = risk_free_rate.mean() / 100
    return market_return, risk_free_rate

def get_sharpe_ratio(group_price, risk_free_rate):
    '''Function to get the sharpe ratio for the given group price
    
    ** Inputs **
    group_price: DataFrame -> dataframe with equally weighted sum of stock price within the groups
    risk_free_rate: float -> quarterly risk free rate
    
    ** Returns **
    sharpe_ratio_per_group: list -> list of sharpe ratio for the given group price
    '''
    sharpe_ratio_per_group = []
    for group in group_price.columns:
        excess_return = group_price[group].pct_change() - risk_free_rate
        sharpe_ratio = excess_return.mean() / excess_return.std()
        sharpe_ratio_per_group.append(sharpe_ratio)
    return sharpe_ratio_per_group

def get_info_ratio(group_price, market_return):
    '''Function to get the information ratio for the given group price
    
    ** Inputs **
    group_price: DataFrame -> dataframe with equally weighted sum of stock price within the groups
    market_return: DataFrame -> dataframe with market return
    
    ** Returns **
    info_ratio_per_group: list -> list of information ratio for the given group price
    '''
    info_ratio_per_group = []
    for group in group_price.columns:
        active_return = group_price[group].pct_change() - market_return
        info_ratio = active_return.mean() / active_return.std()
        info_ratio_per_group.append(info_ratio)
    return info_ratio_per_group

def add_eval_res_to_list(earnings_call_qt_list):
    '''
    '''
    returns_lst= []
    mkt_returns_lst = []
    sharpe_ratio_lst = []
    info_ratio_lst = []
    market_sharpe_ratio_lst = []
    for earnings_call_df in tqdm(earnings_call_qt_list[:-1]):
        same_topic_tic_lst = get_topic_all_tic_list(earnings_call_df)
        stock_price = get_ticker_list_stock_price(earnings_call_df)
        group_price = get_group_price(same_topic_tic_lst, stock_price)
        group_price = group_price.dropna(axis=1)
        returns_lst.append(group_price.pct_change())
        
        start_date, end_date = get_start_end_date(earnings_call_df)
        market_return, risk_free_rate = get_mktrf_rf(start_date, end_date + pd.DateOffset(days=1))
        mkt_returns_lst.append(market_return)
        sharpe_ratio_per_group = get_sharpe_ratio(group_price, risk_free_rate)
        info_ratio_per_group = get_info_ratio(group_price, market_return)

        market_sharpe_ratio = (market_return.mean() - risk_free_rate) / market_return.std()
        sharpe_ratio_lst.append(sharpe_ratio_per_group)
        info_ratio_lst.append(info_ratio_per_group)
        market_sharpe_ratio_lst.append(market_sharpe_ratio)

    return returns_lst, mkt_returns_lst, sharpe_ratio_lst, info_ratio_lst, market_sharpe_ratio_lst