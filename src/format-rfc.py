#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script takes an HTML RFC as input and formats it in a prettier
# format.
import re
import sys
import pystache
from bs4 import BeautifulSoup, Tag, Comment
from template import html_template

class ProcessingException(Exception):
    pass

def process_file(infile, outfile):
    data = ''
    with open(infile) as fd:
        data = fd.read()

    data = data.replace('<br>', '')
    soup = BeautifulSoup(data, 'html.parser')

    title = soup.head.title.text
    # Remove useless formatting:
    [node.extract() for node in soup('span', class_='grey')]
    [node.extract() for node in soup('style')]
    [node.extract() for node in soup('script')]

    # Remove comments:
    for comment in soup.find_all():
        if isinstance(comment, Comment):
            comment.extract()

    # Remove the first <h1> tag --- we're already showing the title
    match = soup.find('h1')
    if match is not None:
        match.extract()

    empty_chars = re.compile('^[\\n]+$')
    indented_blanks = re.compile('^\\n+(\s+)$')

    # Remove invisible anchors
    for match in soup.findAll('a', class_='invisible'):
        match.contents = ''

        # Also remove empty lines after this tag
        for i, sibling in enumerate(match.next_siblings):
            if not isinstance(sibling, basestring):
                break

            if re.match(empty_chars, sibling):
                sibling.string = ''
            elif re.match(indented_blanks, sibling):
                sibling.string = indented_blanks.sub('\\1', sibling)

    # Remove useless line jumps at the beginning and end of a pre tag.
    for match in soup.findAll('pre'):
        if match is not None:
            siblings = list(match.strings)
            first_sibling = siblings[1]
            last_sibling = siblings[-1]

            first_linefeeds = re.compile('^\\n+')
            last_linefeeds = re.compile('\\n+$')

            if isinstance(first_sibling, basestring):
                replacement = first_linefeeds.split(first_sibling.string)[0]
                if first_sibling != replacement:
                    first_sibling.replaceWith(replacement)

            if isinstance(last_sibling, basestring):
                replacement = last_linefeeds.split(last_sibling.string)[0]
                last_sibling.replaceWith(replacement)

    # Remove those weird <span class='h4'></span> tags:
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10']:
        for match in soup.findAll('span', class_=tag):
            match.replaceWithChildren()

        # Strip the blocks following this span.
        for match in soup.findAll(tag):
            sibling = match.next_sibling

            if sibling is not None:
                sibling.string.replaceWith(sibling.string.strip('\n').rstrip('\n'))

    # Remove <hr> tags:
    for match in soup.findAll('hr'):
        if match is not None:
            match.replaceWithChildren()

    # Add a bit more space around the first pre tag (which is actually the
    # intro of the doc).
    #first_pre = soup.find('pre')
    #first_pre.contents.insert(0, 'YOLO')

    # Once we've got rid of everything, remove consecutive blank lines:
    new_lines = re.compile('(\\w*\\n){3,99}')
    re_serialized = soup.prettify()
    contents = re.sub(new_lines, '\\n\\n', re_serialized)
    soup = BeautifulSoup(contents, 'html.parser')

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
