import requests
from requests import get
from html.parser import HTMLParser
from html.entities import name2codepoint

r = requests.get('http://boards.4chan.org/w/thread/2043543')

# print(r.headers['content-type'])
# print(r.encoding)
# après <div> de class fileText puis Data = file, premier <a> contient le liens vers image et champ data = nom fichier
print(r.text)


def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)


class MyHTMLParser(HTMLParser):
    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)
        for attr in attrs:
            print("     attr:", attr)

    def handle_endtag(self, tag):
        print("End tag  :", tag)

    def handle_data(self, data):
        print("Data     :", data)

    def handle_comment(self, data):
        print("Comment  :", data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        print("Named ent:", c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        print("Num ent  :", c)

    def handle_decl(self, data):
        print("Decl     :", data)


class FourChanHtmlParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=True)
        self._step = 0
        self.imgCount = 0
        self.currentURL = ""
        self.currentNAME = ""

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and self._step == 0:
            print("Start tag:", tag)
            for attr in attrs:
                if attr[1] == 'fileText':
                    print("     attr:", attr)
                    self._step = 1
        elif self._step == 1:
            if tag == 'a':
                for attr in attrs:
                    if attr[0] == 'href':
                        print("     attr:", attr)
                        self.currentURL = attr[1]
                        if self._step != 5:
                            self._step = 2
                    if attr[0] == 'title':
                        # bypass the data part, title contains full name
                        self._step = 5
                        self.currentNAME = attr[1]
                        print('lul', attr)
                        break

    def handle_data(self, data):
        if self._step == 2:
            print("Data     :", data)
            self.currentNAME = data
            print("URL:", self.currentURL[2:])
            download("http://"+self.currentURL[2:], self.currentNAME)
            self.imgCount = self.imgCount + 1
            self._step = 0
        if self._step == 5:
            # Data bypasse, URL OK and NAME OK
            print("URL:", self.currentURL[2:])
            download("http://"+self.currentURL[2:], self.currentNAME)
            self.imgCount = self.imgCount + 1
            self._step = 0


parser = FourChanHtmlParser()
parser.feed(r.text)
print(parser.imgCount)
