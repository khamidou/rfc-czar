# render_rfc: convert an RFC from text to HTML.
# Does the following things:
# 1. remove page breaks and signatures
# 2. add links to the table of contents
import re
import sys


def remove_top_space(data):
    topspace_regexp = re.compile(r"^(\n){4,}", re.MULTILINE)
    data = topspace_regexp.sub('', data, count=1)
    return data

def remove_page_breaks(data):
    pagebreak_regexp = re.compile(r"((\n){2,}^.*$\n\f$\n^.*$(\n){3,})", re.MULTILINE)
    data = pagebreak_regexp.sub(r'\n', data)
    return data


def render_rfc(filename):
    with open(filename) as fd:
        data = fd.read()

    for fn in [remove_top_space, remove_page_breaks]:
        out = fn(data)

    return out


def main():
    print render_rfc(sys.argv[1])


if __name__ == '__main__':
    main()
