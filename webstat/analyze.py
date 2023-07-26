import subprocess,re, time
from prometheus_client import Counter

file_path = '.analyzed.txt'
extract_file_path = 'extract.txt'
extract_data = []  # Initialize an empty list for extraction
url_counter = Counter('extracted_url_access_count', 'Number of times a URL is accessed', ['url'])
with open(extract_file_path, "w") as file:
    pass

def read_extract_file():
    # Clear the existing metrics
    url_counter.clear()

    with open(extract_file_path, 'r') as extract_file:
        lines = extract_file.readlines()
        # Skip the header line
        lines = lines[1:]
        for line in lines:
            line_parts = line.strip().split('\t')
            if len(line_parts) == 3:
                url = line_parts[1].strip()
                hits = line_parts[2].strip()
                if hits.isdigit():
                    hits = int(hits)
                    url_counter.labels(url).inc(hits)


def sniff_packets():
    file = open(file_path, 'w')

    # Run TCPdump and capture the output
    p = subprocess.Popen(['sudo', 'tcpdump'], stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.DEVNULL, close_fds=True)

    # Regular expression pattern for URL matching
    url_pattern = r'(\d+:\d+:\d+\.\d+).*?(?:Type65|AAAA)\?([^\(\)]+)\('

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

    # Terminate the TCPdump process
    p.terminate()

def sniff_analyz_mode(arg):
    print(f"Sniff mode is active and collecting HTTP information from network interface")
    print('Proceeding to analyze mode in 3 seconds...')
    sniff_packets()

def analyze_mode():

    read_extract_file()
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

        # Prompt the user for extraction option
        extraction_option = input("Select extraction option: [e] Substring-based, [i] Index-based, [d] Display domains, [Enter] Refresh: ")
        
        if extraction_option.lower() == 'e':
            selected_text = input("Enter the text to extract domains (e.g., smile, google): ")
            if selected_text:
                selected_domains = [(domain, hits) for (domain, hits) in aggregated_counts.items()
                                    if selected_text.lower() in domain.lower()]

                if selected_domains:
                    existing_domains = set([item[0] for item in extract_data])
                    new_domains = [item for item in selected_domains if item[0] not in existing_domains]

                    if new_domains:
                        extract_data.extend(new_domains)
                        extract_data.sort(key=lambda x: x[1], reverse=True)
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

        elif extraction_option.lower() == 'i':
            selected_index = input("Enter the index of the domain to extract: ")
            if selected_index.isdigit() and int(selected_index) <= len(aggregated_counts):
                selected_index = int(selected_index)
                domain = list(aggregated_counts.keys())[selected_index - 1]
                hits = list(aggregated_counts.values())[selected_index - 1]
                if domain not in extract_data:
                    extract_data.append((domain, hits))
                    with open(extract_file_path, 'a') as file:
                        file.write(f"{str(len(extract_data))}\t{domain}\t{str(hits)}\n")
                    print("Data extracted to 'extract.txt'")
                else:
                    print("Selected domain already exists in the extraction list. Data not extracted.")
            else:
                print("Invalid index. Data not extracted.")

        elif extraction_option.lower() == 'd':
            display_domains(output_table)

        elif extraction_option.lower() == 'q':
            return

        else:
            pass

        time.sleep(1)

    except FileNotFoundError:
        print("No requests so far. Please try again later.")

def display_domains(output_table):
    while True:
        print('\033c', end='')
        # Extract domains and hits from the output_table
        domain_hits = {}  # Use a dictionary to store domains and their hits
        for line in output_table.splitlines()[3:]:
            parts = line.split()
            domain = parts[1].split('.')[1]
            hits = int(parts[2])
            domain_hits[domain] = domain_hits.get(domain, 0) + hits

        # Sort the domains by hits in descending order
        sorted_domain_hits = sorted(domain_hits.items(), key=lambda x: x[1], reverse=True)

        # Display the domains with hits
        print("INDEX DOMAIN                                  HITS")
        print("------------------------------------------------------")
        index = 1
        for domain, hits in sorted_domain_hits:
            print(f"{str(index).ljust(6)}{domain.ljust(40)}{str(hits)}")
            index += 1

        user_input = input("Enter an index to display all subdomains related to the main domain, 'b' to go back, or any other key to refresh: ")
        if user_input.lower() == 'b':
            break

        if user_input.isdigit():
            index = int(user_input)
            if 1 <= index <= len(sorted_domain_hits):
                domain = sorted_domain_hits[index - 1][0]
                display_subdomains(domain)
                print(" ")
                input("Press Enter to continue...")
            else:
                print("Invalid index. Please try again.")

        # Fetch the latest output_table
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

        # Format the updated output_table
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

        time.sleep(1)


def display_subdomains(domain):
    # Fetch the latest output_table
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extract subdomains related to the main domain
    subdomains = {}
    for line in lines:
        line_parts = line.strip().split(',')
        line_domain = line_parts[0]
        timestamp = line_parts[1]
        hits = int(line_parts[2]) if len(line_parts) > 2 else 0

        if domain in line_domain:
            subdomains[line_domain] = subdomains.get(line_domain, 0) + hits

    if subdomains:
        print(f"\nSubdomains containing {domain}:")
        print("----------------------------------")
        for subdomain, hits in subdomains.items():
            print(f"{subdomain.ljust(40)}")
    else:
        print("No subdomains found containing the domain.")

    time.sleep(1)