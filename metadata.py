# metadata.py --- generate a metadata.json file
# containing RFCs numbers, titles and summaries.
import os
import re
import sys
import json
import glob
from multiprocessing import Pool


def collect_metadata(file_name):
    metadata = dict()

    print "Processing %s" % file_name
    with open(file_name, 'r') as fd:
        data = fd.read()

        rfc_number_regexp = re.compile(r'Request for Comments:\s+(\d+)', re.MULTILINE | re.IGNORECASE)
        rfc_number = rfc_number_regexp.search(data)

        if rfc_number is not None:
            metadata['rfc'] = int(rfc_number.group(1))

        header_regexp = re.compile('(^Network Working Group.+?\n\n)(.+)\n\n(Status of this Memo)', re.MULTILINE | re.DOTALL | re.IGNORECASE)
        header_data = header_regexp.search(data)
        if header_data is not None:
            original_title = header_data.group(2).lstrip().rstrip().split('\n')
            subject = original_title[0].capitalize()
            metadata['subject'] = subject

        #subject_regex = re.compile('Request for Comments.+\n{2,}(.+)\n{2,}\s*(Status of this Memo|STATUS OF THIS MEMO)', re.MULTILINE | re.DOTALL)
        #subject_data = subject_regex.search(data)

        #if subject_data is not None:
        #    subject = subject_data.group(1).lstrip().rstrip().capitalize()
        #    metadata['subject'] = subject

    return metadata


def create_metadata(folder_name):
    globbing_rule = os.path.join(folder_name, 'rfc[0-9]*.txt')

    metadata = dict()

    # KILL_LIST: a list of badly formatted RFCs which we can't process
    # yet.
    KILL_LIST = ['rfc1147.txt']
    rfc_list = [rfc for rfc in glob.glob(globbing_rule) if not os.path.basename(rfc) in KILL_LIST]

    p = Pool(8)

    results = p.map(collect_metadata, rfc_list)
    for res in results:
        if 'rfc' in res:
            metadata[res['rfc']] = res

    return metadata


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "metadata <rfc_directory>"
        sys.exit(-1)

    folder_name = sys.argv[1]

    metadata = create_metadata(folder_name)
    with open('metadata.json', 'w+') as fd:
        json.dump(metadata, fd)
