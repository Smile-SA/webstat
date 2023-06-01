import pandas as pd
import time

# Read the file into a DataFrame
file_path = 'captured_urls.txt'

def analyze_mode():    
    try:
        df = pd.read_csv(file_path, header=None, names=['domain'])

        # Reverse the order of rows to show most recent entries at the top
        df = df.iloc[::-1]

        # Count the occurrences of each URL
        url_counts = df['domain'].value_counts().reset_index()
        url_counts.columns = ['DOMAIN', 'HITS']  # Capitalize column names

        # Sort the DataFrame by index order
        #url_counts = url_counts.sort_index()

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

        # Wait for 3 seconds before refreshing the screen
        time.sleep(3)

    except Exception as e:
        print('No requests so far, please try again later')
