import discord, os

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Attempts to make a Cary-style palindrome out of an input phrase",
		"FORMAT": "[phrase]",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}palindrome [phrase]` will output a Cary-style palindrome of `[phrase]`, or notify 
		you if such a palindrome could not be constructed.""".replace("\n", "").replace("\t", "")
	}

PERMS = 0 # Non-members
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a phrase to turn into a Cary-style palindrome!")
		return

	phrase = list(" ".join(args[1:]).upper())
	rev_phrase = list(reversed(phrase))

	repeating = {}
	for char in phrase:
		if phrase.count(char) > 1 and char not in repeating.keys():
			ind1 = phrase.index(char)
			ind2 = len(phrase) - rev_phrase.index(char) - 1
			repeating[char] = [ind2 - ind1, ind1, ind2]
	
	if len(repeating.keys()) == 0:
		await message.channel.send(
			"There are no repeating characters - I can't turn this into a Cary-style palindrome!")
		return
	
	repeating = [[k] + repeating[k] for k in repeating]
	repeating = sorted(repeating, reverse=True, key=lambda m: m[1])

	p_sets = []

	for l_set in repeating:
		valid = True

		for p in p_sets:
			intersecting = (l_set[2] < p[1]) or (l_set[3] > p[0])

			if not intersecting: # If they're not intersecting, there's no conflict with this p_set
				continue
			
			after1 = l_set[2] > p[0]
			after2 = l_set[3] > p[1]
			

			if after1 and after2: # (p (l )p )l -- invalid
				valid = False
			elif not after1 and not after2: # (l (p )l )p -- invalid
				valid = False
		
		if not valid:
			continue
		
		adjusted1 = l_set[2] + 1
		adjusted2 = l_set[3] - 1

		ind = 0
		while True:
			if adjusted1 == ind:
				phrase[adjusted1:adjusted1] = "("
				adjusted2 += 1
			
			if adjusted2 == ind:
				phrase[adjusted2:adjusted2] = ")"
				break

			if phrase[ind] in "()":
				if ind < adjusted1:
					adjusted1 += 1
				if ind < adjusted2:
					adjusted2 += 1
			
			ind += 1
		
		p_sets.append(l_set[2:])
	
	unsimplified = "".join(phrase)

	phrase = ["("] + phrase + [")"]

	for ind, char in enumerate(phrase):
		if ind < len(phrase) - 1:
			if char == "(" and phrase[ind + 1] == "(":
				phrase[ind] = ""
			if char == ")" and phrase[ind + 1] == ")":
				phrase[ind] = "\t"
		
		if ind > 0:
			if char == "(" and phrase[ind - 1] == "":
				phrase[ind] == ""
			if char == ")" and phrase[ind - 1] == "\t":
				phrase[ind] == "\t"
	
	phrase = [x for x in phrase if x not in ["", "\t"]]
	phrase = ''.join(phrase)

	await message.channel.send(f"""Successfully generated a Cary-style palindrome!
	**Original Phrase** : `{' '.join(args[1:]).upper()}`
	**Generated Palindrome** : `{phrase}`
	Unsimplified : `{unsimplified}`""".replace("\t", ""))
	return