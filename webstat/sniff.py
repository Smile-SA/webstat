import subprocess
import re
from prometheus_client import Counter

def sniff_packets(interface=None):
    file_path = 'sniffed.txt'
    file = open(file_path, 'w')

    # Build the tcpdump command with optional interface argument
    tcpdump_command = ['sudo', 'tcpdump']
    if interface:
        tcpdump_command.extend(['-i', interface])

    # Run TCPdump and capture the output
    p = subprocess.Popen(tcpdump_command, stdout=subprocess.PIPE, universal_newlines=True)

    # Regular expression pattern for URL matching
    url_pattern = r'(?:Type65|AAAA)\?\s*([^\(\)\s]+)\s*\('

    # Initialize a Counter metric for URL occurrences
    url_counter = Counter('url_access_count', 'Number of times a URL is accessed', ['url'])

    # Loop through each line of output from TCPdump
    for line in iter(p.stdout.readline, ''):
        # Find URLs matching the pattern in the line
        matches = re.search(url_pattern, line)
        if matches:
            # Write each URL to a file
            file.write(matches.group(1) + '\n')
            file.flush()

            # Increment the URL Counter metric
            url_counter.labels(matches.group(1)).inc()

    # Terminate the TCPdump process
    p.terminate()
    file.close()

def sniff_mode(interface=None):
    print("Sniff mode is active and collecting HTTP information, it is a better idea to run this in the background")
    sniff_packets(interface)
