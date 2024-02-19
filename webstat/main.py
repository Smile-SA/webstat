import argparse
import os
import threading
import time
from sniff import sniff_packets
from analyze import analyze_mode, sniff_analyz_mode
from prometheus_client import start_http_server

def main():
    """
    Main function to handle command-line arguments and start the appropriate mode.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", help="Select Mode, either Sniff or Analyze")
    parser.add_argument("--ip", action='store_true', help="Get IP address")
    parser.add_argument("-i", "--interface", help="Specify network interface for webstat")
    parser.add_argument("--location", action='store_true', help="Get Location based information")

    args = parser.parse_args()

    # Check both --ip and --location flags
    if args.ip:
        print("IP address is extracted")

    if args.location:
        print('Location Information is extracted')

    if args.mode == 'analyze':
        try:
            # Start Prometheus HTTP server
            start_http_server(8001)

            # Start Analyze Mode in a separate thread
            sniff_thread = threading.Thread(target=sniff_analyz_mode, args=(args,))
            sniff_thread.daemon = True  # Set the thread as a daemon to terminate when the main thread exits
            sniff_thread.start()
            time.sleep(3)

            # Continuously run Analyze Mode until interrupted
            while True:
                analyze_mode(args=args)

        except KeyboardInterrupt:
            print("\n\nExiting Analyze Mode..\n")
            print("\nDomain information extracted to extract.txt\n")
            os._exit(130)
    else:
        try:
            # Start Prometheus HTTP server
            start_http_server(8000)

            # Start Sniff Mode
            print("Sniff mode is active and collecting HTTP information; it is a better idea to run this in the background.")
            sniff_packets(args=args)

        except KeyboardInterrupt:
            print("\n\nExiting Sniff Mode..\n\n")
            os._exit(130)

if __name__ == '__main__':
    main()
