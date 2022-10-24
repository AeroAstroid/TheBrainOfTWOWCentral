from Helper.__functions import m_line

print("COMMAND GENERATOR")
print("NOTE: All of this can be edited later in the command file\n")

cmd_name = input(m_line("""
	Command name: /n/
	- must start with a letter and must only have alphanumeric chars or underscores /n/
	/t/> """)
).lower().strip()
print("\n")

cog_name = list(cmd_name)
cog_name[0] = cog_name[0].upper()
cog_name = "".join(cog_name)

arguments = input(m_line("""
	Command arguments: /n/
	- separated by spaces /n/
	- each must start with a letter and must only have alphanumeric chars or underscores /n/
	- add an asterisk* to make it an optional argument instead of a required one /n/
	- leave blank for no arguments /n/
	/t/> """)
).lower().strip().split(" ")
print("\n")


if len(arguments) > 0:
	help_arguments = " ".join(
		[f"`({arg[:-1]})`" if arg.endswith("*") else f"`[{arg}]`" for arg in arguments])

	arguments = ",\n\t\t" + ",\n\t\t".join(
		[f"{arg[:-1]} = ''" if arg.endswith("*") else arg for arg in arguments])

else:
	help_arguments = ""
	arguments = ""

aliases = input(m_line("""
	Command aliases: /n/
	- separated by spaces /n/
	- leave blank for no aliases /n/
	/t/> """)
).lower().strip().split(" ")
print("\n")

aliases = "[" + ", ".join([f'\'{alias.lower()}\'' for alias in aliases]) + "]"

cooldown = input(m_line("""
	Command cooldown: /n/
	- number of seconds /n/
	- leave blank for default (1 second) /n/
	/t/> """)
).strip()
print("\n")

if cooldown == "":
	cooldown = "1"

checks = input(m_line("""
	Permission checks to apply to the command: /n/
	- options: dev, staff_anywhere, staff_here /n/
	- include all options wanted separated by spaces /n/ 
	/t/> """)
).lower().strip().split()
print("\n")

dev_check = ""
dev_check_import = ""
if "dev" in checks:
	dev_check = "\n\t@cmd.check(is_dev)"
	dev_check_import = "\nfrom Helper.__functions import is_dev"

staff_check = ""
staff_check_import = ""
if "staff_anywhere" in checks:
	staff_check = "\n\t@cmd.check(is_staff)"
	staff_check_import = "\nfrom Helper.__server_functions import is_staff"

staff_h_check = ""
staff_h_check_import = ""
if "staff_here" in checks:
	staff_h_check = "\n\t@cmd.check(is_staff_here)"

	if staff_check_import:
		staff_h_check_import = ", is_staff_here"
	else:
		staff_h_check_import = "\nfrom Helper.__server_functions import is_staff_here"

with open('Helper/template_cmd.txt', 'r', encoding='utf-8') as f:
	original_code = f.read()

filled_in = original_code.replace(
	"{cog_name}", cog_name).replace(
	"{help_arguments}", help_arguments).replace(
	"{aliases}", aliases).replace(
	"{cooldown}", cooldown).replace(
	"{cmd_name}", cmd_name).replace(
	"{arguments}", arguments).replace(
	"{dev_check}", dev_check).replace(
	"{staff_check}", staff_check).replace(
	"{staff_h_check}", staff_h_check).replace(
	"{dev_check_import}", dev_check_import).replace(
	"{staff_h_check_import}", staff_h_check_import).replace(
	"{staff_check_import}", staff_check_import)

with open(f'Commands/{cmd_name}.py', 'w', encoding='utf-8') as f:
	f.write(filled_in)

print("Command generated!")