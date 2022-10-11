# This is a components file to contain useful objects to be used by scripts in general

# All commands are divided into different categories
# This categorization is purely cosmetic and makes no difference in functionality

# Categories are organized with a name and a display emoji for the help pages

CATEGORIES = {
	"BRAIN": "<:brainoftwowcentral:981613248384225290>",
	# BRAIN category: commands tied directly to the bot and its own functionality

	"SERVER": "📑",
	# SERVER category: commands that are server-specific, including staff action commands
}

# These are the main Discord-related imports common to scripts
# All command, task and event files import from this file, and thus get these too

import discord as dc
import discord.ext.commands as cmd
from discord.ext import tasks
from discord.ext import bridge
from discord.ui import View, Select, Button