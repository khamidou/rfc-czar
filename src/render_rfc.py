# render_rfc: convert an RFC from text to HTML.
# Does the following things:
# 1. remove page breaks and signatures
# 2. add links to the table of contents
import re
import sys
from bs4 import BeautifulSoup, Tag, Comment
from jinja2 import Environment, FileSystemLoader


def cleanup_author_header(data):
    header_regexp = re.compile('(^Network Working Group.+?\n\n)(.+)\n\n(Status of this Memo)', re.MULTILINE | re.DOTALL)

    def format_match(match):
        header = match.group(1).replace('\n', '<br>')
        title = match.group(2)
        status = match.group(3)

        return """<p>{}</p>
                  <h1>{}</h1>
                  <h2>{}</h2>""".format(header, title, status)

    data = header_regexp.sub(format_match, data)

    # Clean up abstract and copyright notice
    copyright_regex = re.compile('(^Copyright Notice)', re.MULTILINE)
    data = copyright_regex.sub(r'<h2>\1</h2>', data)

    abstract_regex = re.compile('(^Abstract)', re.MULTILINE)
    data = abstract_regex.sub(r'<h2>\1</h2>', data)

    return data


def cleanup_toc(data):
    # Clean up the table of contents
    # toc_regexp = re.compile(r'^\s+(.+?)\s*(.+?)(\.+)\s+\d+$', re.MULTILINE)
    toc_regexp = re.compile(r'^\s+([\d\.]+)\s+(.+)(\.+)\s*(\d+)$', re.MULTILINE)
    def format_match(match):
        section_name = match.group(1)
        title = match.group(2)

        anchor = section_name
        if anchor[-1] == '.':
            anchor = anchor[:-1]

        indent = ''
        # Indent parts depending on their section number.
        if anchor.count('.') == 2:
            indent = 'indent-1'
        elif anchor.count('.') == 3:
            indent = 'indent-2'

        return '<a href="#section-{}" class="{}">{} {}</a><br>'.format(anchor, indent,
                                                                       section_name, title)

    data = toc_regexp.sub(format_match, data)

    hl_toc_regexp = re.compile(r'^(Table of Contents)', re.IGNORECASE | re.MULTILINE)
    data = hl_toc_regexp.sub(r'<h2>\1</h2>', data)
    return data


def remove_top_space(data):
    topspace_regexp = re.compile(r"(\n){6}", re.MULTILINE)
    data = topspace_regexp.sub('', data, count=1)
    return data


def remove_page_breaks(data):
    pagebreak_regexp = re.compile(r"((\n){2,}^.*$\n\f$\n^.*$(\n){3,})", re.MULTILINE)
    data = pagebreak_regexp.sub(r'\n', data)
    return data


def create_paragraphs(data):
    paragraph_regexp = re.compile(r"(^.+?(\.|\:|;))\n\n", re.MULTILINE | re.DOTALL)

    data = paragraph_regexp.sub(r'<p class="rfcparagraph">\1</p>', data)

    return data
    # replace the \n inside those paragraphs by <br> tags.
    paragraph_pattern = re.compile(r'(<p class="rfcparagraph">.*?<\/p>)', re.MULTILINE | re.DOTALL)
    return paragraph_pattern.sub(lambda match: match.group(0).replace('\n','<br>'), data)


def create_diagram_blocks(data):
    # A boxed diagram usually starts by +-- and ends by ---+.
    diagram_regexp = re.compile(r"(\s*\+(-){2,}.+(-){2,}\+)", re.MULTILINE | re.DOTALL)
    data = diagram_regexp.sub(r'<pre>\1\n</pre>\n', data)

    # Some diagrams aren't boxed but contain a lot of ----
    #diagram_regexp = re.compile(r"(^(.+?)-{4,}(.+?)$)", re.MULTILINE)
    #data = diagram_regexp.sub(r'<pre>\1\n</pre>\n', data)
    return data


def add_line_breaks_legends(data):
    # RFC diagrams also have legends, of the form:
    # (1) ...comment...\n
    # This function replace \n by <br> to make the code more readable.
    legends_linebreak = re.compile(r'(\(\d+\).+$)\n', re.MULTILINE)
    data = legends_linebreak.sub(r'\1<br>\n', data)
    return data

def line_breaks_indented_blocks(data):
    pass

def anchor_titles(data):
    # Reverse section order because lvl1_title_rx matches the beginning of lvl2_title_rx
    # and lvl3_title_rx.
    lvl4_title_rx = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.(\d+)\.(.*)$", re.MULTILINE)
    data = lvl4_title_rx.sub(r'\t<a name="section-\1.\2.\3.\4"><h4>\1.\2.\3.\4 \5</h4></a>', data)

    lvl3_title_rx = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.(.*)$", re.MULTILINE)
    data = lvl3_title_rx.sub(r'\t<a name="section-\1.\2.\3"><h4>\1.\2.\3 \4</h4></a>', data)

    lvl2_title_rx = re.compile(r"^(\d+)\.(\d+)\.(.*)$", re.MULTILINE)
    data = lvl2_title_rx.sub(r'\t<a name="section-\1.\2"><h3>\1.\2 \3</h3></a>', data)

    lvl1_title_rx = re.compile(r"^(\d+)\.(.*)$", re.MULTILINE)
    data = lvl1_title_rx.sub(r'\t<a name="section-\1"><h2>\1. \2</h2></a>', data)

    return data


def render_rfc(filename):
    with open(filename) as fd:
        data = fd.read()

    out = data
    for fn in [remove_top_space, cleanup_author_header, remove_page_breaks,
               anchor_titles, create_paragraphs,
               add_line_breaks_legends, cleanup_toc, create_diagram_blocks]:
        out = fn(out)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('rfc.html')

    dct = dict(rfc=out)
    rendered = template.render(**dct)

    return rendered
    # return out


def main():
    print render_rfc(sys.argv[1])


if __name__ == '__main__':
    main()
