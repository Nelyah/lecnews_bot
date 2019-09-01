from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from os import path
from time import sleep

import datetime
import configparser
import time
import requests
import re
import logging


# Global variable so the functions can access a single browser instance.
# There's probably a nicer way to do this with webdriver.Remote
browser_driver = None


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def extract_td_team_info(d_teams, list_td_tags):
    """Update d_teams dictionary with info from list_td_tags.

    """
    pass


def startup_browser():
    """Starts a browser using Selenium and returns a browser.
    TODO: connects to an existing browser if available
    :returns: browser browser

    """
    logging.log(logging.INFO, 'Starting headless browser...')


    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--private-window')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')

    # browser = webdriver.Firefox(options=firefox_options)
    browser = webdriver.Chrome(port=9515, options=chrome_options)
    browser.implicitly_wait(30)
    logging.log(logging.INFO, 'Done.')

    return browser


def get_regular_season_standings(browser_driver):
    url = 'https://eu.lolesports.com/en/league/lec'
    url = 'https://watch.lolesports.com/vods/lec/lec_2019_summer'
    url = 'https://watch.lolesports.com/standings'
    url = 'https://watch.lolesports.com/standings/lec/lec_2019_summer/regular_season'

    logging.log(logging.INFO, f'Getting url: {url}')
    browser_driver.get(url)

    # Poll the website because selenium can't wait implicitly
    while True:
        page_source = browser_driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        t_team_data = soup.findAll(class_='ranking')

        if len(t_team_data) > 0:
            break
        sleep(1)

    t_team_dict = []
    for team_data in t_team_data:
        d_team = {}

        soup = BeautifulSoup(str(team_data), 'lxml')
        d_team['name'] = soup.find(class_='name').text
        d_team['rank'] = soup.find(class_='ordinal').text
        record  = soup.find(class_='record').text
        record = re.findall(r'([0-9]+)W-([0-9]+)L', record)[0]
        win, loss = record[0], record[1]

        d_team['win'] = win
        d_team['loss'] = loss

        t_team_dict.append(d_team)

    return t_team_dict


def get_schedule(browser_driver):
    """Get schedule from LEC league.

    :returns: list of dictionary (one per match)

    """
    url = 'https://watch.lolesports.com/schedule?leagues=lec'

    logging.log(logging.INFO, f'Getting url: {url}')
    browser_driver.get(url)

    # Poll the website because selenium can't wait implicitly
    while True:
        page_source = browser_driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        schedule_data = soup.findAll(class_='EventDate')

        if len(schedule_data) > 0:
            break
        sleep(1)
    logging.log(logging.INFO, f'Page loaded! Scraping results.')

    # Getting interesting parts into a list
    soup = BeautifulSoup(page_source, 'lxml')
    t_data = soup.findAll('div', {'class': ['EventDate', 'EventMatch']})

    t_event = []
    weekday = None
    monthday = None

    # Iterate over list and fill up a dictionary each time
    for div in t_data:
        if 'EventDate' in div.attrs['class']:
            weekday = div.find(class_='weekday').text
            monthday = div.find(class_='monthday').text
        elif 'EventMatch' in div.attrs['class']:
            d_event = {}
            if div.find(class_='live') is not None:
                d_event['live'] = True
            else:
                d_event['live'] = False
                d_event['weekday'] = weekday
                d_event['monthday'] = monthday
                d_event['hour'] = div.find(class_='hour').text
                d_event['ampm'] = div.find(class_='ampm').text

                minute = div.find(class_='minute')

                if minute is not None:
                    minute = minute.text
                else:
                    minute = '00'
            d_event['minute'] = minute

            d_event['team1'] = div.find(
                class_='team1').find(class_='name').text
            score_team1 = div.find(class_='scoreTeam1')
            if score_team1 is not None:
                score_team1 = score_team1.text
            d_event['score_team1'] = score_team1

            d_event['team2'] = div.find(
                class_='team2').find(class_='name').text
            score_team2 = div.find(class_='scoreTeam2')
            if score_team2 is not None:
                score_team2 = score_team2.text
            d_event['score_team1'] = score_team2

            t_event.append(d_event)

    return t_event


def start(bot, context):
    bot.send_message(chat_id=context.message.chat_id, text="I'm a bot, please talk to me!")


def echo(bot, context):
    bot.send_message(chat_id=context.message.chat_id, text="I didn't quite get that, sorry.")


def audio(bot, context):
    bot.send_message(chat_id=context.message.chat_id, text="No use sending me audio...")


def bot_get_rankings(bot, context):
    """Scrape website for ranking data and print a nicely formatted output.

    """
    # Connect to existing browser
    t_team_data = get_regular_season_standings(browser_driver)

    msg = ''
    for team_data in t_team_data:
        msg += f"{team_data['rank']} - {team_data['name']}: {team_data['win']}W-{team_data['loss']}L\n"

    bot.send_message(chat_id=context.message.chat_id, text=msg)


def bot_get_schedule(bot, context):
    """TODO: Docstring for bot_get_schedule.

    :bot: TODO
    :context: TODO
    :returns: TODO

    """
    t_schedule_data = get_schedule(browser_driver)

    date_today = datetime.datetime.today()
    date_twoweeks_ahead = date_today + datetime.timedelta(14)
    date_today.year

    msg             = ''
    last_date_event = None
    msg_date        = None
    for event_data in t_schedule_data:
        if event_data['live'] is False:
            human_event_date = f"{event_data['monthday']} {date_today.year}"

            date_event = datetime.datetime.strptime(
                human_event_date,
                '%B %d %Y'
            )

            if last_date_event is None or last_date_event != date_event:
                if msg_date is not None: 
                    msg_date = '\n\n'
                else:
                    msg_date = ''
                msg_date = f"{msg_date}{human_event_date}:\n"
                last_date_event = date_event
            else:
                msg_date = ''
            if date_event > date_today and date_event < date_twoweeks_ahead:
                msg += f"{msg_date}{event_data['hour']}:{event_data['minute']}{event_data['ampm']}: {event_data['team1']} - {event_data['team2']}\n"

            # msg += f"{team_data['rank']} - {team_data['name']}: {team_data['win']}W-{team_data['loss']}L\n"

    bot.send_message(chat_id=context.message.chat_id, text=msg)


def startup_bot():
    """Startup function for the Telegram Bot
    :returns: Updater object

    """

    config = configparser.ConfigParser()
    config.read(path.join(path.dirname(path.abspath(__file__)), 'config.py'))
    api_key = config.get('API', 'key')

    updater = Updater(api_key)
    return updater


def main():
    updater = startup_bot()

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('standings', bot_get_rankings))
    dp.add_handler(CommandHandler('schedule', bot_get_schedule))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, echo))

    updater.start_polling()
    logging.log(logging.INFO, 'Listening for input...')

    updater.idle()

    browser_driver.quit()
    

if __name__ == '__main__':
    browser_driver = startup_browser()
    # get_schedule()
    main()
