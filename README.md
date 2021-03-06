# elo-discord-bot

A discord bot written in python to calculate ELO rankings of users based on wins/losses.

Implementation: https://en.wikipedia.org/wiki/Elo_rating_system

## Running locally

Set Environment Variables:

```
$ export DISCORD_TOKEN=....
$ export MONGODB_SECRET=...
```

To Run:

```
$ pip install -r requirements.txt
$ python botApp.py
```

## Commands

Must be sent through channel labeled #smash and start with '--' indentifier.

```
PLAYER COMMANDS:

-- register me
Adds user to the DB with unique discord ID, start ELO of 1500, and 10 games of placement matches.

-- match PlayerA # - PlayerB #
Queues match to be confirmed by opponent. Users must be in said match.

-- confirm
Confirms queued match and removes match from queue.

-- cancel
Cancels queued match and removes match from queue.

-- my stats
Show players DB name, ELO, total games played, # wins, and # losses.

-- change name
Changes user name in DB if switched in discord.

-- stats vs PlayerB
Find user win loss stats against another player.

-- status
Show queue status and name of opponent to confirm.

-- ranking (optional parameter of -all, -#)
Show ELO rankings for default top 8 players, all, or specified.

-- help
List commands.

ADMIN COMMANDS:

-- delete Player
Deletes player data from all database collections.

-- toggle placements
Turns ON/OFF placement matches.

```
