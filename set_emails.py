import re
import csv
import time
import requests
from bs4 import BeautifulSoup
from termcolor import colored

def get_items_from_file(file_name):
    # Read and return items from a file
    with open(file_name, 'r', errors='ignore') as f:
        items = f.readlines()
        items = [item.strip() for item in items[1:]]
        return items
    

def set_email_for_website(index, website, output_file):
    # Extract and set an email for a website
    email = ''

    r = requests.get(website)
    if r.status_code == 200:
        # Define a regular expression pattern to match email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        # Find all email addresses in the HTML string
        email_addresses = re.findall(email_pattern, r.text)

        email = email_addresses[0] if len(email_addresses) > 0 else ''

    if email:
        print(f'=> Setting email {email} for website {website}')
        with open(output_file, 'r', newline='', errors='ignore') as csvfile:
            csvreader = csv.reader(csvfile)
            items = list(csvreader)
            items[index].append(email)

        with open(output_file, 'w', newline='', errors='ignore') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(items)


def main():
    items = get_items_from_file("results.csv")
    print(colored(f'=> Scraped {len(items)} items.', 'blue'))
    time.sleep(5)
        
    for item in items:
        # Check if the item's website is valid
        website = item.split(',')
        website = [w for w in website if w.startswith('http')]
        website = website[0] if len(website) > 0 else ''
        if website != '':
            test_r = requests.get(website)
            if test_r.status_code == 200:
                set_email_for_website(items.index(item), website, "results.csv")

main()