import subprocess, re
from prometheus_client import Counter


def sniff_packets():
   
    file_path = 'sniffed.txt'
    file = open(file_path, 'w')
    # Run TCPdump and capture the output
    p = subprocess.Popen(['sudo', 'tcpdump'], stdout=subprocess.PIPE, universal_newlines=True)

    # Regular expression pattern for URL matching
    url_pattern = r'(?:Type65|AAAA)\?([^\(\)]+)\('
    #re.compile(r'\bwww.*?\.(?:fr|com|us)\b', re.IGNORECASE)

    # Initialize a Counter metric for URL occurrences
    url_counter = Counter('url_access_count', 'Number of times a URL is accessed', ['url'])

    # Loop through each line of output from TCPdump
    for line in iter(p.stdout.readline, ''):
        # Find URLs matching the pattern in the line
    #    print(line)
        matches = re.search(url_pattern, line)
        if matches:
            # Push each URL as a metric
            #for url in matches:
            file.write(matches.group(1) + '\n')#

            url_counter.labels(matches.group(1)).inc()

            file.flush()

    # Terminate the TCPdump process
    p.terminate()



def sniff_mode(arg):
    print(f"Sniff mode is active and collecting HTTP information from network interface, it is better idea to run this in background")
    sniff_packets()