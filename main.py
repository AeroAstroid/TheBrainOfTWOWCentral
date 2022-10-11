import discord as dc
from discord import *

from Helper.__config import TOKEN, BRAIN, STARTUP
from Helper.__functions import m_line, is_slash_cmd

from discord.ext import commands as cmd

from time import time
import os
import traceback as tb
from datetime import datetime

@BRAIN.event
async def on_connect():
	print(m_line(f"""The Brain of TWOW Central connected to Discord at 
	{round(time() - STARTUP, 2)}s - {datetime.utcnow()}"""))

	await BRAIN.sync_commands()

@BRAIN.event
async def on_ready():
	print(m_line(f"""The Brain of TWOW Central logged in at 
	{round(time() - STARTUP, 2)}s - {datetime.utcnow()}"""), '\n')

	restart_rep_sv = None
	restart_rep_ch = None
	restart_rep_t = None

	for arg in sorted(sys.argv):
		if arg.startswith("1_report_guild:"):
			if arg[len("1_report_guild:"):] == "":
				continue
			
			restart_rep_sv = dc.utils.get(BRAIN.guilds,
				id=int(arg[len("1_report_guild:"):]))

		if arg.startswith("2_report_chnl:"):
			if restart_rep_sv is None:

				for guild in BRAIN.guilds:
					try:
						restart_rep_ch = guild.get_member(int(arg[len("2_report_chnl:"):]))

					except dc.errors.NotFound:
						continue
				
			else:
				restart_rep_ch = dc.utils.get(restart_rep_sv.channels,
					id=int(arg[len("2_report_chnl:"):]))

		if arg.startswith("3_report_time:"):
			restart_rep_t = int(arg[len("3_report_time:"):])/1000
		
	if restart_rep_t is not None:
		t_taken = round(time() - restart_rep_t, 2)
		await restart_rep_ch.send(
			f"✅ **Successfully restarted the Brain of TWOW Central** in {t_taken}s.\n")

	print("="*50, '\n')

	await BRAIN.change_presence(status=dc.Status.online,
	activity=dc.Activity(type=dc.ActivityType.watching, name="over TWOW Central"))

	for cog_name in BRAIN.cogs:
		cog_obj = BRAIN.get_cog(cog_name)

		# Check for a task/event that could have a setting to be turned on while connecting
		if not "ON_BY_DEFAULT" in dir(cog_obj) or not "set_loop" in dir(cog_obj):
			continue
		
		getattr(cog_obj, "ON_BY_DEFAULT")
		
		if getattr(cog_obj, "ON_BY_DEFAULT"):
			getattr(cog_obj, "set_loop")(True)
			print(f"Automatically starting all loops in {type(cog_obj).__name__.upper()}")
	
	print("\n" + "="*50, '\n')

@BRAIN.event
async def on_command_error(ctx, error): # For prefixed commands
	await error_handler(ctx, error)

@BRAIN.event
async def on_application_command_error(ctx, error): # For slash commands
	await error_handler(ctx, error)

async def error_handler(ctx, err):
	if type(err) == cmd.errors.CommandNotFound:
		await ctx.respond(f"⚠️ This command or alias does not exist!")
		return
	
	if type(err) in [dc.errors.CheckFailure, cmd.errors.CheckFailure]:
		await ctx.respond("⚠️ You do not have permission to run this command!")
		return
	
	if type(err) == cmd.errors.CommandOnCooldown:
		if is_slash_cmd(ctx):
			await ctx.respond("💬 **This command is on cooldown right now!**")
		else:
			await ctx.message.add_reaction("💬")
		return
	
	print("-[ERROR]- "*10)
	tb.print_exception(type(err), err, None)

	if type(err).__name__ == "CommandInvokeError":
		err = err.original

	try:
		await ctx.respond(
		f"⚠️ Uh oh! This command raised an unexpected error: **`{type(err).__name__}`**")
	except Exception as e:
		print(f"\nCouldn't inform user of error due to {type(e).__name__}!")
	
	print("-[ERROR]- "*10, '\n')

@BRAIN.event
async def on_command(ctx):
	print("Prefixed command from", ctx.message.author)
	print(datetime.utcnow(), "-", time())

	try:
		print(ctx.message.channel.name, f"({ctx.message.channel.id})")
		print(ctx.message.guild.name, f"({ctx.message.guild.id})")
	except AttributeError:
		print("Sent in DMs")
	
	print("-->", ctx.message.content, "\n")

@BRAIN.event
async def on_application_command(ctx):
	print("Slash command from", ctx.user)
	print(datetime.utcnow(), "-", time())

	try:
		print(ctx.channel.name, f"({ctx.channel.id})")
		print(ctx.guild.name, f"({ctx.guild.id})")
	except AttributeError:
		print("Sent in DMs")
	
	print("-->", ctx.command, "\n")
	
print("="*50, '\n')

commands_loaded = []

for cmd_name in os.listdir("Commands"):
	if not cmd_name.endswith('py') or cmd_name.startswith('__'):
		continue

	BRAIN.load_extension(f"Commands.{cmd_name[:-3]}")

	commands_loaded.append(cmd_name[:-3].upper())

print(f"Added the following commands: {', '.join(commands_loaded)}", '\n')

print("="*50, '\n')

tasks_loaded = []

for task_name in os.listdir("Tasks"):
	if not task_name.endswith('py') or task_name.startswith('__'):
		continue

	BRAIN.load_extension(f"Tasks.{task_name[:-3]}")

	tasks_loaded.append(task_name[:-3].upper())

print(f"Loaded in the following tasks: {', '.join(tasks_loaded)}", '\n')

print("="*50, '\n')

BRAIN.run(TOKEN)