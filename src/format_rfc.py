#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script takes an HTML RFC as input and formats it in a prettier
# format.
import re
import sys
from bs4 import BeautifulSoup, Tag, Comment
from jinja2 import Environment, FileSystemLoader

class ProcessingError(Exception):
    pass

def format_rfc(infile, outfile):
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
            first_sibling = None
            last_sibling = siblings[-1]

            next_anchor = match.find('a', class_='invisible')
            if next_anchor is not None and next_anchor.next_sibling is not None:

                endline_jump = next_anchor.next_sibling
                if isinstance(endline_jump, basestring) and endline_jump == '\n':
                    empty_string = soup.new_string(' ')
                    endline_jump.replace_with(empty_string)

                first_sibling = next_anchor.next_sibling.next_sibling

            first_linefeeds = re.compile('^\\n+')
            last_linefeeds = re.compile('\\n+$')

            if isinstance(first_sibling, basestring) and first_linefeeds.match(first_sibling):
                first_sibling.string = first_linefeeds.sub('', first_sibling)

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
    body_contents = soup.body # .find('div', class_='content')

    if body_contents is None:
        raise ProcessingError("Couldn't find a content block")

    dct = dict(rfc=body_contents.prettify(), title=title)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('rfc.html')
    rendered = template.render(**dct)

    with open(outfile, 'w+') as fd:
        fd.write(rendered.encode('utf-8'))


def main():
    if len(sys.argv) != 3:
        print "usage: format-rfc rfc.html pretty_rfc.html"

    format_rfc(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
