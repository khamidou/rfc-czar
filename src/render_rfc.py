# render_rfc: convert an RFC from text to HTML.
# Does the following things:
# 1. remove page breaks and signatures
# 2. add links to the table of contents
import re
import sys
from jinja2 import Environment, FileSystemLoader


def remove_top_space(data):
    topspace_regexp = re.compile(r"(\n){6}", re.MULTILINE)
    data = topspace_regexp.sub('', data, count=1)
    return data


def remove_page_breaks(data):
    pagebreak_regexp = re.compile(r"((\n){2,}^.*$\n\f$\n^.*$(\n){3,})", re.MULTILINE)
    data = pagebreak_regexp.sub(r'\n', data)
    return data


def anchor_titles(data):
    lvl1_title_rx = re.compile(r"^(\d+\.)(.*)$", re.MULTILINE)
    data = lvl1_title_rx.sub(r'\t<a name="\1"><h2>\1 \2</h2></a>', data)

    lvl2_title_rx = re.compile(r"^(\d+\.\d+\.)(.*)$", re.MULTILINE)
    data = lvl2_title_rx.sub(r'\t<a name="\1"><h3>\1 \2</h3></a>', data)

    lvl3_title_rx = re.compile(r"^(\d+\.\d+\.\d+\.)(.*)$", re.MULTILINE)
    data = lvl3_title_rx.sub(r'\t<a name="\1"><h4>\1 \2</h4></a>', data)

    return data


def render_rfc(filename):
    with open(filename) as fd:
        data = fd.read()

    out = data
    for fn in [remove_top_space, remove_page_breaks, anchor_titles]:
        out = fn(out)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('rfc.html')

    dct = dict(rfc=out)
    rendered = template.render(**dct)
    # return rendered
    return out


def main():
    print render_rfc(sys.argv[1])


if __name__ == '__main__':
    main()