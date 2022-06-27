import os
import discord
from Config._functions import smart_lookup

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Easy mass-pfp-gathering command for staff use",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""W.I.P.
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 2 # Staff
ALIASES = ["GETPFP", "PFPS", "PFP"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
    if level == 1:
        await message.channel.send("Include the method to get PFPs by!")
        return
    
    m = args[1].lower()

    if m == "user":
        user = " ".join(args[2:])
        s_members = SERVER["MAIN"].members
        usernames = [m.name for m in s_members]

        result = smart_lookup(user, usernames)

        if not result:
            await message.channel.send("Could not narrow that name down to one user!")
            return
        
        ind, name = result

        await message.channel.send(f"URL for **{name}**'s PFP:\n{s_members[ind].avatar_url_as(format='png')}")
    
    if m == "role":
        role = " ".join(args[2:])
        s_roles = SERVER["MAIN"].roles
        role_names = [r.name for r in s_roles]

        result = smart_lookup(role, role_names)

        if not result:
            await message.channel.send("Could not narrow that name down to one role!")
            return
        
        ind, role_name = result

        csv_result = ""
        
        for m in s_roles[ind].members:
            csv_result += f"{m.display_avatar.url},{m.id},{m.name}\n"

        with open("getpfps.csv", "w", encoding="utf-8") as f:
            f.write('\ufeff')
            f.write(csv_result)

        await message.channel.send(f"File containing PFPs of members with the {role_name} role:",
        file=discord.File("getpfps.csv"))
        
        os.remove("getpfps.csv")
