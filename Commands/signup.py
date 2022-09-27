import discord as dc
from Config._db import Database

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Use this command to automatically sign up to the current event",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}signups` in a designated event signups channel will add you as a participant 
        of the current running event.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 1 # Member
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
    signup_channel_id = 633045040716840970
    participating_role_id = 498254150044352514

    signup_channel = SERVER["MAIN"].get_channel(signup_channel_id)
    participating = SERVER["MAIN"].get_role(participating_role_id)

    print(signup_channel)
    print(participating)

    if message.channel == signup_channel:
        await SERVER["MAIN"].get_member(message.author.id).add_roles(participating)
        await message.add_reaction("✅")
        
        # Check database for whether to add another role
        db = Database()

        role = db.get_entries("signupeventrole")[0][0]

        if role == "None":
            return
        
        role_obj = dc.utils.get(SERVER["MAIN"].roles, name=role)

        if role_obj is None:
            return
        
        await SERVER["MAIN"].get_member(message.author.id).add_roles(role_obj)
        return
    
    if level == 1 or perms < 2:
        return
    
    if args[1].lower() == "set":
        db = Database()

        if level == 2:
            new_role = "None"
        else:
            new_role = " ".join(args[2:])

        db.edit_entry("signupeventrole", {"role": new_role})

        await message.channel.send(f"Set the event-specific signup role to {new_role}!")
        return