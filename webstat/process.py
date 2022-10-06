from curses import raw
import os
import time
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
from webstat.analyze import summary_anaylyze
import pandas as pd


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
    #if args.pcap != None:
    #    df = process_pcap(file_name)
    while True:
        summary_anaylyze()
        time.sleep(2)
        os.system('clear')

