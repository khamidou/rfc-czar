# This script reads a stackoverflow post archive
# and creates a table of questions related to RFCs.
# Stages: 1. build table of questions
#         2. Go through every question & answer to find RFC references
#         3. Link the question and the RFC number together
#         4. Dump the result to a file.
import sys
import lxml
from collections import defaultdict

questions_table = defaultdict([])

xml_tree = None
def load_posts_file(filename):
    global xml_tree


def main():
    if len(sys.argv) != 2:
        print "usage: build-index Posts.xml"

    load_posts_file(sys.argv[1])

if __name__ == '__main__':
    main()

