import numpy as np
import pandas as pd
from pandas.errors import SettingWithCopyWarning
import pickle
from tqdm import tqdm

import warnings
warnings.simplefilter(action="ignore", category=[SettingWithCopyWarning, DeprecationWarning])

import tomotopy as tp


def train_hdp_model(quarter_lst, df):
    """
    Train Hierarchical Dirichlet Process (HDP) model
    Args:
        quarter_lst (list): list of quarters
        df (pd.DataFrame): QnA transcript of earnings call
    Returns:
        hdp_model_lst (list): list of trained HDP models (tomotopy.HDPModel)
    """
    hdp_model_lst = []

    for quarter in quarter_lst:
        print(quarter)

        term_weight = tp.TermWeight.PMI
        hdp = tp.HDPModel(tw=term_weight,
                          min_cf=5,
                          rm_top=7,
                          gamma=1,
                          alpha=0.1,
                          initial_k=10,
                          seed=1234)
        word_list_lemmatized = df[df['doc_quarter']==quarter]

        for vec in word_list_lemmatized['qna tokens']:
            hdp.add_doc(vec)
        
        for i in range(0, 1000, 100):
            hdp.train(100, workers=1)
            print(f'Iter: {i}\tLoglikelihood: {hdp.ll_per_word}\tNum. of topics: {hdp.live_k}')
        
        hdp_model_lst.append(hdp)
        print('===========================================================')
    return hdp_model_lst

def get_hdp_topics(hdp, top_n=10):
    '''Wrapper function to extract topics from trained tomotopy HDP model 
    
    ** Inputs **
    hdp:obj -> HDPModel trained model
    top_n: int -> top n words in topic based on frequencies
    
    ** Returns **
    topics: dict -> per topic, an arrays with top words and associated frequencies 
    '''
    
    # Get most important topics by # of times they were assigned (i.e. counts)
    sorted_topics = [k for k, _ in 
                     sorted(enumerate(hdp.get_count_by_topics()),
                            key=lambda x:x[1],
                            reverse=True)
                    ]

    topics=dict()
    
    # For topics found, extract only those that are still assigned
    for k in sorted_topics:
        if not hdp.is_live_topic(k): continue # remove un-assigned topics at the end (i.e. not alive)
        topic_wp =[]
        for word, prob in hdp.get_topic_words(k, top_n=top_n):
            topic_wp.append((word, prob))

        topics[k] = topic_wp # store topic word/frequency array
        
    return topics

def get_inferred_topic(hdp, doc):
    '''Wrapper function to extract inferred topic for a given document
    
    ** Inputs **
    hdp:obj -> HDPModel trained model
    doc: list -> list of words in document
    ** Returns **
    topics: dict -> per topic, an arrays with top words and associated frequencies 
    '''
    # Get most important topics by # of times they were assigned (i.e. counts)
    doc_inst = hdp.make_doc(doc)
    real_vecs = []
    for k, vec_k in enumerate(hdp.infer(doc_inst)[0]):
        if not hdp.is_live_topic(k): continue
        real_vecs.append(vec_k)

    inferred_topics = (np.array(real_vecs), hdp.infer(doc_inst)[1])
    return inferred_topics

def get_earnings_call_w_topics(hdp_model_lst, df):
    '''Wrapper function to extract inferred topic for a given document

    Args:
        hdp_model_lst (list): list of trained HDP models (tomotopy.HDPModel)
        df (pd.DataFrame): QnA transcript of earnings call
    Returns:
        earnings_call_qt_list (list): list of QnA transcript with inferred topics
    '''
    earnings_call_qt_list = []

    for i, hdp in tqdm(enumerate(hdp_model_lst), total=len(hdp_model_lst)):
        topics = get_hdp_topics(hdp, top_n=30)
        # get the word list lemmatized for the quarter, or split the entire dataframe by quarters
        word_list_lemmatized = df[df['doc_quarter']==df[i]].reset_index(drop=True)

        # get the inferred topics for each documents
        topic_allocation = []
        for wd_lst in range(len(word_list_lemmatized)):
            doc = word_list_lemmatized['qna tokens'].iloc[wd_lst]
            inferred_topics = get_inferred_topic(hdp, doc)
            # add the index of largest index of inferred_topics[0] to topic_allocation
            topic_allocation.append(np.argmax(inferred_topics[0]))
        
        word_list_lemmatized.loc[:, 'topic_allocation'] = topic_allocation
        word_list_lemmatized = word_list_lemmatized.dropna(subset = ['tic'])
        earnings_call_qt_list.append(word_list_lemmatized)

    return earnings_call_qt_list

