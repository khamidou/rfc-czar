# generate-site-index --- create an index.html page for the site.
import os
import sys
import json
from os import listdir
from jinja2 import Environment, FileSystemLoader

def build_metadata_index(folder):
    metadata_table = {}

    metadata_files = [os.path.join(folder, f) for f in listdir(folder) if '.json' in f]
    for metadata in metadata_files:
        with open(metadata) as fd:
            metadata = json.load(fd)
            if 'rfc' in metadata:
                metadata_table[metadata['rfc']] = metadata

    return metadata_table

def main(rfcs, outfile):
    rfcs = build_metadata_index(rfcs)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')

    dct = dict(rfcs=rfcs.values())
    rendered = template.render(**dct)

    with open(outfile, 'w+') as fd:
        fd.write(rendered.encode('utf-8'))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage: generate-site-index rfcs/ index.html"

    main(sys.argv[1], sys.argv[2])
