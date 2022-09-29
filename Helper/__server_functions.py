from Helper.__db import Database as DB
from Helper.__functions import command_user, is_dm
from Helper.__config import BRAIN

import discord as dc

# Store the current state of the server table for ease of lookup
SERVER_INFO = DB.get_entries("servers")

def update_server_info():
	'''
	Updates the current state of the SERVER_INFO variable
	'''

	global SERVER_INFO

	SERVER_INFO = DB.get_entries("servers")

def member_servers(ctx):
	'''
	Returns a list of all Brain-operational servers the command user is a member of

	Useful for narrowing down where a user's server command can apply
	'''

	# server_id and member_role_id
	servers = [[s[0], s[2]] for s in SERVER_INFO]
	member_of = []

	for server_id, members_id in servers:
		server_obj = dc.utils.get(BRAIN.guilds, id=int(server_id))
		role_obj = dc.utils.get(server_obj.roles, id=int(members_id))

		if command_user(ctx) in role_obj.members:
			member_of.append(server_obj)
			break
	
	return member_of

def staff_servers(ctx):
	'''
	Returns a list of all Brain-operational servers the command user is staff in

	Useful for narrowing down where a user's staff command can apply (or if they can even use a 
	staff command anywhere at all)
	'''

	# The two first columns: server_id and staff_roles_id
	servers = [s[:2] for s in SERVER_INFO]
	staff_in = []

	for s in servers:
		server_obj = dc.utils.get(BRAIN.guilds, id=int(s[0]))
		role_obj = [dc.utils.get(server_obj.roles, id=int(role_id)) for role_id in s[1].split(" ")]

		for r in role_obj:
			if command_user(ctx) in r.members:
				staff_in.append(server_obj)
				break
	
	return staff_in

def is_staff(ctx):
	'''
	CMD module check for commands that need staff perms somewhere
	'''

	staff_in = staff_servers(ctx)

	if is_dm(ctx): # Is the member staff somewhere
		return (len(staff_in) > 0)
	else: # Is the member staff in the server
		return (ctx.guild in staff_in)