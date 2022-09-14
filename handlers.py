from telegram import Update
from telegram.ext import CallbackContext

from .bot import logger
from .utils import get_tickers, get_ticker_info, get_trade_info, create_file


def parse(update: Update, context: CallbackContext) -> None:
    """/parse"""
    logger.info('PARSING')
    update.message.reply_text('Теперь надо подождать')
    tickers = get_tickers()
    tickers_info = {}
    for ticker in tickers:
        info = get_ticker_info(ticker)
        trade_info = get_trade_info(ticker)
        tickers_info[ticker] = {**info, **trade_info}
    file_name = create_file(tickers_info)
    try:
        with open(f"output/{file_name}", "rb") as file:
            # f = file.read()
            context.bot.send_document(update.effective_chat.id, file)
    except Exception:
        update.message.reply_text('Произошла ошибка')
    logger.info('DONE')

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! press /parse',
    )