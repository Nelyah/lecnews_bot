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
    # chrome_options.add_argument('--private-window')

    # driver = webdriver.Firefox(options=firefox_options)
    driver = webdriver.Chrome()
    driver.man .manage().timeouts().implicitlyWait()
    return driver


def get_web_data():
    url = 'https://eu.lolesports.com/en/league/lec'
    url = 'https://watch.lolesports.com/vods/lec/lec_2019_summer'
    url = 'https://watch.lolesports.com/standings'
    url = 'https://watch.lolesports.com/standings/lec/lec_2019_summer/regular_season'

    driver = startup_browser()

    logging.log(logging.INFO, f'Getting url: {url}')
    driver.get(url)
    # sleep(5)

    # standings_button = driver.find_element_by_id('standingsTab')
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'lxml')
    print(soup)
    team_span_values = soup.findAll(class_='ranking')
    print(team_span_values)

    # team_regex = r'>([^<]*)</span'
    # team_names = [re.findall(team_regex, str(span_value))[0] for span_value in team_span_values]

    # team_names = [name for name in team_names if team_names.index(name) % 2 == 0]
            
    # print(team_names)
    # list_td_tags = soup.findAll('td')

    # d_teams = {}

    # # There are 4 <td> tags per team
    # i = 0
    # td_regex = r'<td>([^<]*)</td>'
    # for td in list_td_tags:
    #     if i == 0:
    #         rank = td.text
    #         i += 1
    #     elif i == 1:
    #         names = BeautifulSoup(str(td), 'lxml').findAll('span', class_='standings__team-name')
    #         long_name = names[0].text
    #         short_name = names[1].text
    #         i += 1
    #     elif i == 2:
    #         win = td.text
    #         i += 1
    #     elif i == 3:
    #         loss = td.text
    #         i += 1

    #     if i%4 == 0:
    #         d_teams[short_name] = {}
    #         d_teams[short_name]['long_name'] = long_name
    #         d_teams[short_name]['short_name'] = short_name
    #         d_teams[short_name]['rank'] = rank
    #         d_teams[short_name]['win'] = win
    #         d_teams[short_name]['loss'] = loss

    #         i = 0
            
    # driver.quit()





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
