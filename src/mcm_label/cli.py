from bs4 import BeautifulSoup

def main():
    parts = []
    soup = BeautifulSoup(open("/home/aaron/Downloads/my_labels/McMaster-Carr.html"), "html.parser")
    divs = soup.find_all("div", {"class": "dtl-row-info"})
    for row in divs:
        copy = row.find("div", {"class": "dtl-row-copy"})
        long_name = copy.find("p", class_=None).text.strip()
        pn = copy.find("p", {"class": "dtl-row-specs"}).text.strip()
        parts.append({"pn": pn, "name": long_name})

    for part in parts:
        print(part)

