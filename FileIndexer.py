from html.parser import HTMLParser


class FileIndex:
    def __init__(self):
        self._files = dict()

    def add(self, name, url):
        self._files[url] = name

    def resolve_duplicate(self):
        seen = set()
        uniq = []
        i = 0
        for cle, valeur in self._files.items():
            if valeur not in seen:
                uniq.append(valeur)
                seen.add(valeur)
            else:
                self._files[cle] = str(i) + valeur
                i = i + 1

    def get_files(self):
        return self._files


# <div class=file #1
#   <div class=fileText #2
#       <a href=imgLink 'if title'=trueName> data=trueName #3
#   <a class=fileThumb #4
#       <img src=tinyImgLink alt=imgWeight #5
class FourChanHtmlParser(HTMLParser):
    def __init__(self, indexer):
        super().__init__(convert_charrefs=True)
        self._step = 0
        self._imgCount = 0
        self._currentURL = ""
        self._currentNAME = ""
        self._indexer = indexer

    def getImageCount(self):
        return self._imgCount

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and self._step == 0:
            for attr in attrs:
                if attr[1] == 'fileText':
                    self._step = 1
        elif self._step == 1:
            if tag == 'a':
                for attr in attrs:
                    if attr[0] == 'href':
                        self._currentURL = attr[1]
                        if self._step != 5:
                            self._step = 2
                    if attr[0] == 'title':
                        # bypass the data part, title contains full name
                        self._step = 5
                        self._currentNAME = attr[1]

    def handle_data(self, data):
        if self._step == 2:
            self._currentNAME = data
            self._indexer.add(self._currentNAME, "https://"+self._currentURL[2:])
            self._imgCount = self._imgCount + 1
            self._step = 0
        if self._step == 5:
            # Data bypasse, URL OK and NAME OK
            self._indexer.add(self._currentNAME, "https://" + self._currentURL[2:])
            self._imgCount = self._imgCount + 1
            self._step = 0
