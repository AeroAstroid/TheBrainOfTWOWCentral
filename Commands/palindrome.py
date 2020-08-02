import discord, os

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Attempts to make a Cary-style palindrome out of an input phrase",
		"FORMAT": "[phrase]",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}palindrome [phrase]` will output a Cary-style palindrome of `[phrase]`, or notify 
		you if such a palindrome could not be constructed.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 0 # Non-members
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a phrase to turn into a Cary-style palindrome!")
		return

	input_phrase = " ".join(args[1:])

	if "(" in input_phrase or ")" in input_phrase:
		await message.channel.send("Your phrase cannot include parentheses!")
		return

	def place_p(p_ind, phrase, p_list, p):
		p_ind = round(p_ind)
		phrase[p_ind:p_ind] = p
		for z in range(len(p_list[1])):
			if p_list[1][z] >= p_ind or (p_list[1][z] == p_ind and p == "(" and p_list[0][z] == ")"):
				p_list[1][z] += 1
		
		return [phrase, p_list]

	str_phrase = input_phrase.upper()
	phrase = list(str_phrase)

	substr_length = int(len(phrase) / 2)

	rept_list = []

	while substr_length != 0:
		checks = len(phrase) - 2*substr_length - 1

		for s in range(checks):
			substr = str_phrase[s:s+substr_length]

			if str_phrase.count(substr) > 1:
				ind1 = str_phrase.find(substr)
				ind2 = str_phrase.rfind(substr)

				rept_list.append([substr, substr_length*(ind2-ind1), ind1, ind2])

		substr_length -= 1

	rept_list = sorted(rept_list, reverse=True, key=lambda m: m[1])

	for r_ind, r in enumerate(rept_list):
		if len(r) < 4:
			continue
		
		i1start = r[2]
		i1end = r[2] + len(r[0])
		i2start = r[3]
		i2end = r[3] + len(r[0])

		for c_ind, c in enumerate(rept_list):
			if c_ind == r_ind or len(c) < 4:
				continue
			
			c1start = c[2]
			c1end = c[2] + len(c[0])
			c2start = c[3]
			c2end = c[3] + len(c[0])

			inter_11 = (i1start <= c1start < i1end) or (c1start <= i1start < c1end)
			inter_12 = (i1start <= c2start < i1end) or (c2start <= i1start < c2end)
			inter_21 = (i2start <= c1start < i2end) or (c1start <= i2start < c1end)
			inter_22 = (i2start <= c2start < i2end) or (c2start <= i2start < c2end)

			inter_before = (c2start > i2start > c1start > i1start)
			inter_after = (i2start > c2start > i1start > c1start)

			if (inter_11 or inter_12 or inter_21 or inter_22 or inter_before or inter_after):
				rept_list[c_ind] = [""]

	rept_list = [x for x in rept_list if x != [""]]

	ind_list = []
	p_list = [[], []]

	for rept in rept_list:
		ind_list.append(["", []])

		ind_list[-1][0] += "("
		ind_list[-1][1].append(rept[2])

		if len(rept[0]) > 1 and rept[0] != rept[0][::-1]:
			ind_list[-1][0] += "("
			ind_list[-1][1].append(rept[2] + 1/3)
			ind_list[-1][0] += ")"
			ind_list[-1][1].append(rept[2] + len(rept[0]) - 1/3)

		ind_list[-1][0] += "("
		ind_list[-1][1].append(rept[2] + len(rept[0]))

		ind_list[-1][0] += ")"
		ind_list[-1][1].append(rept[3])

		if len(rept[0]) > 1 and rept[0] != rept[0][::-1]:
			ind_list[-1][0] += "("
			ind_list[-1][1].append(rept[3] + 1/3)
			ind_list[-1][0] += ")"
			ind_list[-1][1].append(rept[3] + len(rept[0]) - 1/3)
	
		ind_list[-1][0] += ")"
		ind_list[-1][1].append(rept[3] + len(rept[0]))

		p_list[0] += list(ind_list[-1][0])
		p_list[1] += ind_list[-1][1]

	p_list[0] = [x for _,x in sorted(zip(p_list[1], p_list[0]))]
	p_list[1] = sorted(p_list[1])

	for char in range(len(p_list[1])):
		phrase, p_list = place_p(p_list[1][char], phrase, p_list, p_list[0][char])

	phrase = "".join(phrase)

	await message.channel.send(f"""Successfully generated a Cary-style palindrome!
	**Original Phrase** : `{str_phrase}`
	**Generated Palindrome** : `{phrase}`
	
	Try it out with **carykh**'s Palindromer: https://htwins.net/palindrome/""".replace("\t", ""))
	return