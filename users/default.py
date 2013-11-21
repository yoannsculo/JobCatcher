#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
]
__license__ = 'GPLv2'
__version__ = '0.1'

configs = {
    'PoleEmploi': {
        'feeds': [
            # {
            #     'url': 'http://candidat.pole-emploi.fr/candidat/rechercheoffres/avancee.recherche',
            #     'datas': {
            #         'appelations': u'11128',
            #         'boutonValider': u'',
            #         'boutonValider:hiddenelementSubmit': u'boutonValider:hiddenelementSubmit',
            #         't:formdata': u'H4sIAAAAAAAAAO2XP08CMRjGC4mLgDEObg4mDJqYnggmChqCgzgQNV507x0Fjty1te0BLk76Afwc/knUnRhHvouLuprYclEYBZWplzTXe3tPf8+zve/NC5hqF8Amx24Dc7VorcaxsFALERdjy8Y+dqVHSYkx7PtIb/NosBeCgw3K6xAxpNRQIoaF5Gfr0KUc+56j3gGjBBMp4BGqerTMacjSNpYhu1rtrjzOvD3HQawCEi4lklN/HwVYgrlKU1mwfETqli25R+qFDgezugh1ER44TWUMDJ4OkyA57Oy3sXJjxMr0Or3eg/3RjStDp+AcxNtZkBnJhU8pU3T4U3pF/Z9ee2W15fL8dXHC3OzT0sVe9v0WTJib+5u8Wjk9tjJpmIZpmIZpmIZpmIZpmIb5b8wSKI6kdGgo1SDzdUQwV132bo1DhmHg6o46CMl3qw29RjDcZe/01XboBJ5MH3LqYiH6X0Koy44v7++2E4sL0eCmEIES6cFNW41FDbma4SIL9pCF9hbIj5GihXyvqgLoi1MSpKLqSVT9BEr0aBPDDgAA',
            #     }
            # }
        ]
    },
    'Apec': {
        'feeds' : [
            { 'url': 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101833_R712.xml'},
        ]
    },
    'cadresonline': {
        'feeds': [
            #{ 'url': 'http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=developpeur&kt=1&jc=5t.0.1.2.3.4.5.6.7-10t.0.1.2.3.4.5.6.7.8&ct=0&dt=1374746615' }
        ]
    },
    'RegionJob': {
        'feeds': [
            {'url': 'http://www.pacajob.com/fr/rss/flux.aspx?ville=9&fonction=7&qualification=3'},
            {'url': 'http://www.pacajob.com/fr/rss/flux.aspx?ville=9&fonction=9&qualification=3'},
            {'url': 'http://www.pacajob.com/fr/rss/flux.aspx?ville=9&fonction=10&qualification=3'},
        ]
    },
    'Eures': {
        'feeds': [
            { 'url': 'https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?lg=FR&isco=213&multipleCountries=FR-R281&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=99&page=1&country=FR&totalCount=1&multipleRegions=R281'}
        ]
    }
}
