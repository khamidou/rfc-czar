# This script reads a stackoverflow post archive
# and creates a table of questions related to RFCs.
# Stages: 1. build table of questions
#         2. Go through every question & answer to find RFC references
#         3. Link the question and the RFC number together
#         4. Dump the result to a file.
import re
import sys
import json
from lxml import etree
from collections import defaultdict


def load_posts_file(filename):
    xml_tree = None
    with open(filename) as fd:
        xml_tree = etree.parse(fd)

    return xml_tree


def build_post_index(tree):
    questions_table = defaultdict(dict)

    # Get all the questions.
    for post in tree.findall('//row[@PostTypeId="1"]'):
        title = post.get('Title')
        post_id = int(post.get('Id'))
        url = "https://stackoverflow.com/questions/{}/".format(post_id)

        questions_table[post_id] = dict(title=title, post_id=post_id, url=url)

    return questions_table


# Create a mapping between RFCs and stack exchange questions.
def build_rfc_index(tree, post_index):
    rfcs_table = defaultdict(list)
    rfc_regexp = re.compile(r'RFC\s*(\d+)', re.IGNORECASE)

    # Get all the comments.
    for post in tree.findall('//row[@PostTypeId="2"]'):
        body = post.get('Body')
        parent_post = int(post.get('ParentId'))

        for match in rfc_regexp.findall(body):
            # FIXME: we're limiting ourselves to top-level replies.
            # Maybe do the same for replies to replies?
            rfc_id = int(match)

            if parent_post in post_index:
                rfcs_table[rfc_id].append(parent_post)

    # Dedupe.
    for rfc in rfcs_table:
        rfcs_table[rfc] = list(set(rfcs_table[rfc]))

    return rfcs_table


# The post index is big. Only keep posts which are related to an RFC.
def optimize_post_index(rfc_index, post_index):
    posts = [item for sublist in rfc_index.values() for item in sublist]
    optimized_index = dict()

    for post in posts:
        if post in post_index:
            optimized_index[post] = post_index[post]

    return optimized_index


def main():
    if len(sys.argv) != 2:
        print "usage: build-index Posts.xml"

    print "Building tree"
    tree = load_posts_file(sys.argv[1])

    print "Building post index"
    post_index = build_post_index(tree)

    print "Building RFC index"
    rfc_index = build_rfc_index(tree, post_index)

    print "Building optimized index"
    optimized_index = optimize_post_index(rfc_index, post_index)


    with open('post_index.json', 'w+') as fd:
        json.dump(optimized_index, fd, indent=4)

    with open('rfc_index.json', 'w+') as fd:
        json.dump(rfc_index, fd, indent=4)


if __name__ == '__main__':
    main()

