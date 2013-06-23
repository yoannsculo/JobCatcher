# JobCatcher

JobCatcher is a daemon that retrieves job offers from multiple job boards feeds
and generates custom RSS feeds and HTML reports for you. This is a decentralized
software meant to run of your own server.

JobCatcher comes with a filter feature, so you can filter company names with
black or whitelists.

Think of it as a RSS feed reader with filter feature.

I would like this software to be under GPLv2 License. But I need to check if
this is compatible with dependencies I've choosen.

## Work in Progress

The project is fully in development and many features need to be implemented.
It is developed in Python. This is my first time I use Python on a non-basic
project. So I guess my code is not so pythonic ... yet. Feel free to help me or
show me mistakes I could have made or improvements I could do.

## Dependencies

	python-html2text, python-requests, python-beautifulsoup

## Usage

	./jobcatcher.py -c # To create database
	./jobcatcher.py -b # To load my blacklist into the DB
	./jobcatcher.py -s # To fetch last offers
	./jobcatcher.py -r # To generate reports

Reports are generated into the local "www" directory.

I start jobcatcher.py -s manually with crontab for now. But this should change
soon.

# List of supported Job Boards

- Apec.fr (French)
- Lolix.org (French) TODO
- Linux.com (English) TODO
- L'eXpress-Board (French) TODO
- Remixjobs.com (French) TODO

Help me to add new job boards to JobCatcher ! :)
