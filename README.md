# JobCatcher

![JobCatcher Screenshot](https://raw.github.com/yoannsculo/JobCatcher/master/screenshots/jobcatcher.png)

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

## Usage (mainly development options for now)

	./jobcatcher.py -b # To load my blacklist into the DB
	./jobcatcher.py -f # To flush and update the blacklist
	./jobcatcher.py -s # To fetch last offers
	./jobcatcher.py -p # To download a related page
	./jobcatcher.py -i # Insert data to jobboard table
	./jobcatcher.py -m # Move jobboard datas to offers table
	./jobcatcher.py -r # To generate reports
	./jobcatcher.py -u # To fetch an offer only with its url
	./jobcatcher.py -a # Sync the blacklist, fetch the offers and generates reports.

Reports are generated into the local "www" directory.

I start jobcatcher.py -s manually with crontab for now. But this should change
soon.

# List of supported Job Boards

- Apec.fr (France)
- Progressive Recruitment (France)
- RegionsJob
 - RegionCentre (France)
 - RegionOuest (France)
 - RegionSudOuest (France)
- Cadreonline (France)
- Eures (Europe)

### TODO

- Lolix.org (France)
- Linux.com (Int.)
- L'eXpress-Board (France)
- Remixjobs.com (France)

## Installation

### Debian

    # Install a packages
    apt-get update
    apt-get install python-pip git virtualenv virtualenvwrapper


    # Configure virtualenvwrapper
    cat << EOF >> ~/.bashrc
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/Devel
    source /usr/local/bin/virtualenvwrapper.sh
    EOF
    source ~/.bashrc
    
    # Prepare jobcatcher environment
    mkvirtualenv --no-site-packages -p /usr/bin/python2.7 jobcatcher
    add2virtualenv /opt/JobCatcher

    # Install jobcatcher project
    cd opt
    git clone -b unstable https://github.com/badele/JobCatcher.git
    cd JobCatcher
    pip install -r requirements.txt

## Utilisation

Modify the config.py and execute

    workon jobcatcher
    python jobcatcher.py -a


Help me to add new job boards to JobCatcher ! :)
