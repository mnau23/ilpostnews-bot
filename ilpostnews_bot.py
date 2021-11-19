import os
import itertools
import requests
from bs4 import BeautifulSoup
import telebot


API_KEY = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(API_KEY)
url = 'https://www.ilpost.it/'
emb_url = f'<a href="{url}">ilpost.it</a>'


# Init variables for BeautifulSoup
def init():
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


# Check input from user
def check(text):
    if text.isnumeric():
        return True
    else:
        return False


# Create embedded url
def create_embedded(selection):
    a_dict = {}

    # Create dict as {title: href}
    for s in selection:
        a_dict[s['title']] = s['href']

    # Rewrite dict value as embedded link
    for key in a_dict:
        emb_link = '<a href="' + a_dict[key] + '">link</a>'
        a_dict[key] = emb_link

    return a_dict


# Retrieve articles from webpage
def get_articles():
    bs = init()
    articles = bs.select('article div.entry-content h2 a')
    return create_embedded(articles)


# Retrieve "bits" articles from webpage
def get_bits():
    bs = init()
    articles_b = bs.select('div#thirdy div.widget.bits ul li a')
    return create_embedded(articles_b)


# Retrieve "flashes" articles from webpage
def get_flashes():
    bs = init()
    articles_f = bs.select('aside div.widget.flashes_hp ul li a')
    return create_embedded(articles_f)


# Complete response message
def make_response(res, a_dict):
    for key in a_dict:
        res += f'\u2022 {key}\n=> {a_dict[key]}\n'
    return res


# Give short description on the other commands
@bot.message_handler(commands=['help'])
def help_msg(message):
    response = f'Commands available:\n' \
               f'- /bits to receive bit news from {emb_url}\n' \
               f'- /flashes to receive flash news from {emb_url}\n' \
               f'- /latest to receive latest news from {emb_url}\n' \
               f'- /support to check dev info page'

    bot.send_message(message.chat.id, response, disable_web_page_preview=True, parse_mode='HTML')


# Get bits news
@bot.message_handler(commands=['bits'])
def bits(message):
    emoji = '--- --- ---'
    txt = f' <b>Bits</b> from {emb_url} '
    msg = emoji + txt + emoji + '\n'

    bits_news = get_bits()
    response = make_response(msg, bits_news)

    bot.send_message(message.chat.id, response, disable_web_page_preview=True, parse_mode='HTML')


# Get flash news
@bot.message_handler(commands=['flashes'])
def flashes(message):
    emoji = '\U0001f4a5\U0001f4a5\U0001f4a5'
    txt = f' <b>Flashes</b> from {emb_url} '
    msg = emoji + txt + emoji + '\n'

    flash_news = get_flashes()
    response = make_response(msg, flash_news)

    bot.send_message(message.chat.id, response, disable_web_page_preview=True, parse_mode='HTML')


# Get latest news
@bot.message_handler(commands=['latest'])
# Ask for a number of articles
def question(message):
    quest = bot.send_message(message.chat.id, 'How many articles do you want to view?')
    bot.register_next_step_handler(quest, latest)


# Send articles
def latest(message):
    if not check(message.text):
        bot.send_message(message.chat.id, 'Not a number! Please send me a valid integer number.')
    else:
        emoji = '\u26a0\ufe0f\u26a0\ufe0f\u26a0\ufe0f'
        line = f' <b>Latest News</b> from {emb_url} '
        msg = emoji + line + emoji + '\n'

        news = get_articles()

        if int(message.text) > len(news):
            bot.send_message(message.chat.id, f'There are a maximum of {len(news)} articles available on the website.')
        else:
            selected = dict(itertools.islice(news.items(), int(message.text)))
            response = make_response(msg, selected)
            bot.send_message(message.chat.id, response, disable_web_page_preview=True, parse_mode='HTML')


# Get extra info
@bot.message_handler(commands=['support'])
def support(message):
    links = ['https://github.com/mnau23', 'https://www.buymeacoffee.com/emanuele']
    gh = f'<a href="{links[0]}">GitHub</a>'
    bmac = f'<a href="{links[1]}">offer</a>'

    response = 'Hey! \U0001f604\nThanks for reaching here and using this very simple bot \U0001f916\n' \
               'Any suggestions or improvements for this project? Check my ' + gh +\
               ' page \U0001f468\U0001f3fb\u200d\U0001f4bb and let&#39s get in touch there.\n' \
               'If you like my work, you could also ' + bmac + ' me a coffee \u2615\n' \
               '\nEnjoy!!! \U0001f44b'

    bot.send_message(message.chat.id, response, disable_web_page_preview=True, parse_mode='HTML')


# Keep checking for messages
bot.polling()
