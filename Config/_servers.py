import discord
from Config._db import Database
from Config._const import BRAIN

db = Database()

columns = db.get_entries("serverdata")

SERVERS = {}

MAIN_SERVER = {}
MAIN_SERVER["ID"] = 653673010821201920 # 481509601590771724
MAIN_SERVER["MAIN"] = discord.utils.get(BRAIN.guilds, id=653673010821201920)
MAIN_SERVER["LOGS"] = discord.utils.get(MAIN_SERVER["MAIN"].channels, id=653673395954647095) # 653677748832698378
MAIN_SERVER["BIRTHDAY"] = discord.utils.get(MAIN_SERVER["MAIN"].channels, id=653771648616366103) # 653630098813222943
MAIN_SERVER["MEMES"] = discord.utils.get(MAIN_SERVER["MAIN"].channels, id=656641155869704205) # 656639194415759371
MAIN_SERVER["INTERESTED"] = discord.utils.get(MAIN_SERVER["MAIN"].roles, id=654094896562438154) # something

for server in columns:
	server_inst = discord.utils.get(BRAIN.guilds, id=int(server[0]))

	if server_inst is None:
		continue
	
	SERVERS[server[0]] = {}

	SERVERS[server[0]]["MAIN"] = server_inst
	SERVERS[server[0]]["STAFF_ROLE"] = discord.utils.get(server_inst.roles, id=int(server[1]))
	SERVERS[server[0]]["MEMBER_ROLE"] = discord.utils.get(server_inst.roles, id=int(server[2]))
	SERVERS[server[0]]["PUBLIC_CHANNELS"] = [discord.utils.get(server_inst.channels, id=int(x)) for x in server[3].split(" ")]
	SERVERS[server[0]]["BOT_CHANNELS"] = [discord.utils.get(server_inst.channels, id=int(x)) for x in server[4].split(" ")]
	SERVERS[server[0]]["GAME_CHANNEL"] = discord.utils.get(server_inst.channels, id=int(server[5]))
	SERVERS[server[0]]["BOT_ROLE"] = discord.utils.get(server_inst.roles, id=int(server[6]))
	SERVERS[server[0]]["PREFIX"] = server[7]

	SERVERS[server[0]]["EVENTS"] = {}