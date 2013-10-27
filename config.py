#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__license__ = 'GPLv2'
__version__ = '0.1'

configs = {
    'global': {
        'debug': False,
        'ignorefeeds': [
            # 'SUDOUESTJOB',
            # 'OUESTJOB',
            # 'CENTREJOB',
            # 'PROGRESSIVE',
            # 'Lolix',

            # 'APEC',
            # 'Cadresonline',
        ]
    },
    'apec': {
        'feeds' : [
            'http://www.apec.fr/fluxRss/XML/OffresCadre_F101833.xml', # informatique
            'http://www.apec.fr/fluxRss/XML/OffresCadre_F101810.xml', # informatique industrielle
            'http://www.apec.fr/fluxRss/XML/OffresCadre_F101813.xml', # système, réseaux, donnée
            # 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101835_R712.xml', # RH
            # 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101836_R712.xml', # Culture
            # 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101832_R712.xml', # Finance
        ]
    },
    'cadresonline': {
        'feeds': [
            'http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=developpeur&kt=1&jc=5t.0.1.2.3.4.5.6.7-10t.0.1.2.3.4.5.6.7.8&ct=0&dt=1374746615',
            # 'http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kt=1&sr=12t.0.1.2.3.4&jc=0f.0.1.3.4.6-1f.5.6-2f.0.1-3f.3-4f.2-7t.0.1.2-8t.0.1.2-17t.0.1.2.3.4.5.6-19f.0.7&dt=1382823937',
        ]
    },
    'regionjob': {
        'feeds': [
            'http://www.pacajob.com/fr/rss/flux.aspx?&fonction=22&qualification=2',
            # 'http://www.pacajob.com/fr/rss/flux.aspx?ville=9&fonction=19'
        ]
    }

}
