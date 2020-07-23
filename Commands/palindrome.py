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

	input_phrase = " ".join(args[1])
	str_phrase = input_phrase.upper()
	phrase = list(str_phrase)

	repeating = []
	substr_length = int(len(phrase) / 2)

	while substr_length != 0:
		for s in range(len(phrase) - 2*substr_length + 1):
			test_substr = phrase[s:s+substr_length]
			test_substr = "".join(test_substr)

			if str_phrase.count(test_substr) > 1:
				ind1 = str_phrase.find(test_substr)
				ind2 = str_phrase.rfind(test_substr)

				valid = True

				for already_found in repeating:
					f1start = already_found[2]
					f1end = f1start + len(already_found[0])

					f2start = already_found[2]
					f2end = f1start + len(already_found[0])

					ind1end = ind1 + substr_length
					ind2end = ind2 + substr_length

					intersecting11 = (f1start < ind1 <= f1end) or (f1end > ind1end >= f1start)
					intersecting22 = (f2start < ind2 <= f2end) or (f2end > ind2end >= f2start)
					intersecting12 = (f2start < ind1 <= f2end) or (f2end > ind1end >= f2start)
					intersecting21 = (f1start < ind2 <= f1end) or (f1end > ind2end >= f1start)

					if True in [intersecting11, intersecting22, intersecting12, intersecting21]:
						valid = False
						break
				
				if not valid:
					continue
				
				repeating.append([test_substr, ind2 - ind1, ind1, ind2])
		
		substr_length -= 1
	
	if len(repeating) == 0:
		print("can't turn into palindrome")
		return
	
	repeating = sorted(repeating, reverse=True, key=lambda m: m[1])
	repeating = sorted(repeating, reverse=True, key=lambda m: len(m[0]))

	print(repeating)

	p_sets = []

	for l_set in repeating:
		valid = True

		for p in p_sets:
			intersecting = (l_set[2] < p[2]) or (l_set[3] > p[1])

			if not intersecting: # If they're not intersecting, there's no conflict with this p_set
				continue
			
			after1 = l_set[2] > p[1]
			after2 = l_set[3] > p[2]
			

			if after1 and after2: # (p (l )p )l -- invalid
				valid = False
			elif not after1 and not after2: # (l (p )l )p -- invalid
				valid = False
		
		if not valid:
			continue
		
		adjusted1 = l_set[2]
		adjusted2 = l_set[3]

		ind = 0
		while True:
			if adjusted1 == ind:
				phrase[adjusted1:adjusted1] = "("
				adjusted2 += 1

				if adjusted2 - adjusted1 > len(l_set[0]) + 1:
					second_ind = adjusted1 + len(l_set[0]) + 1
					phrase[second_ind:second_ind] = "("
					adjusted2 += 1
				
				if len(l_set[0]) > 1:
					phrase[adjusted1+1:adjusted1+1] = "("
					second_ind = adjusted1 + 2 + len(l_set[0])
					phrase[second_ind:second_ind] = ")"
					adjusted2 += 2
			
			if adjusted2 == ind:
				adjusted2 += len(l_set[0]) - 4
				if adjusted2 - adjusted1 > len(l_set[0]) + 2:
					second_ind = adjusted2 - len(l_set[0])
					phrase[second_ind:second_ind] = ")"
				phrase[adjusted2+1:adjusted2+1] = ")"

				if len(l_set[0]) > 1:
					substr_start = adjusted2-len(l_set[0])+1
					phrase[substr_start:substr_start] = "("
					second_ind = adjusted2 + 2
					phrase[second_ind:second_ind] = ")"
				break

			try:
				if phrase[ind] in "()":
					if ind < adjusted1:
						adjusted1 += 1
					if ind < adjusted2:
						adjusted2 += 1
			except IndexError:
				pass
			
			ind += 1
		
		p_sets.append([len(l_set[0])] + l_set[2:])
	
	phrase = "".join(phrase)

	await message.channel.send(f"""Successfully generated a Cary-style palindrome!
	**Original Phrase** : `{' '.join(args[1:]).upper()}`
	**Generated Palindrome** : `{phrase}`
	
	Try it out at https://htwins.net/palindrome/ !""".replace("\t", ""))
	return