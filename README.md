# Reacher

This program uses the [Google Maps Scraper](https://github.com/gosom/google-maps-scraper) to scrape Google Maps for places and then scrapes the email for each place based on their website.

## Installation

1. Install [Python 3](https://www.python.org/downloads/)
2. Install [Go](https://golang.org/doc/install)
3. Clone this repository `git clone https://github.com/FujiwaraChoki/reacher.git`
4. Install the dependencies `pip install -r requirements.txt`

## Usage

1. Run the program using one of these modes: `default`, `scrape`, `email`
```bash
python main.py --mode {default,scrape,email}
```

### Default Mode

This will scrape Google Maps places, find their corresponding email, and send them an email. Make sure
you have your HTML-File with your E-Mail contents ready.

### Scrape Mode

If Reacher is in `scrape`-mode, it will only scrape Google Maps for places and save them to a file.

### Email Mode

If Reacher is in `email`-mode, it will only find the email for each place in the file and send them an email.
You will have to provide a file with the previously scraped places.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.