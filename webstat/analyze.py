import subprocess
import re
import time
from prometheus_client import Counter, Summary

file_path = 'analyzed.txt'
extract_file_path = 'extract.txt'
extract_data = []  # Initialize an empty list for extraction
selected_url_metrics = {}

def sniff_packets(iface=None, show_raw=False):
    file_path = 'analyzed.txt'
    file = open(file_path, 'w')

    # Run TCPdump and capture the output
    p = subprocess.Popen(['sudo', 'tcpdump'], stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.DEVNULL, close_fds=True)

    # Regular expression pattern for URL matching
    url_pattern = r'(\d+:\d+:\d+\.\d+).*?(?:Type65|AAAA)\?([^\(\)]+)\('

    # Initialize a Counter metric for URL occurrences
    url_counter = Counter('extracted_url_access_count', 'Number of times a URL is accessed', ['url'])

    # Loop through each line of output from TCPdump
    for line in iter(p.stdout.readline, ''):
        # Find the time and URLs matching the pattern in the line
        matches = re.search(url_pattern, line)
        if matches:
            # Get the matched time and URL
            time_str = matches.group(1)
            url = matches.group(2)

            # Get the current system date
            current_date = time.strftime("%Y-%m-%d", time.localtime())

            # Combine the current date with the extracted time
            timestamp_str = f"{current_date} {time_str}"
            timestamp = int(time.mktime(time.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")))

            # Write the URL with the timestamp to the file
            file.write(f"{url},{timestamp}\n")
            file.flush()

            # Increment the URL count and the corresponding Summary metric
            url_counter.labels(url).inc()
            if url in selected_url_metrics:
                selected_url_metrics[url].observe(1)

    # Terminate the TCPdump process
    p.terminate()

def sniff_analyz_mode(arg):
    print(f"Sniff mode is active and collecting domain information from interface {arg.iface}. It is better to run this in the background.")
    print('Proceeding to analyze mode in 7 seconds...')
    sniff_packets(arg.iface, arg.show_raw)

def analyze_mode():
    global extract_data

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Reverse the order of lines to show most recent entries at the top
        lines = lines[::-1]

        # Count the occurrences of each URL and get the corresponding timestamps
        url_counts = {}
        for line in lines:
            domain, timestamp = line.strip().split(',')
            key = domain  # Remove timestamp from the key
            url_counts[key] = url_counts.get(key, 0) + 1

        # Sort the URL counts by hits in descending order
        sorted_counts = sorted(url_counts.items(), key=lambda x: x[1], reverse=True)

        # Format the output table
        output_table = ''
        output_table += f"{'INDEX'.ljust(6)}{'DOMAIN'.ljust(40)}{'HITS'}\n"  # Include column headers
        output_table += '-' * 54 + '\n'  # Add a separator line
        
        # Aggregate hits for the same domain
        aggregated_counts = {}
        for (domain, hits) in sorted_counts:
            aggregated_counts[domain] = aggregated_counts.get(domain, 0) + hits
        
        for index, (domain, hits) in enumerate(aggregated_counts.items(), start=1):
            domain = domain.ljust(40)
            output_table += f"{str(index).ljust(6)}{domain}{str(hits)}\n"

        # Clear the screen and print the formatted table
        print('\033c', end='')
        print(output_table)

        # Prompt the user for domain selection
        selected_text = input("Enter the text to extract domains (e.g., smile, google). Press Enter to refresh: ")

        if selected_text:
            # Extract the domains that contain the entered text as a substring
            selected_domains = [(domain, hits) for (domain, hits) in aggregated_counts.items()
                                if selected_text.lower() in domain.lower()]

            if selected_domains:
                # Check if the selected domains already exist in the extract_data
                existing_domains = set([item[0] for item in extract_data])
                new_domains = [item for item in selected_domains if item[0] not in existing_domains]
                for index, (domain, hits) in enumerate(selected_domains, start=1):
                    # Create a unique metric name for the selected URL
                    metric_name = f"selected_url_access_count_{index}"

                    # Create a Summary metric for the selected URL
                    selected_url_metrics[domain] = Summary(metric_name, f"Number of times {domain} is accessed")

                if new_domains:
                    # Update the extract_data with new_domains
                    extract_data.extend(new_domains)

                    # Sort the extract_data by hits
                    extract_data.sort(key=lambda x: x[1], reverse=True)

                    # Write the updated extract_data to the extract_file_path
                    with open(extract_file_path, 'w') as file:
                        file.write('INDEX\tDOMAIN\tHITS\n')
                        for index, (domain, hits) in enumerate(extract_data, start=1):
                            file.write(f"{str(index)}\t{domain}\t{str(hits)}\n")
                    print("Data extracted to 'extract.txt'")
                else:
                    print("Input domain already exists. Data not extracted.")
            else:
                print("Input domain not requested. Data not extracted.")
        else:
            print("No input provided. Data not extracted.")

        # Wait for 3 seconds before refreshing the screen
        time.sleep(3)

    except FileNotFoundError:
        print('No requests so far. Please try again later.')

for metric in selected_url_metrics.values():
    metric.collect()

analyze_mode()
