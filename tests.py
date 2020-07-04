import os
import unittest
# import setEnvVar
from bot.bot import DiscordBot


class IsBotOnline(unittest.TestCase):
    def test_run(self):
        pass


if __name__ == '__main__':

    bot = DiscordBot()
    bot.run()
    unittest.main()
