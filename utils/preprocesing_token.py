import pandas as pd
from pandas.errors import SettingWithCopyWarning
import pickle
from tqdm import tqdm

import warnings
warnings.simplefilter(action="ignore", category=[SettingWithCopyWarning, DeprecationWarning])

import gensim


def tokenize_text(df, nlp, noun=True):
    """
    Tokenize text using spacy and gensim
    Args:
        df (pd.DataFrame): QnA transcript of earnings call
        nlp (spacy.lang.en.English): spacy nlp object
        noun (bool): if True, consider only noun, else consider non-removal pos
    Returns:
        tokens (list): list of tokens
    """
    removal= ['ADV','PRON','CCONJ','PUNCT','PART','DET','ADP','SPACE', 'NUM', 'SYM']
    consider_only = ['NOUN']
    text_data = df['componentText']
    tqdm_len = len(text_data)
    tokens = []

    for qna in tqdm(nlp.pipe(text_data), total=tqdm_len):
        if noun:
            proj_tok = [token.lemma_.lower()
                        for token in qna
                        if token.pos_ in consider_only 
                        and not token.is_stop and token.is_alpha]
        else:
            proj_tok = [token.lemma_.lower()
                        for token in qna
                        if token.pos_ not in removal
                        and not token.is_stop and token.is_alpha]
        tokens.append(proj_tok)

    # make a bigram for better analysis
    bigram = gensim.models.phrases.Phrases(tokens)
    tokens = [bigram[line] for line in tokens]
    tokens = [bigram[line] for line in tokens]
    return tokens

def add_tokenized_text(df, tokens):
    """
    Add tokenized text to the dataframe
    Args:
        df (pd.DataFrame): QnA transcript of earnings call
        tokens (list): list of tokens
    Returns:
        df (pd.DataFrame): QnA transcript of earnings call with tokenized text
    """
    df['qna tokens'] = tokens

    # get the quarter of the transcript
    df['doc_date'] = pd.to_datetime(df['doc_date'])
    df['doc_quarter'] = df['doc_date'].dt.to_period('Q')
    return df