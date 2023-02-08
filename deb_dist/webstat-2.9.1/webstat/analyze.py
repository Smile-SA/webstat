from webstat.sniff import encrypt, decrypt
import json
import pandas as pd

def http_analyze(df):
    print('***************************')
    print('*      HTTP Analysis      *')
    print('***************************')
    print('Host Ranking')
    n_by_host = df.groupby("host").size()
    print(n_by_host.to_string())

    print('\n***************************\n')

    n_by_method = df.groupby("method").size()
    print(n_by_method.to_string())

    print('\n***************************\n')

    n_by_path = df.groupby("path").size()
    print(n_by_path.to_string())

def summary_anaylyze():
    try:
        decrypt('.data.json')
        #TODO: Memory optimisation
        with open(".data.json", "r") as json_file:
            my_dict = json.load(json_file)     
            sniff_df = pd.DataFrame.from_dict(my_dict).rename(columns = {'ip_source':'IP_SOURCE','host':'DOMAIN', 'path':'PATH'})
            sniff_df_sorted = sniff_df.groupby(['IP_SOURCE','DOMAIN','PATH'])['DOMAIN'].count().reset_index(name='HITS').sort_values(['HITS'], ascending=False)
            return sniff_df_sorted
    except Exception as e:
        print('No requests so far, please try again later')