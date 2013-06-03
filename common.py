# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7

# Copyright 2013 DixonD-git

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import pywikibot
from pywikibot.data.api import LoginManager
from pywikibot import config


def getWikiSite(code=None, page=None):
    if not code is None:
        if code == 'wikidata':
            return pywikibot.Site(code=code, fam=code)
        return pywikibot.Site(code=code)

    if not page is None:
        return page.site()

    return pywikibot.Site(code='uk')


def templateAliases(templateNames, getRedirectsFromWiki=False):
    templateNamespaces = {u'Шаблон:', u'шаблон:', u'Template:', u'template:'}

    # remove namespace from names
    aliases = set()
    for templateName in templateNames:
        for templateNamespace in templateNamespaces:
            if templateName.startswith(templateNamespace):
                templateName = templateName[len(templateNamespace):]
                break
        aliases.add(templateName)

    if getRedirectsFromWiki:
        templateNames = set(aliases)
        for templateName in templateNames:
            templatePage = pywikibot.Page(getWikiSite(), u'Шаблон:' + templateName)
            aliases.union(set(page.titleWithoutNamespace() for page in templatePage.getReferences(redirectsOnly=True)))

    templateNames = set(aliases)
    for templateName in templateNames:
        aliases.add(templateName[0].upper() + templateName[1:])
        aliases.add(templateName[0].lower() + templateName[1:])

    templateNames = set(aliases)
    for templateName in templateNames:
        for templateNamespace in templateNamespaces:
            aliases.add(templateNamespace + templateName)

    return aliases


def login(username, password=None, code=None, site=None):
    if site is None:
        site = getWikiSite(code=code)

    config.usernames[site.family.name][site.code] = username

    loginManager = LoginManager(user=username, site=site)
    if password is None:
        loginManager.readPassword()
    if site.user() != username:
        pywikibot.output("Logging in as " + username)
        loginManager.login()
    else:
        pywikibot.output("Already logged in as " + username)
