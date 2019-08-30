from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from os import path
from time import sleep

import configparser
import time
import requests
import re
import logging


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

    return browser


def get_regular_season_standings(browser_driver):
    url = 'https://eu.lolesports.com/en/league/lec'
    url = 'https://watch.lolesports.com/vods/lec/lec_2019_summer'
    url = 'https://watch.lolesports.com/standings'
    url = 'https://watch.lolesports.com/standings/lec/lec_2019_summer/regular_season'

    browser_driver = startup_browser()

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
            


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url

def bop(bot, context):
    url = get_url()
    chat_id = context.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


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
    browser_driver = startup_browser()
    t_team_data = get_regular_season_standings(browser_driver)

    msg = ''
    for team_data in t_team_data:
        msg += f"{team_data['rank']} - {team_data['name']}: {team_data['win']}W-{team_data['loss']}L\n"

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
    browser_driver = startup_browser()

    updater = startup_bot()

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop',bop))
    dp.add_handler(CommandHandler('standings', bot_get_rankings))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, echo))

    updater.start_polling()
    logging.log(logging.INFO, 'Listening for input...')

    updater.idle()

    browser_driver.quit()
    

if __name__ == '__main__':
    main()
