import json, time, os
from scapy.sendrecv import sniff
from scapy.sessions import TCPSession
from scapy.layers.http import * # import HTTP packet
from scapy.layers.inet import IP, TCP
import pandas as pd
from collections import Counter as cCount
from prometheus_client import Counter, Gauge
import psutil
from cryptography.fernet import Fernet

#Importing key
try:
    fernet = Fernet(os.environ['WEBKEY'])
except Exception as error:
    print("Please export the provided key to env")
    exit()
    
#Importing ethernet ports
addrs = psutil.net_if_addrs()

## Create a Packet Counter
packet_source_counts = cCount()
packet_destination_counts = cCount()
packet_response_counts = cCount()
http_request_proto_source_gauge = Gauge("http_request_proto_source", "Count HTTP request from source", ["method", "host"])
http_request_proto_destination_gauge = Gauge("http_request_proto_destination", "Count HTTP request to a destination", ["method", "host", "path"])
http_response_proto_gauge = Gauge("http_response_proto_destination", "Count HTTP  Response", ["status"])
sniff_dt = {'ip_source': [], 'ip_destination':[], 'host': []} #}, 'access_time': []} 

def sniff_packets(iface=None):
    """
    Sniff 80 port packets with `iface`, if None (default), then the
    Scapy's default interface is used
    """
    if iface == None:
        iface = [*addrs.keys()][1]
    if iface:
        # port 80 for http (generally)
        # `process_packet` is the callback
        
        while True:
            sniff(filter="port 80", prn=process_packet, iface=iface, session=TCPSession, store=False, timeout=10)
            # print("Reset cycle")
            for k, v in packet_source_counts.items():
                http_request_proto_source_gauge.labels(method=k[0], host=k[1]).set(v)

            for k, v in packet_destination_counts.items():
                http_request_proto_destination_gauge.labels(method=k[0], host=k[1], path=k[2]).set(v)

            for k, b in packet_response_counts.items():
                http_response_proto_gauge.labels(status=k[0])
    else:
        # sniff with default interface
        sniff(filter="port 80", prn=process_packet, session=TCPSession, store=False)

def process_packet(packet):
    """
    This function is executed whenever a packet is sniffed
    """
    if HTTP in packet:
        if HTTPRequest in packet:
            host = ""
            path = ""

            show_raw = True
            if packet[HTTPRequest].Host and packet[HTTPRequest].Path:
                host = packet[HTTPRequest].Host.decode()
                path = packet[HTTPRequest].Path.decode()
                sniff_dt['host'].append(host)
            else:
                print(f'Host: {packet[HTTPRequest].Host}, path: {packet[HTTPRequest].Path}')
            
            # get the requester's IP Address
            ip_source = packet[IP].src
            sniff_dt['ip_source'].append(ip_source)

            ip_destination = packet[IP].dst
            sniff_dt['ip_destination'].append(ip_destination)
            #sniff_dt["access_time"].append(printable_timestamp())
            
            # get the request method
            method = packet[HTTPRequest].Method.decode()

            key_source = tuple([method, ip_source])
            packet_source_counts.update([key_source])

            destination_source = tuple([method, host, path])
            packet_destination_counts.update([destination_source])
            #print(f"\n\{ip_source} Requested {host+path} with {method}")

            with open('.data.json', 'w') as fp:
                json.dump(sniff_dt, fp)
            
            # encrypting data
            encrypt('.data.json')

            if show_raw and packet.haslayer(Raw) and method == "POST":
                # if show_raw flag is enabled, has raw data, and the requested method is "POST"
                # then show raw
                print(f"\nSome useful Raw data: {packet[Raw].load}")

        if HTTPResponse in packet:
            status = packet[HTTPResponse].Status_Code.decode()
            response_content = tuple([status])
            #print(f"\n{GREEN}[-] \ Status code {status}{RESET}")
            packet_response_counts.update([response_content])

def printable_timestamp(ts, resol):
    ts_sec = ts // resol
    ts_subsec = ts % resol
    ts_sec_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_sec))
    return '{}.{}'.format(ts_sec_str, ts_subsec)

def encrypt(data):
    if os.path.exists(".data.json"):
        with open(data, 'rb') as file:
        	original = file.read()
        encrypted = fernet.encrypt(original)
        with open(data, 'wb') as encrypted_file:
	        encrypted_file.write(encrypted)

def decrypt(data):
    with open(data, 'rb') as enc_file:
    	encrypted = enc_file.read()
    decrypted = fernet.decrypt(encrypted)
    with open(data, 'wb') as dec_file:
        dec_file.write(decrypted)

def sniff_mode(arg):
    print('sniff mode is active and collecting domain information, it is better idea to run this in background')
    print('Please proceed to analyze mode to see more information')
    sniff_packets(arg.iface)
    os.remove(".data.json")