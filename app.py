from flask import Flask, render_template
import pandas as pd
import requests
import dateparser
from bs4 import BeautifulSoup
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)


def scrape(url):
    # This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content, "html.parser")

    # Find the key to get the information
    table = soup.find('table')
    tr = table.find_all('tr')

    temp = []  # initiating a tuple

    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
        # use the key to take information here
        # name_of_object = row.find_all(...)[0].text
        date = row.find_all('td')[0].text
        ask = row.find_all('td')[1].text
        bid = row.find_all('td')[2].text

        temp.append((date, ask, bid))  # append the needed information

    temp = temp[::-1]  # remove the header

    df = pd.DataFrame(temp, columns=('Tanggal', 'Kurs jual', 'Kurs beli'))

    # Parse Indonesian month using dateparser
    df['Tanggal'] = df['Tanggal'].apply(lambda date : dateparser.parse(date))

    # Replace ',' in numeric string to '.'
    df['Kurs jual'].replace(',','.',regex=True, inplace=True)
    df['Kurs beli'].replace(',','.',regex=True, inplace=True)

    # Change data types
    df = df.astype({'Tanggal' : 'datetime64[D]', 'Kurs jual' : 'float', 'Kurs beli' : 'float'})

    # Set date as index before plotting
    df = df.set_index('Tanggal')
   # end of data wranggling

    return df


@app.route("/")
def index():
    url = 'https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019'
    df = scrape(url)  # insert url here

    # This part for rendering matplotlib
    fig = plt.figure(figsize=(5, 2), dpi=300)
    axes = df.plot(title='Kurs Jual & Beli IDR/JPY Tahun 2019')
    axes.set_xlabel('Bulan')
    axes.set_ylabel('IDR / JPY')

    # Do not change this part
    plt.savefig('kursIDRJPY2019', bbox_inches="tight")
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    # This part for rendering matplotlib

    # this is for rendering the table
    df = df.to_html(
        classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__":
    app.run()
