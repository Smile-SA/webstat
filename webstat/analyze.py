import subprocess
import re
import os
import time
import sys
import datetime
from prometheus_client import Counter
from utils import get_ip_location

# Add a timestamp to the extract file name
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
extract_file_path = os.path.join(os.path.expanduser("~"), f'webstat_{timestamp}.txt')
file_path = '/tmp/.analyzed.txt'
extract_data = []
url_counter = Counter('extracted_url_access_count', 'Number of times a URL is accessed', ['url', 'city', 'ip'])

with open(extract_file_path, "w"):
    pass

def read_extract_file(args=None):
    # Clear the existing metrics
    url_counter.clear()

    with open(extract_file_path, 'r') as extract_file:
        lines = extract_file.readlines()[1:]
        for line in lines:
            line_parts = line.strip().split('\t')
            if len(line_parts) == 5:
                url, hits, ip, city = map(str.strip, line_parts[1:])
                if hits.isdigit():
                    hits = int(hits)
                    # Increment the URL Counter metric with the city information
                    url_counter.labels(url, city, ip).inc(hits)

def sniff_packets(args=None):
    with open(file_path, 'w'):
        pass

    tcpdump_command = ['sudo', 'tcpdump']
    if args and args.interface:
        tcpdump_command.extend(['-i', args.interface])

    # Run TCPdump and capture the output
    p = subprocess.Popen(tcpdump_command, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.DEVNULL, close_fds=True)
    url_pattern = r'(\d+:\d+:\d+\.\d+).*?(?:Type65|AAAA)\?([^\(\)]+)\('

    # Loop through each line of output from TCPdump
    for line in iter(p.stdout.readline, ''):
        # Find the time and URLs matching the pattern in the line
        matches = re.search(url_pattern, line)
        if matches:
            # Get the matched time and URL
            time_str, url = map(str.strip, matches.group(1, 2))
            current_date = time.strftime("%Y-%m-%d", time.localtime())
            timestamp_str = f"{current_date} {time_str}"
            timestamp = int(time.mktime(time.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")))
            with open(file_path, 'a') as file:
                file.write(f"{url},{timestamp}\n")
                file.flush()

    # Terminate the TCPdump process
    p.terminate()

def sniff_analyz_mode(args=None):
    print(f"Sniff mode is active and collecting HTTP information")
    print('Proceeding to analyze mode in 3 seconds...')
    sniff_packets(args=args)

def analyze_mode(args=None):
    ip_info = get_ip_location(args=args)
    city, ip = ip_info.get('city'), ip_info.get('ip')

    if args and args.interface:
        try:
            subprocess.run(['ip', 'link', 'show', 'dev', args.interface], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Interface '{args.interface}' does not exist.")
            sys.exit(1)

    read_extract_file()
    global extract_data

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()[::-1]

        url_counts = {}
        for line in lines:
            domain, timestamp = line.strip().split(',')
            key, hits = domain, url_counts.get(domain, 0) + 1
            url_counts[key] = hits

        sorted_counts = sorted(url_counts.items(), key=lambda x: x[1], reverse=True)

        output_table = f"{'INDEX'.ljust(6)}{'DOMAIN'.ljust(57)}{'HITS'.ljust(6)}{'IP'.ljust(15)} {'CITY'}\n" + '-' * 100 + '\n'

        aggregated_counts = {}
        for (domain, hits) in sorted_counts:
            aggregated_counts[domain] = aggregated_counts.get(domain, 0) + hits

        for index, (domain, hits) in enumerate(aggregated_counts.items(), start=1):
            domain = (domain[:53] + '...') if len(domain) > 57 else domain
            domain = domain.ljust(40)
            output_table += f"{str(index).ljust(6)}{domain.ljust(57)}{str(hits).ljust(6)}{str(ip).ljust(15)} {str(city).ljust(6)}\n"

        print('\033c', end='')
        print(output_table)

        extraction_option = input("Select extraction option: [e] Substring-based, [i] Index-based, [d] Display domains, [Enter] Refresh: ")

        if extraction_option.lower() == 'e':
            selected_text = input("Enter the text to extract domains (e.g., smile, google): ")
            if selected_text:
                selected_domains = [(domain, hits) for (domain, hits) in aggregated_counts.items()
                                    if selected_text.lower() in domain.lower()]

                if selected_domains:
                    existing_domains = set(item[0] for item in extract_data)
                    new_domains = [item for item in selected_domains if item[0] not in existing_domains]

                    if new_domains:
                        extract_data.extend(new_domains)
                        extract_data.sort(key=lambda x: x[1], reverse=True)
                        with open(extract_file_path, 'w') as file:
                            file.write('INDEX\tDOMAIN\tHITS\tIP\tCITY\n')
                            for index, (domain, hits) in enumerate(extract_data, start=1):
                                file.write(f"{str(index)}\t{domain}\t{str(hits)}\t{ip}\t{str(city)}\n")
                        print(f"Data extracted to '{extract_file_path}'.")
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
                    print(f"Data extracted to '{extract_file_path}'.")
                else:
                    print("Selected domain already exists in the extraction list. Data not extracted.")
            else:
                print("Invalid index. Data not extracted.")

        elif extraction_option.lower() == 'd':
            display_domains(output_table, city, ip)

        elif extraction_option.lower() == 'q':
            return

        else:
            pass

        time.sleep(1)

    except FileNotFoundError:
        print("No requests so far. Please try again later.")

def display_domains(output_table, city, ip):
    while True:
        print('\033c', end='')
        domain_hits = {}

        for line in output_table.splitlines()[3:]:
            print("LINE: " + line)
            time.sleep(7)
            parts = line.split()
            print("PARTS: ")
            print(parts)
            time.sleep(7)
            domain, hits = parts[1].split('.')[1], int(parts[2])
            print("DOMAIN: " + domain, "HITS: " + hits)
            time.sleep(7)
            domain_hits[domain] = domain_hits.get(domain, 0) + hits
            print("DOMAIN_HITS: " + domain_hits)
            time.sleep(7)

        sorted_domain_hits = sorted(domain_hits.items(), key=lambda x: x[1], reverse=True)

        output_table = f"{'INDEX'.ljust(6)}{'DOMAIN'.ljust(57)}{'HITS'.ljust(6)}{'IP'.ljust(15)} {'CITY'}\n" + '-' * 100 + '\n'
        index = 1

        for domain, hits in sorted_domain_hits:
            output_table += f"{str(index).ljust(6)}{domain.ljust(57)}{str(hits).ljust(6)}{str(ip).ljust(15)} {str(city).ljust(6)}\n"
            index += 1

        print(output_table)
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

        with open(file_path, 'r') as file:
            lines = file.readlines()[::-1]

        url_counts = {}
        for line in lines:
            domain, timestamp = line.strip().split(',')
            key, hits = domain, url_counts.get(domain, 0) + 1
            url_counts[key] = hits

        output_table = f"{'INDEX'.ljust(6)}{'DOMAIN'.ljust(40)}{'HITS'.ljust(6)}{'IP'.ljust(6)}{'CITY'.ljust(6)}\n" + '-' * 100 + '\n'
        aggregated_counts = {}

        for (domain, hits) in sorted(url_counts.items(), key=lambda x: x[1], reverse=True):
            aggregated_counts[domain] = aggregated_counts.get(domain, 0) + hits

        for index, (domain, hits) in enumerate(aggregated_counts.items(), start=1):
            domain = domain.ljust(40)
            output_table += f"{str(index).ljust(6)}{domain.ljust(57)}{str(hits).ljust(6)}{str(ip).ljust(15)}{str(city).ljust(6)}\n"

        time.sleep(1)

def display_subdomains(domain):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    subdomains = {}
    for line in lines:
        line_parts = line.strip().split(',')
        line_domain, timestamp, hits = line_parts[0], line_parts[1], int(line_parts[2]) if len(line_parts) > 2 else 0

        if domain in line_domain:
            subdomains[line_domain] = subdomains.get(line_domain, 0) + hits

    if subdomains:
        print(f"\nSubdomains containing {domain}:")
        print('-' * 100 + '\n')

        for subdomain, hits in subdomains.items():
            print(f"{subdomain.ljust(40)}")
    else:
        print("No subdomains found containing the domain.")

    time.sleep(1)
