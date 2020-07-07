import os
import threading
import asyncio
from flask import Flask
# import setEnvVar
from bot.bot import DiscordBot


def runBot():
    # bot = DiscordBot()
    # bot.run()
    return 'Hosting ELO BOT...'


application = Flask(__name__)

application.add_url_rule('/', 'index', (lambda:
                                        runBot()))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.

    bot = DiscordBot()

    # bot.run()

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(bot.run())

    # print('Start Discord bot')
    # t = threading.Thread(target=bot.run)
    # t.daemon = True
    # t.start()
    # print('Discord bot success')

    print('Start Flask')
    application.debug = False
    application.run()
