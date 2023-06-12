import pandas as pd
import time
import re

# Read the file into a DataFrame
file_path = 'captured_urls.txt'
extract_file_path = 'extract.txt'
extract_df = pd.DataFrame(columns=['DOMAIN', 'HITS'])  # Initialize an empty DataFrame for extraction

def analyze_mode():
    global extract_df  # Declare extract_df as a global variable

    try:
        df = pd.read_csv(file_path, header=None, names=['domain'])

        # Reverse the order of rows to show most recent entries at the top
        df = df.iloc[::-1]

        # Count the occurrences of each URL
        url_counts = df['domain'].value_counts().reset_index()
        url_counts.columns = ['DOMAIN', 'HITS']  # Capitalize column names

        # Sort the DataFrame by index order
        url_counts = url_counts.sort_index()

        # Format the output table
        output_table = ''
        output_table += f"{'DOMAIN'.ljust(50)}{'HITS'}\n"  # Include column headers
        output_table += '-' * 60 + '\n'  # Add a separator line
        for _, row in url_counts.iterrows():
            domain = row['DOMAIN'].ljust(50)
            hits = str(row['HITS']).rjust(3)
            output_table += f"{domain}{hits}\n"

        # Clear the screen and print the formatted table
        print('\033c', end='')
        print(output_table)

        # Prompt the user for domain selection
        selected_text = input("Enter the text to extract domains: example: smile, google: Press Enter to refresh: ")
        
        if selected_text:
            # Extract the domains that contain the entered text as a substring
            selected_df = url_counts[url_counts['DOMAIN'].str.contains(selected_text, case=False)]

            if not selected_df.empty:
                # Check if the selected domains already exist in the extract_df
                existing_domains = extract_df['DOMAIN'].tolist()
                new_domains = selected_df[~selected_df['DOMAIN'].isin(existing_domains)]

                if not new_domains.empty:
                    # Update the extract_df with new_domains
                    extract_df = pd.concat([extract_df, new_domains])

                    # Sort the extract_df by hits
                    extract_df = extract_df.sort_values(by='HITS', ascending=False)

                    # Write the updated extract_df to the extract_file_path
                    extract_df.to_csv(extract_file_path, header=True, index=False, sep='\t')
                    print("Data extracted to 'extract.txt'")
                else:
                    print("Input domain already exists, Data not extracted")
            else:
                print("Input domain not requested, Data not extracted")
        else:
            print("No input provided. Data not extracted")

        # Wait for 3 seconds before refreshing the screen
        time.sleep(3)

    except Exception as e:
        print('No requests so far, please try again later')


analyze_mode()
