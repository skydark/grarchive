#!/usr/bin/python2
# -*- coding: utf8 -*-


USERNAME, PASSWORD = 'Your username', 'Your password'
SUBSCRIPTION_XML = 'subscriptions.xml'
BASE_DIR = u'outdir'
NO_CATEGORY = u''


GR_URL = 'https://www.google.com/reader/atom/feed/'
GR_PARAMETERS = {'r': 'n', 'n': '1000'}


import os
from lxml import etree
import itertools
from collections import namedtuple

from auth import ClientAuthMethod


Feed = namedtuple('Feed', 'title url category'.split())


def node_to_feed(node):
    attr = node.attrib
    category = node.getparent().attrib.get('title', NO_CATEGORY)
    return Feed(title=attr['title'], url=attr['xmlUrl'], category=category)


def get_feeds(xml):
    doc = etree.parse(xml)
    outlines = doc.findall('body//outline[@xmlUrl]')
    feeds = map(node_to_feed, outlines)
    return feeds


def normalize(title):
    return title.replace('/', ' ')


def main():
    auth = ClientAuthMethod(USERNAME, PASSWORD)
    feeds = get_feeds(SUBSCRIPTION_XML)
    for feed in feeds:
        print(u'Processing {} in {}: {}'.format(
            feed.title, feed.category, feed.url))
        url = GR_URL + feed.url
        content = auth.get(url, GR_PARAMETERS)
        content = content.encode('utf8')
        dir = os.path.join(BASE_DIR, normalize(feed.category))
        if not os.path.isdir(dir):
            os.makedirs(dir)
        outfile_base = os.path.join(dir, normalize(feed.title))
        outfile = outfile_base
        for retry in itertools.count():
            if retry == 0:
                outfile = u'{}.xml'.format(outfile_base)
            else:
                outfile = u'{} ({}).xml'.format(outfile_base, retry)
            if not os.path.exists(outfile):
                break
        open(outfile, 'wb').write(content)


if __name__ == '__main__':
    main()
