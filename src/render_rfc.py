# render_rfc: convert an RFC from text to HTML.
# Does the following things:
# 1. remove page breaks and signatures
# 2. add links to the table of contents
import re
import sys
import json
from jinja2 import Environment, FileSystemLoader

# A dictionary containing metadata about the RFC. We
# fill it out as we go through the file.
metadata = dict()


def cleanup_author_header(data, **kwargs):
    rfc_number_regexp = re.compile(r'Request for Comments:\s+(\d+)', re.MULTILINE | re.IGNORECASE)
    rfc_number = rfc_number_regexp.search(data)

    if rfc_number is not None:
        metadata['rfc'] = int(rfc_number.group(1))

    header_regexp = re.compile('(^Network Working Group.+?\n\n)(.+)\n\n(Status of this Memo)', re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def format_match(match):
        header = match.group(1).replace('\n', '<br>')
        title = match.group(2)
        status = match.group(3)

        metadata['title'] = title.strip().replace('\n', '')

        return """<p>{}</p>
                  <h1>{}</h1>
                  <h2>{}</h2>""".format(header, title, status)

    data = header_regexp.sub(format_match, data)


    # Clean up abstract and copyright notice
    copyright_regex = re.compile('(^Copyright Notice)', re.MULTILINE | re.IGNORECASE)
    data = copyright_regex.sub(r'<h2>\1</h2>', data)

    abstract_regex = re.compile('(^Abstract)', re.MULTILINE | re.IGNORECASE)
    data = abstract_regex.sub(r'<h2>\1</h2>', data)

    return data


def cleanup_toc(data, **kwargs):
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
        if anchor.count('.') == 1:
            indent = 'indent-1'
        elif anchor.count('.') == 2:
            indent = 'indent-2'

        return """<a href="#section-{}" class="{}">{} {}</a><br>""".format(anchor, indent, section_name, title)

    data = toc_regexp.sub(format_match, data)

    hl_toc_regexp = re.compile(r'^(Table of Contents)', re.IGNORECASE | re.MULTILINE)
    data = hl_toc_regexp.sub(r'<h2>\1</h2>', data)
    return data


def remove_top_space(data, **kwargs):
    topspace_regexp = re.compile(r"(\n){6}", re.MULTILINE)
    data = topspace_regexp.sub('', data, count=1)
    return data


def remove_page_breaks(data, **kwargs):
    pagebreak_regexp = re.compile(r"((\n){2,}^.*$\n\f$\n^.*$(\n){3,})", re.MULTILINE)
    data = pagebreak_regexp.sub(r'\n', data)
    return data


def create_paragraphs(data, **kwargs):
    paragraph_regexp = re.compile(r"(^.+?(\.|\:|;))\n\n", re.MULTILINE | re.DOTALL)

    def format_match(match):
        paragraph = match.group(0)
        escaped_raw = paragraph.replace('"', '\"')

        return """<p class="rfcparagraph">{}</p>""".format(paragraph)


    data = paragraph_regexp.sub(format_match, data)

    return data


def create_diagram_blocks(data, **kwargs):
    # A boxed diagram usually starts by +-- and ends by ---+.
    diagram_regexp = re.compile(r"(\s*\+(-){2,}.+(-){2,}\+)", re.MULTILINE | re.DOTALL)
    data = diagram_regexp.sub(r'<pre>\1\n</pre>\n', data)

    # Some diagrams aren't boxed but contain a lot of ----
    #diagram_regexp = re.compile(r"(^(.+?)-{4,}(.+?)$)", re.MULTILINE)
    #data = diagram_regexp.sub(r'<pre>\1\n</pre>\n', data)
    return data


def add_line_breaks_legends(data, **kwargs):
    # RFC diagrams also have legends, of the form:
    # (1) ...comment...\n
    # This function replace \n by <br> to make the code more readable.
    legends_linebreak = re.compile(r'(\(\d+\).+$)\n', re.MULTILINE)
    data = legends_linebreak.sub(r'\1<br>\n', data)
    return data

def line_breaks_indented_blocks(data, **kwargs):
    pass

def anchor_titles(data, **kwargs):
    filename = kwargs['filename']

    # Reverse section order because lvl1_title_rx matches the beginning of lvl2_title_rx
    # and lvl3_title_rx.
    lvl4_title_rx = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.(\d+)\.*(.*)$", re.MULTILINE)
    lvl4_template = r"""<a name="section-\1.\2.\3.\4"><h4>\1.\2.\3.\4 \5</h4></a>
                    """.format(filename)

    data = lvl4_title_rx.sub(lvl4_template, data)

    lvl3_title_rx = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.*(.*)$", re.MULTILINE)
    lvl3_template = r"""\t<a name="section-\1.\2.\3"><h4>\1.\2.\3 \4</h4></a>"""
    data = lvl3_title_rx.sub(lvl3_template, data)

    lvl2_title_rx = re.compile(r"^(\d+)\.(\d+)\.*(.*)$", re.MULTILINE)
    data = lvl2_title_rx.sub(r'\t<a name="section-\1.\2"><h3>\1.\2 \3</h3></a>', data)

    lvl1_title_rx = re.compile(r"^(\d+)\.*(.*)$", re.MULTILINE)
    data = lvl1_title_rx.sub(r'\t<a name="section-\1"><h2>\1. \2</h2></a>', data)

    return data


def render_rfc(filename):
    with open(filename) as fd:
        data = fd.read()

    out = data
    opts = dict(filename=filename)

    for fn in [remove_top_space, cleanup_author_header, remove_page_breaks,
               anchor_titles, create_paragraphs,
               add_line_breaks_legends, cleanup_toc, create_diagram_blocks]:
        out = fn(out, **opts)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('rfc.html')

    dct = dict(rfc=out)
    rendered = template.render(**dct)

    return rendered
    # return out


def main():
    infile = sys.argv[1]
    outfile = sys.argv[2]

    with open(outfile, 'w+') as fd:
        fd.write(render_rfc(infile))

    json_filename = outfile.split('.')[0] + '.json'
    with open(json_filename, 'w+') as fd:
        json.dump(metadata, fd)

if __name__ == '__main__':
    main()
