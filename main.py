import io
import os
import csv
import time
import zipfile
import requests
import subprocess
from termcolor import colored
from bs4 import BeautifulSoup

def unzip_file(zip_link):
    if os.path.exists('google-maps-scraper-0.9.7'):
        print(colored('=> Scraper already unzipped. Skipping unzip.', 'blue'))
        return

    r = requests.get(zip_link)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()

def build_scraper():
    if os.path.exists('google-maps-scraper.exe'):
        print(colored('=> Scraper already built. Skipping build.', 'blue'))
        return

    os.chdir('google-maps-scraper-0.9.7')
    os.system('go mod download')
    os.system('go build')
    os.system('mv google-maps-scraper ../google-maps-scraper')
    os.chdir('..')

def run_scraper_with_args_for_30_seconds(args):
    command = 'google-maps-scraper ' + args
    try:
        scraper_process = subprocess.call(command.split(' '), shell=True, timeout=200)

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
    with open(file_name, 'r', errors='ignore') as f:
        items = f.readlines()
        items = [item.strip() for item in items[1:]]
        return items
    
def set_email_for_website(index, website, output_file):
    email = ''

    r = requests.get(website)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        email_tags = soup.find_all('a')
        email_list = [e.text for e in email_tags if '@' in e.text]

        email_list = [e for e in email_list if len(e.split('@')[0]) > 0]
        email = email_list[0] if len(email_list) > 0 else ''

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
    zip_link = 'https://github.com/gosom/google-maps-scraper/archive/refs/tags/v0.9.7.zip'
    unzip_file(zip_link)

    build_scraper()

    keywords_file = input('Enter the name of the keywords file: ')
    output_file = input('Enter the name of the output file: ')

    run_scraper_with_args_for_30_seconds(f'-input {keywords_file} -results {output_file} -exit-on-inactivity 3m')

    items = get_items_from_file(output_file)
    print(f'=> Scraped {len(items)} items.')
    time.sleep(5)
    for item in items:
        # Find the website, starts with http
        website = item.split(',')
        website = [w for w in website if w.startswith('http')]
        website = website[0] if len(website) > 0 else ''
        if website != '':
            set_email_for_website(items.index(item), website, output_file)

    print(colored('=> Done.', 'green'))

if __name__ == '__main__':
    main()