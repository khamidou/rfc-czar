# We're getting RFCs from the IETF's rsync server.
# These RFCs are in text format, so we need to use the
# IETF's rfcmarkup to convert them to HTML. This html is
# then used by format-rfc to make a pretty rfc.
import sys
import subprocess
from os import listdir
from os.path import (isfile, join, getmtime, splitext,
                     basename, dirname)


def list_files(directory, extension=''):
    l = []
    files = listdir(directory)

    for f in files:
        filename, ext = splitext(f)
        if isfile(join(directory, f)) and extension in ext:
            l.append(filename)
    return l


def build_file(infile, outfile):
    with open(outfile, 'w+') as fd:
        command = ['python', 'src/rfcmarkup', dirname(infile), infile]
        subprocess.call(command, stdout=fd)

def convert_rfc_html(src_dir, dest_dir):
    src_files = {filename: join(src_dir, filename) for filename in list_files(src_dir, 'txt')}
    dest_files = {filename: join(dest_dir, filename) for filename in list_files(dest_dir, 'html')}

    for filename in src_files:
        src_path = join(src_dir, filename) + '.txt'
        dest_path = join(dest_dir, filename) + '.html'

        if filename not in dest_files or getmtime(src_path) > getmtime(dest_path):
            print "Building {}".format(src_path)
            build_file(src_path, dest_path)


if __name__ == '__main__':
    main()
