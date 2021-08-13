from bs4 import BeautifulSoup as bs
import requests
import json
import csv

class Link:
    def __init__(self, url):
        self.url = url

    def Scraper(self, url):
        HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
        webpage  = requests.get(url, headers=HEADERS)
        soup = bs(webpage.content, 'lxml')
        return soup

    def GetPageLinks(self, soup):
        linkList = []
        table = soup.select_one("#outer-container > div.table-responsive.col-md-12")
        links = table.find_all("div", {"class": "disable-ios-link div"})
        for l in links:
            linkList.append(l.text)
        return linkList
    
    def GetLinks(self):
        soup = self.Scraper(self.url)
        linkList = []
        pages = soup.select_one("#outer-container > div:nth-child(10) > div.col-sm-9.small > div.col-sm-12 > b:nth-child(4)").text
        pages = int(pages)
        linkList.extend(self.GetPageLinks(soup))
        for i in range(1, pages):
            soup = self.Scraper(self.url.replace('page=0', f'page={i}'))
            linkList.extend(self.GetPageLinks(soup))
        return linkList

    def GetPageData(self, soup, csv_columns):
        data = {}
        table = soup.find_all("table", {"class": "table table-bordered small"})[0]
        trList = table.find_all("tr")
        for tr in trList:
            if tr.th.text.strip() in csv_columns or tr.th.text.strip() == 'Mailing Address':
                if tr.th.text.strip() != 'School Address':
                    v = tr.td.text
                    if tr.th.text.strip() == 'Administrator':
                        v = v.strip().replace('Principal', '')
                        value = v.strip()
                        value = value.replace('  ', '')
                        value = value.replace('\r', '')
                        value = value.split('\n')
                        tempv = ''
                        for p in value:
                            if p != '':
                                if p[-1] == ' ':
                                    p = p[:-1]
                                if p == value[-1]:
                                    tempv += f'{p}'
                                else:
                                    tempv += f'{p}, '
                        value = tempv
                    elif tr.th.text.strip() == 'Mailing Address':
                        value = v.strip()
                        value = value.replace('  ', '')
                        value = value.replace('\r', '')
                        value = value.split('\n')
                        tempv = ''
                        for p in value:
                            tempv += p
                        value = tempv
                    else:
                        value = v.strip().replace('\n', '')
                    
                    if tr.th.text.strip() == 'Mailing Address':
                        data['School Address'] = value
                    else:
                        data[tr.th.text.strip()] = value
        return data

    def GetData(self, links, baseUrl, csv_columns):
        data = []
        for i in links:
            print(f'{links.index(i) + 1}/{len(links)}')
            url = baseUrl + i
            data.append(self.GetPageData(self.Scraper(url), csv_columns))
        return data

def toCsv(data, csv_columns):
    csv_file = 'School Data.csv'
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for d in data:
                writer.writerow(d)
    except IOError:
        print("I/O error")

csv_columns = ['School', 'County', 'District', 'School Address', 'Phone Number', 'Administrator', 'School Type', 'Low Grade', 'High Grade', 'Public School', 'Charter', 'Magnet', 'Year Round']

url = 'https://www.cde.ca.gov/SchoolDirectory/Results?title=California%20School%20Directory&search=1&status=1&types=61%2C60%2C66%2C67%2C62%2C64&nps=0&multilingual=0&charter=2&magnet=0&yearround=0&qdc=0&qsc=0&tab=1&order=0&page=0&items=500&hidecriteria=False&isstaticreport=False'
main = Link(url)
# Writing links to file
"""links = main.GetLinks()
with open('links.json', 'w') as outfile:
    #json.dump(links, outfile)"""

# Reading links from file
with open('links.json', 'r') as outfile:
    links = json.load(outfile)

data = main.GetData(links, "https://www.cde.ca.gov/SchoolDirectory/details?cdscode=", csv_columns)
toCsv(data, csv_columns)