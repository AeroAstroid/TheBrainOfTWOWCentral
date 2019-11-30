# This script gathers all the code required to run events and/or actions spanning more than one message

import importlib, os, traceback

EVENTS = {}

file_list = [x[:-3] for x in os.listdir("Events") if x.endswith(".py") and not x.startswith("_")]

for event_file in file_list:
	try:
		info = importlib.import_module("Events." + event_file)
		
		EVENTS[event_file.upper()] = info.EVENT() # The object with all the code to be used for the specific event
	
	except Exception as e: # Report events that failed to load, and the error received
		print(f"[ERROR] Event {event_file.upper()} failed to load ({e})")
		traceback.print_exc()

print(f"\nEvents loaded up! Current events:\n\t{', '.join(EVENTS.keys())}\n")