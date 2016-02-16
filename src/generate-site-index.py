# generate-site-index --- create an index.html page for the site.
import sys
from jinja2 import Environment, FileSystemLoader

def main(rfcs, outfile):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')

    dct = dict()
    rendered = template.render(**dct)

    with open(outfile, 'w+') as fd:
        fd.write(rendered.encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage: generate-site-index rfcs/ index.html"

    main(sys.argv[1], sys.argv[2])
