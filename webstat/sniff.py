import subprocess
import re
from prometheus_client import Counter
from utils import get_ip_location

def sniff_packets(args=None):

    if args and args.interface:
        try:
            # Check if the specified network interface exists
            subprocess.check_output(['ifconfig', args.interface])
        except subprocess.CalledProcessError:
            return

    file_path = 'sniffed.txt'
    file = open(file_path, 'w')
    ip_info = get_ip_location(args=args)

    # Build the tcpdump command with optional interface argument
    tcpdump_command = ['sudo', 'tcpdump']

    if args.interface:
        tcpdump_command.extend(['-i', args.interface])

    # Run TCPdump and capture the output
    p = subprocess.Popen(tcpdump_command, stdout=subprocess.PIPE, universal_newlines=True)

    # Regular expression pattern for URL matching
    url_pattern = r'(?:Type65|AAAA)\?\s*([^\(\)\s]+)\s*\('

    # Initialize a Counter metric for URL occurrences
    url_counter = Counter('url_access_count', 'Number of times a URL is accessed', ['url', 'city'])  # Added 'city' label
        
    # Loop through each line of output from TCPdump
    for line in iter(p.stdout.readline, ''):
        # Find URLs matching the pattern in the line
        matches = re.search(url_pattern, line)
        if matches:
            # Get city information from get_ip_location with the provided args
            city = ip_info.get('city')

            # Write each URL to a file
            file.write(f"{matches.group(1)} - {city}\n")
            file.flush()

            # Increment the URL Counter metric
            url_counter.labels(matches.group(1), city).inc()

    # Terminate the TCPdump process
    p.terminate()
    file.close()