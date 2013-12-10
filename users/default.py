#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Yankel Scialom (YSC) <yankel.scialom@mail.com>',
]
__license__ = 'GPLv2'
__version__ = '0.1'

# Uncomment feed entries to enable them

configs = {
    'PoleEmploi': {
        'feeds': [
            {
                'url': 'http://candidat.pole-emploi.fr/candidat/rechercheoffres/avancee.recherche',
                'datas': {
                    'appelations': u'10316',
                    'boutonValider': u'',
                    'boutonValider:hiddenelementSubmit': u'boutonValider:hiddenelementSubmit',
                    't:formdata': 'H4sIAAAAAAAAAO1VP0sDMRxNCy62FXFwcxA6KEjO2graKqUO1qGoeOieu+baK7kkJrm2Lk76Afwc/gF1L+LY7+KiroJJD21HW6UgNHDkd7/Ly3tvePe7eQFTrQLYFNitY6Ef5nkCSws1EXUxtmxMsKt8RkucY0KQKfOoX0spwAYTNYg40mioEMdSibN16DKBie/oPeCMYqokPEJVn5UFC3naxirkV6udlceZt+c4iFVAwmVUCUb2UYAVmKs0tASLIFqzbCV8Wiu0BZg1TWia8MBpaGGgv9pcgeSgst/ayo1gK9Ntd7sP9kcnrgWdgnMQb2VBZigVhDGu2eFP2Sv6fHrtlXvL5fnr4ph5s09LF3vZ91swZt7c3/g1yOmRkckJ54TzX3KWQHEopMNCpX+KX58oFjqxu56AHMPANekMQvodW+jXg8HE7vTQdugEvkofCuZiKXtvUurLji/v77YTiwvRENAUgQaZIWCkxqJw63kQSbAHJLS2QH4EF01E/Ko2YC5OKZCKuidR9xMIE1r2DwcAAA==',
                }
            },
            {
                'url': 'http://candidat.pole-emploi.fr/candidat/rechercheoffres/avancee.recherche',
                'datas': {
                    'appelations': u'18258',
                    'boutonValider': u'',
                    'boutonValider:hiddenelementSubmit': u'boutonValider:hiddenelementSubmit',
                    't:formdata': 'H4sIAAAAAAAAAO1VP0sDMRxNCy62FXFwcxA6KEjO2graKqUO1qGoeOieu+baK7kkJrm2Lk76Afwc/gF1L+LY7+KiroJJD21HW6UgNHDkd7/Ly3tvePe7eQFTrQLYFNitY6Ef5nkCSws1EXUxtmxMsKt8RkucY0KQKfOoX0spwAYTNYg40mioEMdSibN16DKBie/oPeCMYqokPEJVn5UFC3naxirkV6udlceZt+c4iFVAwmVUCUb2UYAVmKs0tASLIFqzbCV8Wiu0BZg1TWia8MBpaGGgv9pcgeSgst/ayo1gK9Ntd7sP9kcnrgWdgnMQb2VBZigVhDGu2eFP2Sv6fHrtlXvL5fnr4ph5s09LF3vZ91swZt7c3/g1yOmRkckJ54TzX3KWQHEopMNCpX+KX58oFjqxu56AHMPANekMQvodW+jXg8HE7vTQdugEvkofCuZiKXtvUurLji/v77YTiwvRENAUgQaZIWCkxqJw63kQSbAHJLS2QH4EF01E/Ko2YC5OKZCKuidR9xMIE1r2DwcAAA==',
                }
            }

        ]
    },
    # How to add a custom feed?
    # 1. Go to <http://cadres.apec.fr/MonCompte/Flux-RSS/abonnements-flux-rss.jsp>;
    # 2. Fill the form;
    # 3. Find and click the RSS icon next to "Voici le flux RSS généré correspondant à vos critères;"
    # 4. Copy the url and add it below: "{'url': 'PASTE HERE'},";
    # 5. Swear & curse Apec.fr for not providing more custom feeds.
    'Apec': {
        'feeds': [
            # APEC, Informatique, Ile-de-France
            { 'url': 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101833_R711.xml'},
            # APEC, R&D (conception, recherche), Ile-de-France
            #{ 'url': 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101796_R711.xml'},
        ]
    },
    # How to add a custom feed?
    # 1. Go to <http://www.cadresonline.com/recherche-emploi>;
    # 2. Fill the form;
    # 3. Click "Lancer la recherche" (Search);
    # 4. Find & click the RSS logo (on the right-hand side of "x offres correspondent à votre recherche d'emploi;"
    # 5. Copy the url and add it below: "{'url': 'PASTE HERE'},".
    'cadresonline': {
        'feeds': [
            #{ 'url': 'http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=developpeur&kt=1&jc=5t.0.1.2.3.4.5.6.7-10t.0.1.2.3.4.5.6.7.8&ct=0&dt=1374746615' },
        ]
    },
    # How to add a custom feed?
    # 1. Select your region                             {REGION_CODE}
    #   See ./help/regionjobs-region-codes.txt
    # 2. Select your job sector                         {SECTOR_CODE}
    #   See ./help/regionjobs-sector-codes.txt
    # 3. Craft your feed url {URL} =
    #   http://www.{REGION_CODE}/fr/rss/flux.aspx?&fonction={SECTOR_CODE}
    # 4. Add the line {'url': '{URL}'},
    'RegionJob': {
        'feeds': [
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=7'},
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=9'},
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=10'},
        ]
    },
    # How to add a custom feed?
    # 1. Select your country                            {COUNTRY_CODE}
    #   See ./help/eures-contry-codes.txt
    # 2. Select your region                             {REGION_CODE}
    #   See ./help/eures-region-codes.txt
    # 3. Select your job sector                         {SECTOR_CODE}
    #   See ./help/eures-sector-codes.txt
    # 4. Craft your feed url {URL} =
    #   https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?country={COUNTRY_CODE}&multipleRegions={REGION_CODE}&isco={SECTOR_CODE}&lg=FR&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=99&page=1&totalCount=1
    # 5. Add the line {'url': '{URL}'},
    'Eures': {
        'feeds': [
            # France (FR), Ile-de-France (R21), Concepteurs et analystes de systèmes informatiques (2131)
            # { 'url': 'https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?country=FR&multipleRegions=R21&isco=2131&lg=FR&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=99&page=1&totalCount=1'},
            # Allemagne (DE), Berlin (R1B), Pompiers (5161)
            # { 'url': 'https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?country=DE&multipleRegions=R1B&isco=5161&lg=FR&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=99&page=1&totalCount=1'},
        ]
    }
}
