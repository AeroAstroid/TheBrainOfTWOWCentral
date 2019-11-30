# This script gathers all the commands into the lookup dict for the main script

import importlib, os, traceback

COMMANDS = {}

# Detect all the command files in the folder
file_list = [x[:-3] for x in os.listdir("Commands") if x.endswith(".py") and not x.startswith("_")]

for command_file in file_list:
	try:
		info = importlib.import_module("Commands." + command_file)
		
		COMMANDS[command_file.upper()] = { # These variable names are standardized on each script file
			"MAIN": info.MAIN, # The function to call to run the command
			"HELP": info.HELP, # The tc/help description of the command
			"PERMS": info.PERMS, # The permission required to run the command
			"ALIASES": info.ALIASES, # The aliases you can use to run the command instead
			"REQ": info.REQ # The required parameters for this command, supplied through the PARAMS dict
		}

	except Exception as e: # Report commands that failed to load, and the error received
		print(f"[ERROR] Command {command_file.upper()} failed to load ({e})")
		traceback.print_exc()

# Report all the commands that successfully loaded
print(f"\nCommands loaded up! Current commands:\n\t{', '.join(COMMANDS.keys())}\n")