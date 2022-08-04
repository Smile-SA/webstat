from xml import dom
from scapy.sendrecv import sniff
from scapy.sessions import TCPSession
from scapy.layers.http import * # import HTTP packet
from scapy.layers.inet import IP, TCP

from colorama import init, Fore
from collections import Counter as cCount
from prometheus_client import Counter, Gauge

# initialize colorama
init()
# define colors
GREEN = Fore.GREEN
RED   = Fore.RED
RESET = Fore.RESET

## Create a Packet Counter
packet_source_counts = cCount()
packet_destination_counts = cCount()
packet_response_counts = cCount()
http_request_proto_source_gauge = Gauge("http_request_proto_source", "Count HTTP request from source", ["method", "host"])
http_request_proto_destination_gauge = Gauge("http_request_proto_destination", "Count HTTP request to a destination", ["method", "host", "path"])
http_response_proto_gauge = Gauge("http_response_proto_destination", "Count HTTP  Response", ["status"])

def sniff_packets(iface=None):
    """
    Sniff 80 port packets with `iface`, if None (default), then the
    Scapy's default interface is used
    """
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
            else:
                print(f"Host: {packet[HTTPRequest].Host}, path: {packet[HTTPRequest].Path}")
            
            # get the requester's IP Address
            ip_source = packet[IP].src
            ip_destination = packet[IP].dst
            # get the request method
            method = packet[HTTPRequest].Method.decode()

            key_source = tuple([method, ip_source])
            packet_source_counts.update([key_source])

            destination_source = tuple([method, host, path])
            packet_destination_counts.update([destination_source])

            print(f"\n{GREEN}[+] \{ip_source} Requested {host+path} with {method}{RESET}")

            if show_raw and packet.haslayer(Raw) and method == "POST":
                # if show_raw flag is enabled, has raw data, and the requested method is "POST"
                # then show raw
                print(f"\n{RED}[*] Some useful Raw data: {packet[Raw].load}{RESET}")

        if HTTPResponse in packet:
            status = packet[HTTPResponse].Status_Code.decode()
            response_content = tuple([status])
            print(f"\n{GREEN}[-] \ Status code {status}{RESET}")
            packet_response_counts.update([response_content])


def sniff_mode():
    import argparse
    parser = argparse.ArgumentParser(description="HTTP Packet Sniffer, this is useful when you're a man in the middle." \
                                                 + "It is suggested that you run arp spoof before you use this script, otherwise it'll sniff your personal packets")
    parser.add_argument("-i", "--iface", help="Interface to use, default is scapy's default interface")
    parser.add_argument("--show-raw", dest="show_raw", action="store_true", help="Whether to print POST raw data, such as passwords, search queries, etc.")

    # parse arguments
    args = parser.parse_args()
    iface = args.iface
    # show_raw = args.show_raw

    sniff_packets(iface)