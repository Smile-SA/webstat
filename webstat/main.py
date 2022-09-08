from webstat.process import analyze_mode
from webstat.sniff import sniff_mode
from prometheus_client import start_http_server
import argparse

def main():
    parser = argparse.ArgumentParser(description="Mode selection")
    parser.add_argument("-m", "--mode", help="Select Mode")
    parser.add_argument("-i", "--iface", help="Interface to use, default is scapy's default interface")
    parser.add_argument("--show-raw", dest="show_raw", action="store_true", help="Whether to print POST raw data, such as passwords, search queries, etc.")
    parser.add_argument("-o", "--output", help="Whether to dump http requests")
    

    args = parser.parse_args()

    if args.mode != 'sniff':
        analyze_mode()
    else:
        start_http_server(8000)   
        sniff_mode(args)

if __name__ == '__main__':
    main()
