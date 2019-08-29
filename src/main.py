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
    """Starts a browser using Selenium and returns a driver.
    TODO: connects to an existing browser if available
    :returns: browser driver

    """
    logging.log(logging.INFO, 'Starting firefox headless browser...')


    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--private-window')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')

    # driver = webdriver.Firefox(options=firefox_options)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_web_data():
    url = 'https://eu.lolesports.com/en/league/lec'
    url = 'https://watch.lolesports.com/vods/lec/lec_2019_summer'
    url = 'https://watch.lolesports.com/standings'
    url = 'https://watch.lolesports.com/standings/lec/lec_2019_summer/regular_season'

    driver = startup_browser()
    driver.implicitly_wait(15)

    logging.log(logging.INFO, f'Getting url: {url}')
    driver.get(url)

    # Poll the website because selenium can't wait implicitly
    while True:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        t_team_data = soup.findAll(class_='ranking')
        print(t_team_data)

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

    print(t_team_dict)
            
    driver.quit()


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


def main():
    config = configparser.ConfigParser()
    config.read(path.join(path.dirname(path.abspath(__file__)), 'config.py'))
    api_key = config.get('API', 'key')

    updater = Updater(api_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop',bop))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, echo))


    updater.start_polling()
    updater.idle()
    

if __name__ == '__main__':
    # main()
    get_web_data()
