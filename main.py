import io
import os
import re
import csv
import sys
import time
import zipfile
import yagmail
import requests
import subprocess

from getpass import getpass
from termcolor import colored

def is_go_installed():
    # Check if go is installed
    try:
        subprocess.call('go version', shell=True)
        return True
    except Exception as e:
        return False

def unzip_file(zip_link):
    # Check if the scraper is already unzipped, if not, unzip it
    if os.path.exists('google-maps-scraper-0.9.7'):
        print(colored('=> Scraper already unzipped. Skipping unzip.', 'blue'))
        return

    r = requests.get(zip_link)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()

def build_scraper():
    # Check if the scraper is already built, if not, build it
    if os.path.exists('google-maps-scraper.exe'):
        print(colored('=> Scraper already built. Skipping build.', 'blue'))
        return

    os.chdir('google-maps-scraper-0.9.7')
    os.system('go mod download')
    os.system('go build')
    os.system('mv google-maps-scraper ../google-maps-scraper')
    os.chdir('..')

def run_scraper_with_args_for_30_seconds(args, timeout = 300):
    # Run the scraper with the specified arguments
    print(colored('=> Running scraper...', 'blue'))
    command = 'google-maps-scraper ' + args
    try:
        scraper_process = subprocess.call(command.split(' '), shell=True, timeout=float(timeout))

        if scraper_process == 0:
            subprocess.call('taskkill /f /im google-maps-scraper.exe', shell=True)
            print(colored('=> Scraper finished successfully.', 'green'))
        else:
            subprocess.call('taskkill /f /im google-maps-scraper.exe', shell=True)
            print(colored('=> Scraper finished with an error.', 'red'))
        
    except Exception as e:
        subprocess.call('taskkill /f /im google-maps-scraper.exe', shell=True)
        print(colored('An error occurred while running the scraper:', 'red'))
        print(str(e))

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

def whole_process(emails_set = False, timeout = 200):
    email_sender = input('Enter your email: ')
    email_password = getpass('Enter your password: ')
    smtp_server = input('Enter your SMTP server: ')
    smtp_port = input('Enter your SMTP port: ')
    message_subject = input('Enter your message subject: ')
    message_body = input('Enter your message.html path: ')
    keywords_file = input('Enter the name of the keywords file: ')
    output_file = input('Enter the name of the output file: ')

    print(colored('=> Checking if requirements installed...', 'blue'))
    go_installed = is_go_installed()

    if not go_installed:
        print(colored('=> GoLang is not installed.', 'bredlue'))

    print(colored('=> Downloading scraper...', 'blue'))
    
    zip_link = 'https://github.com/gosom/google-maps-scraper/archive/refs/tags/v0.9.7.zip'
    unzip_file(zip_link)

    build_scraper()

    run_scraper_with_args_for_30_seconds(f'-input {keywords_file} -results {output_file}', timeout=timeout)

    items = get_items_from_file(output_file)
    print(colored(f'=> Scraped {len(items)} items.', 'blue'))
    time.sleep(5)
    
    print(colored('=> Logging into SMTP-Server...', 'blue'))
    
    # Create a yagmail SMTP client outside the loop
    yag = yagmail.SMTP(user=email_sender, password=email_password, host=smtp_server, port=smtp_port)
    
    for item in items:
        try:
            # Check if the item's website is valid
            website = item.split(',')
            website = [w for w in website if w.startswith('http')]
            website = website[0] if len(website) > 0 else ''
            if website != '':
                test_r = requests.get(website)
                if test_r.status_code == 200:
                    if not emails_set:
                        set_email_for_website(items.index(item), website, output_file)
                    
                    # Send emails using the existing SMTP connection
                    receiver_email = item.split(',')[-1]

                    if '@' not in receiver_email:
                        print(colored(f'=> No email provided. Skipping...', 'blue'))
                        continue

                    subject = message_subject.replace('{{COMPANY_NAME}}', item[0])
                    body = open(message_body, 'r').read().replace('{{COMPANY_NAME}}', item[0])

                    print(colored(f'=> Sending email to {receiver_email}...', 'blue'))
                    
                    yag.send(
                        to=receiver_email,
                        subject=subject,
                        contents=body,
                    )

                    print(colored(f'=> Sent email to {receiver_email}', 'blue'))
                else:
                    print(colored(f'=> Website {website} is invalid. Skipping...', 'red'))
        except Exception as err:
            print(colored(f'=> Error: {err}...', 'red'))
            continue

