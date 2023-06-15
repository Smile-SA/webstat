from sniff import sniff_mode
from analyze import analyze_mode, sniff_analyz_mode
from prometheus_client import start_http_server
import argparse, os, threading, time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", help="Select Mode", required=True)
    parser.add_argument("-i", "--iface", help="Interface to use, default is scapy's default interface")
    parser.add_argument("-r", "--show_raw", dest="show_raw", action="store_true", help="Whether to print POST raw data, such as passwords, search queries, etc.")
    args = parser.parse_args()

    if args.mode == 'analyze':
        try:
            start_http_server(8001)
            sniff_thread = threading.Thread(target=sniff_analyz_mode, args=(args,))
            sniff_thread.daemon = True  # Set the thread as a daemon so it terminates when the main thread exits
            sniff_thread.start()
            time.sleep(3)
            while True:
                analyze_mode()
        except KeyboardInterrupt:
            print("\n\nExiting Analyze Mode..\n\n")
            os._exit(130)
    else:
        try:  
            start_http_server(8000)   
            sniff_mode(args)
        except KeyboardInterrupt:
            print("\n\nExiting Sniff Mode..\n\n")
            os._exit(130)

if __name__ == '__main__':
    main()
