import os
import requests
import sys, getopt
import re
from requests import get
from FileIndexer import FourChanHtmlParser, FileIndex


def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)


def sanitise_url(url):
    # https://boards.4chan.org/s/thread/17829010#p17837211
    c = re.compile('^(https?)://boards.4chan.org/[a-z0-9]+/thread/.*$')
    m = c.match(url)
    if m is not None:
        if m.group(1) == 'http':
            url = 'https'+url[4:]
        return url
    else:
        sys.exit(3)


def main(argv):
    mypath = ''
    url = ''
    try:
        opts, args = getopt.getopt(argv, "hl:f:", ["link=", "folder="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        if opt == '-l' or opt == '-link':
            url = arg
        if opt == '-f' or opt == '-folder':
            mypath = arg
    if not os.path.isdir(mypath):
        os.makedirs(mypath)
    index = FileIndex()
    parser = FourChanHtmlParser(index)
    url = sanitise_url(url)
    r = requests.get(url)
    parser.feed(r.text)
    print()
    print(parser.getImageCount())
    index.resolve_duplicate()

    for cle, valeur in index.get_files().items():
        download("http://" + cle[2:], os.path.join(mypath, valeur))
        # print(cle, os.path.join(mypath, valeur))


main(sys.argv[1:])
