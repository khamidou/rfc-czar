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

    # Remove invisible anchors
    for match in soup.findAll('a', class_='invisible'):
        match.extract()

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

    # Merge the <pre class="newpage"> tags together.
    first_tag = None
    for match in soup.findAll('pre', class_='newpage'):
        if first_tag is not None:
            match.replaceWithChildren()
            match.extract()
            first_tag.append(match)

        if first_tag is None:
            first_tag = match

    # Once we've got rid of everything, remove consecutive blank lines:
    #new_lines = re.compile('(\\w*\\n){3,99}')
    #re_serialized = soup.prettify()
    #contents = re.sub(new_lines, '\\n\\n', re_serialized)
    #soup = BeautifulSoup(contents, 'html.parser')

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
