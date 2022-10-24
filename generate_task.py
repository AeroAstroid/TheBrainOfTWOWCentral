from Helper.__functions import m_line

print("TASK GENERATOR")
print("NOTE: All of this can be edited later in the task file\n")

cog_name = input(m_line("""
	Task name: /n/
	- must start with a letter and must only have alphanumeric chars or underscores /n/
	- not required but preferrably have no separators and all words capitalized 
	(e.g. MemeChannelRenamer) /n/
	/t/> """)
).strip()
print("\n")

prefix = input(m_line("""
	Task prefix: /n/
	- preferrably up to four lowercase characters followed by a slash (e.g. mcr/) /n/
	/t/> """)
).strip()
print("\n")

is_on = input(m_line("""
	On by default? /n/
	- write "true" for true and anything else for false /n/
	- if true, the task will be activated right as the bot logs in /n/
	/t/> """)
).lower().strip() == "true"
print("\n")

print("Up next you will define the task loops you want in your script.\n")

loop_template = m_line("""
@tasks.loop({loop_time}) /n/
/t/async def {loop_name}(self): /n/
/n/
/t//t/# Write loop code here /n/
/n/
/t//t/pass
""")

task_code_signatures = ""

while True:
	loop_name = input(m_line("""
		Loop function name: /n/
		- name of the next loop to add to the task /n/
		- must start with a letter and must only have alphanumeric chars or underscores /n/
		- leave blank to adding loops /n/
		/t/> """)
	).lower().strip()
	print("\n")

	if not loop_name:
		break
	
	loop_time = input(m_line("""
		Loop interval: /n/
		- time interval between each iteration of the loop /n/
		- to add a number of hours, write a number (can be float) followed by h (eg. 1h) /n/
		- to add a number of minutes, write a number (can be float) followed by m (eg. 40.2m) /n/
		- to add a number of seconds, write a number (can be float) followed by s (eg. 5.0s) /n/
		- include these in any combination to specify the interval (eg. 2h 7.5s ; 1h 1m 1s) /n/
		- leave blank to have no interval (useful in case you want to manually set the timestamps 
		at which the task will run) /n/
		/t/> """)
	).lower().strip()
	print("\n")

	if loop_time:
		args = loop_time.split()
		time_args = []

		for a in args:
			if a.endswith("h"):
				time_args.append(f"hours={a[:-1]}")
			if a.endswith("m"):
				time_args.append(f"minutes={a[:-1]}")
			if a.endswith("s"):
				time_args.append(f"seconds={a[:-1]}")
		
		loop_time = ", ".join(time_args)
	
	task_code_signatures += (("" if len(task_code_signatures) == 0 else "\n\n") +
		loop_template.replace("{loop_time}", loop_time).replace("{loop_name}", loop_name))
	
	print(f"Added {loop_name}!\n")


with open('Helper/template_task.txt', 'r', encoding='utf-8') as f:
	original_code = f.read()

filled_in = original_code.replace(
	"{cog_name}", cog_name).replace(
	"{prefix}", prefix).replace(
	"{is_on}", str(is_on)).replace(
	"{task_code_signatures}", task_code_signatures)

with open(f'Tasks/{cog_name}.py', 'w', encoding='utf-8') as f:
	f.write(filled_in)

print("Task generated!")