import argparse
import os
import threading
import time
import requests
from sniff import sniff_mode
from analyze import analyze_mode, sniff_analyz_mode
from prometheus_client import start_http_server

def get_ip_location():
    """
    Get IP-based location information using ipinfo.io.
    """
    response = requests.get('https://ipinfo.io/json')
    if response.status_code == 200:
        ip_info = response.json()
        for key, value in ip_info.items():
            print(f"{key}: {value}")
    else:
        print(f"Failed to retrieve IP information. Status code: {response.status_code}")

def main():
    """
    Main function to handle command-line arguments and start the appropriate mode.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", help="Select Mode, either Sniff or Analyze")
    parser.add_argument("--ipinfo", action='store_true', help="Get IP-based location information")
    parser.add_argument("-i", "--interface", help="Specify network interface for webstat")

    args = parser.parse_args()

    if args.ipinfo:
        get_ip_location()
        os._exit(0)

    if args.mode == 'analyze':
        try:
            start_http_server(8001)
            sniff_thread = threading.Thread(target=sniff_analyz_mode, args=(args,))
            sniff_thread.daemon = True  # Set the thread as a daemon so it terminates when the main thread exits
            sniff_thread.start()
            time.sleep(3)
            while True:
                analyze_mode(args.interface)
        except KeyboardInterrupt:
            print("\n\nExiting Analyze Mode..\n")
            print("\nDomain information extracted to extract.txt\n")
            os._exit(130)
    else:
        try:
            start_http_server(8000)
            sniff_mode(args.interface)
        except KeyboardInterrupt:
            print("\n\nExiting Sniff Mode..\n\n")
            os._exit(130)

if __name__ == '__main__':
    main()
