from datetime import date, datetime, timedelta
import csv
import inquirer
from bs4 import BeautifulSoup
import requests


charts = {'Hot 100': ["https://www.billboard.com/charts/hot-100/", 1958, 8, 4],
          'Pop Songs': ["https://www.billboard.com/charts/pop-songs/", 1992, 10, 3],
          'Rock Songs': ["https://www.billboard.com/charts/rock-songs/", 2009, 6, 20],
          'Hip-Hop/R&B Songs': ["https://www.billboard.com/charts/r-b-hip-hop-songs/", 1958, 10, 20],
          'Country Songs': ["https://www.billboard.com/charts/country-songs/", 1958, 10, 20]
          }


def scrape_site(writer, url, chart_date):
    new_url = url + chart_date.isoformat()
    req = requests.get(new_url)
    soup = BeautifulSoup(req.text, "html.parser")
    songs = soup.find_all(class_="chart-list-item")
    for index in range(len(songs)):
        artist = songs[index].get("data-artist").encode('ascii', 'ignore').decode('ascii')
        song = songs[index].get("data-title").encode('ascii', 'ignore').decode('ascii')
        rank = songs[index].get("data-rank")
        if songs[index].find(class_="chart-list-item__last-week") is None:
            last = '0'
        else:
            last = songs[index].find(class_="chart-list-item__last-week").contents[0]
        if songs[index].find(class_="chart-list-item__weeks-at-one") is None:
            peak = '0'
        else:
            peak = songs[index].find(class_="chart-list-item__weeks-at-one").contents[0]
        if songs[index].find(class_="chart-list-item__weeks-on-chart") is None:
            weeks = '0'
        else:
            weeks = songs[index].find(class_="chart-list-item__weeks-on-chart").contents[0]
        writer.writerow([artist, song, chart_date.isoformat(), rank, last, peak, weeks])


def date_increment(d):
    dt = datetime(d.year, d.month, d.day)
    week = timedelta(days=7)
    inc = dt + week
    return inc.date()


def last_day():
    today = datetime.today()
    day = today.weekday()
    if day == 6:
        return today.date()
    sub = timedelta(days=(day + 1))
    previous_sunday = today - sub
    last = timedelta(days=13)
    last_date = previous_sunday + last
    return last_date.date()


def inquire():
    questions = [
        inquirer.List('chart',
                      message="Which chart do you want data from?",
                      choices=['Hot 100', 'Pop Songs', 'Rock Songs', 'Hip-Hop/R&B Songs', 'Country Songs'],
                      carousel=True,
                      ),
    ]
    answers = inquirer.prompt(questions)
    return charts.get(answers['chart'])


if __name__ == '__main__':

    # Base url and dates for the Billboard Hot 100 chart, putting them into a
    # datetime object for easy addition and date manipulation

    billboard_url, base_year, base_month, base_day = inquire()

    curr_date = date(base_year, base_month, base_day)
    end_date = last_day()
    # Ask user for input to name the spreadsheet.
    sheetTitle = raw_input("Enter spreadsheet title: ").replace(" ", "_")
    sheetTitle = sheetTitle + ".csv"
    with open(sheetTitle, mode='w') as billboard_chart:
        charter = csv.writer(billboard_chart, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        charter.writerow(["Artist", "Song", "Date", "Current Rank", "Last Weeks Position", "Weeks on Chart", "Peak Position"])
        while curr_date != end_date:
            scrape_site(charter, billboard_url, curr_date)
            print("Finished charting the week of: " + curr_date.isoformat())
            curr_date = date_increment(curr_date)





