def ip_analyze(df):
    print('***************************')
    print('*      IP Analysis        *')
    print('***************************')
    n_by_src = df.groupby("ip_source").size()
    print('IP Source Ranking')
    print(n_by_src.to_string())

    print('\n***************************\n')

    print('IP Destination Ranking')
    n_by_dst = df.groupby("ip_destination").size()
    print(n_by_dst.to_string())


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


def summary_anaylyze(df):
    ip_analyze(df)
    print('\n\n')
    http_analyze(df)