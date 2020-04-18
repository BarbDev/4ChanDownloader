import os
import sys
import re
import logging
from requests import get
from contextlib import closing
from bs4 import BeautifulSoup
from slugify import slugify


def download(url, file_name) -> None:
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        with closing(get(url)) as response:
            # write to file
            file.write(response.content)


def sanitise_url(url: str) -> str:
    """
    Make sure the URL correspond to 4chan and makes it HTTPS
    :param url: a string corresponding to a 4chan URL
    :return: a string URL with HTTPS
    """
    # https://boards.4chan.org/s/thread/17829010#p17837211
    c = re.compile(r'^(https?)://boards.4chan(nel)?.org/[a-z0-9]+/thread/.*$')
    m = c.match(url)
    if m is not None:
        if m.group(1) == 'http':
            url = 'https'+url[4:]
        return url
    else:
        sys.exit(3)


def get_urls(file_path):
    """
    Return a generator of URLs from a file
    """
    with open(file_path) as file:
        return (sanitise_url(url) for url in file.readlines())


def thread_archived(chan_thread) -> bool:
    return chan_thread.find("div", class_="closed") is not None


def extract_medias(chan_thread) -> list:
    """
    Return a list of dict of all the media
    """
    files = chan_thread.find_all("div", class_="fileText")
    return [
        {
            'url': "https:" + file.a['href'],
            'filename': file.a.get('title', file.a.string),
            # TODO put the size and format (get index 2 of I don't remember what, parent?)
        } for file in files
    ]


def get_title(chan_thread) -> str:
    return slugify(chan_thread.title.string)


LOGGER = logging.getLogger("4ChanDownloader")
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    urls_filename = "url_list.txt"
    new_urls = []

    for url in get_urls(urls_filename):
        with closing(get(url)) as response:
            if response.status_code == 404:
                LOGGER.error("Thread url %s is not valid anymore (404 status code), url discarded." % url.strip())
                continue
            chan_thread = BeautifulSoup(response.text, 'html.parser')
            thread_title = get_title(chan_thread)

            if thread_archived(chan_thread):
                LOGGER.info("Thread %s is archived, downloading..." % thread_title)

                # Creating the directories to store the images
                imgs_path = "imgs/" + thread_title
                if not os.path.isdir(imgs_path):
                    os.makedirs(imgs_path)

                # Downloading the images
                medias = extract_medias(chan_thread)
                total_images = len(medias)
                for index, media in enumerate(medias, start=1):
                    LOGGER.info("Downloading media %d of %d..." %(index, total_images))
                    download(media['url'], imgs_path + "/" + media['filename'])

                LOGGER.info("Thread %s downloaded." % thread_title)

            else:
                LOGGER.info("Thread %s is not archived, url kept." % thread_title)
                new_urls.append(url)

    # Update the file with the URLs not archived
    with open(urls_filename, "w") as file:
        file.writelines(new_urls)
