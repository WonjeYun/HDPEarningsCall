# Run this script on WRDS cloud to download data from WRDS
import wrds
import pandas as pd

def delete_duplicates(df):
    '''
    Delete duplicates in the dataframe
    Input:  df: pandas dataframe
    Output: df: pandas dataframe
    '''
    df = df.drop_duplicates(subset=['gvkey', 'mostimportantdateutc', 'componenttext'])
    return df


if __name__ == "__main__":
    # Assuming that you have a WRDS account and generated a pgpass on WRDS cloud
    db = wrds.Connection()

    years = range(2014, 2024)
    for year in years:
        snp500_query = f'''SELECT b.gvkey \
                            FROM (SELECT * FROM crsp.dsp500list \
                                        WHERE start<=make_date({year}, 1, 1) \
                                            and ending>=make_date({year},12,31)
                                ) as a \
                            LEFT JOIN (SELECT * FROM crsp.ccmxpf_lnkhist \
                                        WHERE linkdt<=make_date({year}, 1, 1) \
                                            and (linkenddt>=make_date({year},12,31)) or linkenddt is NULL
                                        ) as b \
                            ON a.permno=b.lpermno and b.linktype in ('LU','LC') and b.linkprim in ('P','C')'''


        query_select = '''SELECT j.gvkey, a.mostimportantdateutc, a.headline, b.transcriptcomponenttypeid, b.transcriptcomponenttypename, c.componenttext'''
        query_from1 = f'''FROM (SELECT * FROM ciq.wrds_transcript_detail \
                                        WHERE keydeveventtypeid = 48 \
                                            and transcriptpresentationtypeid=5 \
                                            and date_part('year', mostimportantdateutc) = {year} \
                                ) as a, \
                            (SELECT * FROM ciq.wrds_transcript_person \
                                WHERE transcriptcomponenttypeid=3 \
                                        or transcriptcomponenttypeid=4 \
                            ) as b, \
                            ciq.ciqtranscriptcomponent as c,'''
        query_from2 =   '(' + snp500_query + ')' + 'as j, ciq_common.wrds_gvkey as k'
        query_where = '''WHERE a.companyid=k.companyid \
                                and k.gvkey=j.gvkey \
                                and a.transcriptid = b.transcriptid \
                                and b.transcriptid = c.transcriptid \
                                and b.transcriptcomponenttypeid = c.transcriptcomponenttypeid'''
        query_orderby = '''ORDER BY a.transcriptid, b.transcriptcomponentid, a.companyid'''

        sql_query = ' '.join([query_select, query_from1, query_from2, query_where, query_orderby])

        print(f'querying {year}...')
        snp500_transcripts = db.raw_sql(sql_query)
        snp500_transcripts = delete_duplicates(snp500_transcripts)
        snp500_transcripts.to_csv(f'/home/[groupname]/[username]/data/sp500_cc_transcripts_{year}.csv', index=False)
        print(f'{year} saved!')

    db.close()

    print('Concatenating all data...')
    base_year = pd.read_csv('/home/[groupname]/[username]/data/sp500_cc_transcripts_2014.csv')
    for year in years[1:]:
        yearly_data = pd.read_csv(f'/home/[groupname]/[username]/data/sp500_cc_transcripts_{year}.csv')
        base_year = pd.concat([base_year, yearly_data], axis=0)
        print(f'{year} concatenated!')

    print('Grouping by gvkey and mostimportantdateutc to merge the componenttext...')
    base_year = base_year.groupby(['gvkey', 'mostimportantdateutc'])['componenttext'].apply(lambda x: ' '.join(x)).reset_index()
    base_year.to_csv('/home/[groupname]/[username]/data/sp500_cc_transcripts_2014_2023.csv', index=False)
    print('All data saved!')