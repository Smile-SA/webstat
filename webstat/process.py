from webstat.analyze import summary_anaylyze
import os
import time
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
import pandas as pd
from pytimedinput import timedInput

def printable_timestamp(ts, resol):
    ts_sec = ts // resol
    ts_subsec = ts % resol
    ts_sec_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_sec))
    return '{}.{}'.format(ts_sec_str, ts_subsec)

def process_pcap(file_name):
    print('Opening {}...'.format(file_name))

    count = 0
    interesting_packet_count = 0

    data = []

    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):

        count += 1

        ether_pkt = Ether(pkt_data)
        if not ether_pkt.haslayer('HTTPRequest'):
            continue

        if 'type' not in ether_pkt.fields:
            # LLC frames will have 'len' instead of 'type'.
            # We disregard those
            continue

        if ether_pkt.type != 0x0800:
            # disregard non-IPv4 packets
            continue

        ip_pkt = ether_pkt[IP]
        http_req_pkt = ether_pkt.getlayer('HTTPRequest')

        if ip_pkt.proto != 6:
            # Ignore non-TCP packet
            continue

        records = [ip_pkt.src, ip_pkt.dst, http_req_pkt.Host.decode(), http_req_pkt.Method.decode(), http_req_pkt.Path.decode()]
        data.append(records)
        df = pd.DataFrame(data, columns=['ip_source', 'ip_destination', 'host', 'method', 'path'])

        interesting_packet_count += 1


    print('{} contains {} packets ({} interesting)'.
        format(file_name, count, interesting_packet_count))

    return df

def analyze_mode(args):
    #TODO: Don't drop index!
    domains = set()
    if not os.path.exists('export.txt'):
        pd.DataFrame(columns=['IP_SOURCE', 'DOMAIN', 'HITS']).to_csv(r'export.txt', sep='\t', mode='w' , header=True)

    while True:
        #DONE: Dropped index
        df = summary_anaylyze()
        if df is not None:
            df.reset_index(drop=True, inplace=True)
        print(df)
        print('')        

        if not os.path.exists("export.txt"):
            print("No domains have been shared so far")            
        else:
            extract_pre = pd.read_csv('export.txt', delimiter = "\t")
            if extract_pre.shape[0] < 1:
                print("No domains have been shared so far")            
            else:
                print('* Following domain information has been shared *')
                for x in extract_pre.DOMAIN.values: domains.add(x)
                print(domains)
        print('')        

        if os.path.exists("data.json"):
            userText, timedOut = timedInput("Enter Index To Share Domain:")
            if len(userText) != 0:
                if df.iloc[int(userText)].DOMAIN in domains:
                    print("Domain already shared, ignoring input")
                else:
                    domains.add(df.iloc[int(userText)].DOMAIN)
                #TODO: check HERE IF STUCK
        else:
            time.sleep(3)
            continue
        
        extract = df[df['DOMAIN'].isin(domains)]
        #DONE: currently, items = index numbers, replace with actual domain NAMES
        #DONE: Find a way to read old export data
        #DONE: Merge extract_pre with extract
        #This merge should be performed in this particular order - to avoid mismatch with current df and past df
        exported = extract_pre.merge(extract, on = ['IP_SOURCE', 'DOMAIN', 'HITS'], how='outer').drop('Unnamed: 0', axis=1).sort_values('HITS', ascending=False).drop_duplicates(['DOMAIN', 'IP_SOURCE']).sort_index()
        exported.to_csv(r'export.txt', sep='\t', mode='w' , header=True)
        
        os.system('clear')
        #TODO:EXPORT AS JSON .TXT IS SHIT