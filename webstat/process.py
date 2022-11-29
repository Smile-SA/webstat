from webstat.analyze import summary_anaylyze, encrypt
import os, sys, select, time
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
import pandas as pd

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
        df = summary_anaylyze()

        # encrypting data
        encrypt('.data.json')
        
        if df is not None:
            df.reset_index(drop=True, inplace=True)
            print(df)
        print('')        
        
        extract_pre = pd.read_csv('export.txt', delimiter = "\t")
        if extract_pre.shape[0] < 1:
            print("No domains have been shared so far")            
        else:
            print('* Following domain information has been shared *')
            for x in extract_pre.DOMAIN.values: domains.add(x)
            print(domains)
        print('')        

        if os.path.exists(".data.json"):
            print("Enter Index To Share Domain:")
            i, o, e = select.select( [sys.stdin], [], [], 1 )
            if (i):
                userText = sys.stdin.readline().strip()
                if userText:
                    if len(userText) > 1 or int(userText) >= len(df):
                        print("Enter a valid index")
                        time.sleep(2)
                    elif df.iloc[int(userText)].DOMAIN in domains:
                        print("Domain already shared, ignoring input")
                        time.sleep(2)
                    else:
                        domains.add(df.iloc[int(userText)].DOMAIN)
        else:
            time.sleep(3)
            continue

        extract = df[df['DOMAIN'].isin(domains)]
        #This merge should be performed in this particular order - to avoid mismatch with current df and past df
        exported = extract_pre.merge(extract, on = ['IP_SOURCE', 'DOMAIN', 'HITS'], how='outer').drop('Unnamed: 0', axis=1).sort_values('HITS', ascending=False).drop_duplicates(['DOMAIN', 'IP_SOURCE']).sort_index()
        exported.to_csv(r'export.txt', sep='\t', mode='w' , header=True)
        
        os.system('clear')