def just_scrape(emails_set, timeout = 200):
    keywords_file = input('Enter the name of the keywords file: ')
    output_file = input('Enter the name of the output file: ')

    print(colored('=> Checking if requirements installed...', 'blue'))
    go_installed = is_go_installed()

    if not go_installed:
        print(colored('=> GoLang is not installed.', 'bredlue'))

    print(colored('=> Downloading scraper...', 'blue'))
    
    zip_link = 'https://github.com/gosom/google-maps-scraper/archive/refs/tags/v0.9.7.zip'
    unzip_file(zip_link)

    build_scraper()

    run_scraper_with_args_for_30_seconds(f'-input {keywords_file} -results {output_file}', timeout)


    items = get_items_from_file(output_file)
    print(colored(f'=> Scraped {len(items)} items.', 'blue'))
    time.sleep(5)

    if not emails_set:
        for item in items:
            try:
                # Check if the item's website is valid
                website = item.split(',')
                website = [w for w in website if w.startswith('http')]
                website = website[0] if len(website) > 0 else ''
                if website != '':
                    test_r = requests.get(website)
                    if test_r.status_code == 200:
                        set_email_for_website(items.index(item), website, output_file)
                    else:
                        print(colored(f'=> Website {website} is invalid. Skipping...', 'red'))
            except Exception as err:
                print(colored(f'=> Error: {err}...', 'red'))
                continue

    print(colored('=> Done.', 'green'))

def send_emails(emails_set = False):
    email_sender = input('Enter your email: ')
    email_password = getpass('Enter your password: ')
    smtp_server = input('Enter your SMTP server: ')
    smtp_port = input('Enter your SMTP port: ')
    message_subject = input('Enter your message subject: ')
    message_body = input('Enter your message.html path: ')
    output_file = input('Enter the name of the output file: ')

    items = get_items_from_file(output_file)
    print(colored(f'=> Scraped {len(items)} items from last session.', 'blue'))
    time.sleep(5)
    
    print(colored('=> Logging into SMTP-Server...', 'blue'))
    
    # Create a yagmail SMTP client outside the loop
    yag = yagmail.SMTP(user=email_sender, password=email_password, host=smtp_server, port=smtp_port)
    
    for item in items:
        try:
            # Check if the item's website is valid
            website = item.split(',')
            website = [w for w in website if w.startswith('http')]
            website = website[0] if len(website) > 0 else ''
            if website != '':
                test_r = requests.get(website)
                if test_r.status_code == 200:
                    if not emails_set:
                        set_email_for_website(items.index(item), website, output_file)
                    
                    # Send emails using the existing SMTP connection
                    receiver_email = item.split(',')[-1]

                    if '@' not in receiver_email:
                        print(colored(f'=> No email provided. Skipping...', 'blue'))
                        continue

                    subject = message_subject.replace('{{COMPANY_NAME}}', item[0])
                    body = open(message_body, 'r').read().replace('{{COMPANY_NAME}}', item[0])

                    print(colored(f'=> Sending email to {receiver_email}...', 'blue'))
                    
                    yag.send(
                        to=receiver_email,
                        subject=subject,
                        contents=body,
                    )

                    print(colored(f'=> Sent email to {receiver_email}', 'blue'))
                else:
                    print(colored(f'=> Website {website} is invalid. Skipping...', 'red'))
        except Exception as err:
            print(colored(f'=> Error: {err}...', 'red'))
            continue

    # Close the SMTP connection
    yag.close()

    print(colored('=> Done.', 'green'))

def main():
    args = sys.argv[1:]

    if len(args) == 0:
        print(colored('=> No arguments provided. Running default mode...', 'blue'))
        whole_process()

    for arg in args:
        if arg == "--mode":
            emails_set = input('Have you already set the emails for the scraped companies? (y/n): ')
            next_word = args[args.index(arg) + 1]
            if next_word == "default":
                if emails_set.lower() == 'y':
                    emails_set = True
                else:
                    emails_set = False
                if '--timeout' in args:
                    timeout = args[int(args.index('--timeout')) + 1]
                    whole_process(emails_set, timeout)
                else:
                    whole_process(emails_set)
            elif next_word == 'scrape':
                if '--timeout' in args:
                    timeout = args[int(args.index('--timeout')) + 1]
                    just_scrape(emails_set, timeout)
                else:
                    just_scrape(emails_set)
            elif next_word == 'email':
                emails_set = input('Have you already set the emails for the scraped companies? (y/n): ')
                if emails_set.lower() == 'y':
                    emails_set = True
                else:
                    emails_set = False
                send_emails(emails_set)
            else:
                print(colored(f'=> Invalid mode: {next_word}\n', 'red'))

                print(colored('=> Exiting...', 'blue'))
                exit()

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(colored(f'An error occurred: {err}', 'red'))
