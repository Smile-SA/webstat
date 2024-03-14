import subprocess
import re
from prometheus_client import Counter
from utils import get_ip_location

def sniff_packets(args=None):
    ip = city = 'Unknown'

    if args and args.ip:
        ip_info = get_ip_location(args=args)
        ip = ip_info.get('ip')

    if args and args.location:
        ip_info = get_ip_location(args=args)
        city = ip_info.get('city')

    if args and args.interface:
        try:
            # Check if the specified network interface exists
            subprocess.check_output(['ifconfig', args.interface])
        except subprocess.CalledProcessError:
            return

    file_path = '/tmp/.sniffed.txt'
    file = open(file_path, 'w')

    # Build the tcpdump command with optional interface argument
    tcpdump_command = ['sudo', 'tcpdump']

    if args.interface:
        tcpdump_command.extend(['-i', args.interface])

    # Run TCPdump and capture the output
    p = subprocess.Popen(tcpdump_command, stdout=subprocess.PIPE, universal_newlines=True)

    # Regular expression pattern for URL matching
    url_pattern = r'(?:Type65|AAAA)\?\s*([^\(\)\s]+)\s*\('

    # Initialize a Counter metric for URL occurrences
    url_counter = Counter('url_access_count', 'Number of times a URL is accessed', ['url', 'city', 'ip']) 
        
    # Loop through each line of output from TCPdump
    for line in iter(p.stdout.readline, ''):
        # Find URLs matching the pattern in the line
        matches = re.search(url_pattern, line)
        if matches:
            file.write(f"{matches.group(1)} - City: {city}, IP: {ip}\n")
            file.flush()

            # Increment the URL Counter metric
            url_counter.labels(matches.group(1), city, ip).inc()

    # Terminate the TCPdump process
    p.terminate()
    file.close()