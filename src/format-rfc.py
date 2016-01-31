#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script takes an HTML RFC as input and formats it in a prettier
# format.
import re
import sys
import pystache
from bs4 import BeautifulSoup, Tag
from template import html_template

class ProcessingException(Exception):
    pass

def process_file(infile, outfile):
    data = ''
    with open(infile) as fd:
        data = fd.read()

    soup = BeautifulSoup(data, 'html.parser')

    title = soup.head.title.text
    # Remove useless formatting:
    [node.extract() for node in soup('span', class_='grey')]
    [node.extract() for node in soup('style')]
    [node.extract() for node in soup('script')]

    # Remove the first <h1> tag --- we're already showing the title
    node = soup.find('h1')
    if node is not None:
        node.extract()

    # Remove <hr> tags:
    for match in soup.findAll('hr'):
        match.replaceWithChildren()

    # Once we've got rid of everything, remove consecutive blank lines:
    new_lines = re.compile('(\w*\n){3,99}')
    re_serialized = soup.prettify()
    contents = re.sub(new_lines, '\n\n', re_serialized)
    soup = BeautifulSoup(contents, 'html.parser')

    # Find the first pre tag and extract 
    # Finally, extract the body:
    body_contents = soup.body.find('div', class_='content')

    if body_contents is None:
        raise ProcessingException("Couldn't find a content block")

    dct = dict(rfc=body_contents.prettify(), title=title)
    rendered = pystache.render(html_template, dct)

    with open(outfile, 'w+') as fd:
        fd.write(rendered.encode('utf-8'))


def main():
    if len(sys.argv) != 3:
        print "usage: format-rfc rfc.html pretty_rfc.html"

    process_file(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
