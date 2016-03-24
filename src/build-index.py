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


def build_post_index(tree):
    questions_table = defaultdict(dict)

    # Get all the questions.
    for post in tree.findall('//row[@PostTypeId="1"]'):
        title = post.get('Title')
        print title
        post_id = int(post.get('Id'))
        url = "https://stackoverflow.com/questions/{}/".format(post_id)

        questions_table[post_id] = dict(title=title, post_id=post_id, url=url)

    return questions_table


# Create a mapping between RFCs and stack exchange questions.
def build_rfc_index(filename):
    rfcs_table = defaultdict(list)
    rfc_regexp = re.compile(r'RFC\s*(\d+)', re.IGNORECASE)

    count = 0
    with open(filename) as fd:
        # Get all the comments.
        for _, post in etree.iterparse(fd, events=('end',), tag='row'):
            if post.get('PostTypeId') != '2':
                continue

            count += 1
            if count % 10000 == 0:
                print count

            body = post.get('Body')
            parent_post = int(post.get('ParentId'))

            for match in rfc_regexp.findall(body):
                # FIXME: we're limiting ourselves to top-level replies.
                # Maybe do the same for replies to replies?
                rfc_id = int(match)
                rfcs_table[rfc_id].append(parent_post)

        # Dedupe.
        for rfc in rfcs_table:
            rfcs_table[rfc] = list(set(rfcs_table[rfc]))

        return rfcs_table


def main():
    if len(sys.argv) != 2:
        print "usage: build-index Posts.xml"

    filename = sys.argv[1]
    print "Building RFC index"
    rfc_index = build_rfc_index(filename)

    with open('rfc_index.json', 'w+') as fd:
        json.dump(rfc_index, fd, indent=4)


if __name__ == '__main__':
    main()

