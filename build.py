#!/usr/bin/env python
# a simple incremental build script.
# usage build.py src_dir/ output_dir
import os
import sys
import subprocess
from os import listdir
from os.path import isfile, join, getmtime
from convert_txt_rfc_to_html import convert_rfc_html
from src.format_rfc import format_rfc, ProcessingError

TMP_DIR = 'html_rfcs'

def list_files(directory):
    return [f for f in listdir(directory)
              if isfile(join(directory, f)) and f.endswith('.html')]

def execute(command):
    return subprocess.call(command)

def build_file(infile, outfile):
    print "Building {}".format(outfile)

    try:
        format_rfc(infile, outfile)
    except ProcessingError:
        print "Skipping {}".format(infile)

def copy_static(out_dir):
    print "Copying static files."
    command = ['cp', '-r', 'static', out_dir]
    execute(command)

def generate_site_index(out_dir):
    print "Creating index file."
    command = ['python', 'src/generate-site-index.py', out_dir, join(out_dir, 'index.html')]
    execute(command)

def build_rfcs(src_dir, dest_dir):
    src_files = {filename: join(src_dir, filename) for filename in list_files(src_dir)}
    dest_files = {filename: join(dest_dir, filename) for filename in list_files(dest_dir)}

    for filename in src_files:
        src_path = join(src_dir, filename)
        dest_path = join(dest_dir, filename)

        if filename not in dest_files:
            build_file(src_path, dest_path)

        if os.path.exists(dest_path) and getmtime(src_path) > getmtime(dest_path):
            build_file(src_path, dest_path)


def main():
    if len(sys.argv) != 3:
        print "usage: build.py <src dir> <output dir>"
        sys.exit(-1)

    src_dir = sys.argv[1]
    dest_dir = sys.argv[2]

    #convert_rfc_html(src_dir, TMP_DIR)
    #build_rfcs(TMP_DIR, dest_dir)
    copy_static(dest_dir)
    generate_site_index(dest_dir)

if __name__ == '__main__':
    main()
