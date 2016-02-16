#!/usr/bin/env python
# a simple incremental build script.
# usage build.py src_dir/ output_dir
import sys
import subprocess
from os import listdir
from os.path import isfile, join, getmtime


def list_files(directory):
    return [f for f in listdir(directory)
              if isfile(join(directory, f)) and f.endswith('.html')]


def build_file(infile, outfile):
    command = ['python', 'src/format-rfc.py', infile, outfile]
    print " ".join(command)
    return subprocess.call(command)


def main():
    if len(sys.argv) != 3:
        print "usage: build.py <src dir> <output dir>"
        sys.exit(-1)

    src_dir = sys.argv[1]
    dest_dir = sys.argv[2]

    src_files = {filename: join(src_dir, filename) for filename in list_files(src_dir)}
    dest_files = {filename: join(dest_dir, filename) for filename in list_files(dest_dir)}

    for filename in src_files:
        src_path = join(src_dir, filename)
        dest_path = join(dest_dir, filename)

        if filename not in dest_files:
            build_file(src_path, dest_path)

        if getmtime(src_path) > getmtime(dest_path):
            build_file(src_path, dest_path)


if __name__ == '__main__':
    main()
