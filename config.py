#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
    'Yankel Scialom <yankel.scialom@mail.com>'
]
__license__ = 'GPLv2'
__version__ = '0.1'

# TODO
# https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?lg=FR&isco=%25&multipleCountries=FR-R281&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=5&page=1&country=FR&totalCount=781&multipleRegions=R281
# http://www.jobijoba.com
# http://candidat.pole-emploi.fr/candidat/rechercheoffres/resultatsrechercheparparametres?lieux=34D,91R&grandDomaine=K&offresPartenaires=true

configs = {
    'debug': True,
    'rootdir': './www/dl',
    'wwwdir': './www',
    'database': 'jobs.db',
    'refreshfeeds': 3600,  # In seconds
    'refreshpages': 21600,  # In seconds
    'p2pdir': './p2p',
    'p2pservers': {
        'yankel': 'http://yankee.sierra77.free.fr/jobcatcher',
        'jesuislibre': 'http://jobs.jesuislibre.org',
        'sculo': 'http://jobcatcher.sculo.fr',
    },
    'report': {
        # dynamic: true/false
        'dynamic': True,
        # offer_per_page: int
        'offer_per_page': 15,
    },
}

configstest = {
    'debug': True,
    'rootdir': '/tmp/dl',
    'wwwdir': '/tmp/www',
    'database': '/tmp/jobs.db',
}
