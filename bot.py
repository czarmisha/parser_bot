import os
from xmlrpc.client import Boolean
from dotenv import load_dotenv
import logging
import requests
from bs4 import BeautifulSoup

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
token = os.environ['BOT_TOKEN']

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
    )

def get_tickers():
    url = 'https://finviz.com/'
    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,'referer':'https://www.google.com/'}
    resp = requests.get(url=url, headers=header)
    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = soup.find(id='signals_1').find_all('tr', class_='table-light-row-cp')
    tickers = []
    for row in rows:
        links = row.find_all('a')
        if links and len(links)==2 and links[1].getText()=='Top Gainers':
            tickers.append(links[0].getText())
    return tickers

def get_ticker_info(ticker):
    """
    •	достать значение показателей Market Cap, P/E, EPS (ttm), Avg Volume, ATR
    •	достать сектор, индустрию, биржу, к которым принадлежит акция.
    """
    ticker_info = {}
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,'referer':'https://www.google.com/'}
    resp = requests.get(url=url, headers=header)
    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = soup.find('div', {'class':'content', 'data-testid':'quote-data-content'}).find('div', class_='fv-container').find('table', class_='snapshot-table2').find_all('tr')
    for row in rows:
        title_cols = row.find_all('td', class_='snapshot-td2-cp')
        value_cols = row.find_all('td', class_='snapshot-td2')
        for col in title_cols:
            if col.getText()=='Market Cap':
                index = title_cols.index(col)
                ticker_info['Market Cap'] = value_cols[index].getText()
            elif col.getText()=='P/E':
                index = title_cols.index(col)
                ticker_info['P/E'] = value_cols[index].getText()
            elif col.getText()=='EPS (ttm)':
                index = title_cols.index(col)
                ticker_info['EPS (ttm)'] = value_cols[index].getText()
            elif col.getText()=='Avg Volume':
                index = title_cols.index(col)
                ticker_info['Avg Volume'] = value_cols[index].getText()
            elif col.getText()=='ATR':
                index = title_cols.index(col)
                ticker_info['ATR'] = value_cols[index].getText()
    
    ticker_info['exchange'] = soup.find(id='ticker').find_next('span').getText()[1:-1]
    info = soup.find(id='ticker').find_parent('td').find_parent('tr').find_next('tr').find_next('tr').find_all('a')
    ticker_info['sector'] = info[0].getText()
    ticker_info['industry'] = info[1].getText()

    return ticker_info


def parse(update: Update, context: CallbackContext) -> None:
    """/parse"""
    update.message.reply_text('Ждите, идет загрузка')
    tickers = get_tickers()
    tickers_info = {}
    for ticker in tickers:
        info = get_ticker_info(ticker)
        tickers_info[ticker] = info
    print(tickers_info)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("parse", parse))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()