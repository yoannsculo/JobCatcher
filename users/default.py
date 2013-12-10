#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
    'Yoann Sculo <yoann.sculo@gmail.com>',
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
    'Apec': {
        'feeds': [
            { 'url': 'http://www.apec.fr/fluxRss/XML/OffresCadre_F101833_R711.xml'}
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
            #{ 'url': 'http://www.cadresonline.com/resultat-emploi/feed.rss?flux=1&kw=developpeur&kt=1&jc=5t.0.1.2.3.4.5.6.7-10t.0.1.2.3.4.5.6.7.8&ct=0&dt=1374746615' }
        ]
    },
    'RegionJob': {
        'feeds': [
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=7'},
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=9'},
            {'url': 'http://www.parisjob.com/fr/rss/flux.aspx?&fonction=10'},
        ]
    },
    'Eures': {
        'feeds': [
            #{ 'url': 'https://ec.europa.eu/eures/eures-searchengine/servlet/BrowseCountryJVsServlet?lg=FR&isco=213&multipleCountries=FR-R281&date=01%2F01%2F1975&title=&durex=&exp=&serviceUri=browse&qual=&pageSize=99&page=1&country=FR&totalCount=1&multipleRegions=R281'}
        ]
    }
}
