#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script takes an HTML RFC as input and formats it in a prettier
# format.
import sys
import pystache
from bs4 import BeautifulSoup
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
    # [node.extract() for node in soup('hr', class_='noprint')]

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
