import numpy as np
import pandas as pd
from pandas.errors import SettingWithCopyWarning
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from tqdm import tqdm
import datetime

import warnings
warnings.simplefilter(action="ignore", category=[SettingWithCopyWarning, DeprecationWarning])

import pyLDAvis.gensim_models
pyLDAvis.enable_notebook()

import tomotopy as tp

from hdp_training import get_hdp_topics


def get_top_n_topic_wrds(hdp_model_lst, n):
    # for each hdp models, get the top 10 words for each topic
    top_words = []
    for _, hdp in enumerate(hdp_model_lst):
        top_words.append(get_hdp_topics(hdp, top_n=n))
    return top_words

def merge_top_wrds_by_qtr(top_words):
    total_top_wrds_by_qt = []
    for i in range(len(top_words)):
        qt_top_wrds = []
        for word_scr_lst in top_words[i].values():
            for wrd, _ in word_scr_lst:
                qt_top_wrds.append(wrd)
        total_top_wrds_by_qt.append(qt_top_wrds)
    return total_top_wrds_by_qt

def dfdfd(top_words):
    total_top_words = []
    for num_periods in range(len(top_words)):
        for _, value in top_words[num_periods].items():
            for words in value:
                total_top_words.append(words[0])

    total_top_words = set(total_top_words)
    total_top_words = list(total_top_words)
    return total_top_words

def dfsdafsd(total_top_wrds_by_qt, total_top_words, quarter_lst):
    # for each list in total_top_wrds_by_qt, get the count of the words in the list that appears in total_top_words
    # and add as a column to a new dataframe
    word_count_df = pd.DataFrame()
    for i in range(len(total_top_wrds_by_qt)):
        word_count = []
        for word in total_top_words:
            word_count.append(total_top_wrds_by_qt[i].count(word))
        word_count_df[quarter_lst[i]] = word_count
    word_count_df.index = total_top_words
    return word_count_df

# for each row in word_count_df, remove the rows with more than half of the values as 0
trimmed_word_count_df = word_count_df.loc[(word_count_df!=0).sum(axis=1) > 10]
trimmed_word_count_df.to_csv('data/quarterly_trimmed_word_count.csv')

# sum the columns of word_count_df based on the year of the column
yrly_word_count_df = word_count_df.copy()
yrly_word_count_df.columns = word_count_df.columns.to_timestamp().to_period('Y')
# groupby columns and sum
yrly_word_count_df = yrly_word_count_df.transpose().groupby(level=0).sum().transpose()

trim_yrly_word_count_df = yrly_word_count_df.loc[(yrly_word_count_df!=0).sum(axis=1) > 3]
trim_yrly_word_count_df.to_csv('data/yearly_trimmed_word_count.csv')
