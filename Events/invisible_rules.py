import os
from time import time
import discord as dc
import importlib
import numpy as np
from math import ceil

from discord.ui import Button, View

from Config._functions import m_line

def DEFAULT_PARAM():
    return { # Define all the parameters necessary
        "PLAYER_ROLE_ID": None,
        "ANNOUNCE_CHANNEL_ID": None,
        "GAME_CHANNEL_ID": None,
        "EVENT_ADMIN_ID": None,

        "PHASE_1_ROUND_TIME": 900,
        "PHASE_2_ROUND_TIME": 900,

        "PHASE_1_LEN": 0,
        "PHASE_2_LEN": 5,
        "PHASE_1_TEST_LEN": 10,
        "PHASE_2_TEST_LEN": 10,
        
        "WRONG_ANSWER_PENALTY": 0.02,
        "MAX_TIME_PENALTY": 0.45
    }

def DEFAULT_GAME():
    return { # Game variables
        "ROUND": 0,
        "PHASE": 1,

        "RULES": [],
        "RULE_DESC": [],
        "TEST_GEN": None,

        "PLAYERS": [],
        "TOTAL_POINTS": [],

        "INSPECTING": [],
        "TESTING": [],
        "PLAYER_TESTS": [],

        "NEXT_PERIOD": 0,
        "PERIOD_STEP": 0,
        "ROUND_RUNNING": False,
        "TRACKED_MSGS": [],
        
        "MAX_POINTS": []
    }

class EVENT:
    # Executes when loaded
    def __init__(self):
        self.RUNNING = False
        self.GAME_STARTED = False
        
        self.GAME = DEFAULT_GAME()

        self.PLAYER_ROLE = None
        self.ANNOUNCE_CHANNEL = None
        self.GAME_CHANNEL = None

        self.PARAM = DEFAULT_PARAM()
    
    def start(self, SERVER):
        self.RUNNING = True

        self.PARAM["PLAYER_ROLE_ID"] = 498254150044352514
        self.PARAM["ANNOUNCE_CHANNEL_ID"] = 598613590190325760
        self.PARAM["GAME_CHANNEL_ID"] = 830232343331209216
        self.PARAM["EVENT_ADMIN_ID"] = 959155078844010546

        self.EVENT_ADMIN = dc.utils.get(SERVER["MAIN"].roles, id=self.PARAM["EVENT_ADMIN_ID"])

        self.SERVER = SERVER

    def end(self):
        self.RUNNING = False
        self.GAME_STARTED = False
        
        self.GAME = DEFAULT_GAME()

        self.PLAYER_ROLE = None
        self.ANNOUNCE_CHANNEL = None
        self.GAME_CHANNEL = None
    
    def make_timer(self, remaining, just_timestamp=False):
        round_t = self.PARAM[f"PHASE_{self.GAME['PHASE']}_ROUND_TIME"]

        p = int(np.ceil((remaining / round_t) * 8))

        if p >= 7:
            emoji = ["🟩"] # Green square
        elif p >= 5:
            emoji = ["🟨"] # Yellow square
        elif p >= 3:
            emoji = ["🟧"] # Orange square
        else:
            emoji = ["🟥"] # Red square
        
        timer_bar = ["➡️"] + emoji * p + ["⬛"] * (8 - p)  + ["⬅️"]

        timer_bar = " ".join(timer_bar)

        if remaining != 0:
            msg = f"{'⌛' if p % 2 == 0 else '⏳'} **The round ends <t:{self.GAME['NEXT_PERIOD']}:R>!**"
        else:
            msg = "⌛ **The round has ended!**"
        
        if just_timestamp:
            return msg

        return msg + "\n\n" + timer_bar
    
    # Currently not fully implemented
    def generate_test_msg(self, uid, rule):
        return self.GAME["TEST_GEN"].gen_test(uid, rule)
    
    def reset_test(self, uid):
        return self.GAME["TEST_GEN"].reset_test(uid)

    # Function that runs every two seconds
    async def on_two_second(self):

        if not self.GAME_STARTED:
            return
        
        # Within a period
        if time() <= self.GAME["NEXT_PERIOD"]:
            if self.GAME["ROUND_RUNNING"]:
                round_t = self.PARAM[f"PHASE_{self.GAME['PHASE']}_ROUND_TIME"]

                edit_delay = round_t / 32 # Amount of iterations (2s each) between timer edits

                if self.GAME["PERIOD_STEP"] % edit_delay < 1:

                    await self.GAME["TRACKED_MSGS"][0].edit(content=m_line(
                    f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!/n
                    Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
                    messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

                    {self.make_timer(self.GAME["NEXT_PERIOD"] - time())}"""))
                
                self.GAME["PERIOD_STEP"] += 1
            
            return
        
        if self.GAME["ROUND"] > 0: # Ending a round
            if self.GAME["ROUND_RUNNING"]:
                self.GAME["ROUND_RUNNING"] = False
                self.GAME["PERIOD_STEP"] = 0

            if self.GAME["PERIOD_STEP"] == -1:
                self.GAME["ROUND"] = -(self.GAME["ROUND"] + 1)
                return
            
            if self.GAME["PERIOD_STEP"] == 0:
                await self.ANNOUNCE_CHANNEL.send(f"🔍 **Round {self.GAME['ROUND']} has ended!**")
                await self.GAME_CHANNEL.send(f"🔍 **Round {self.GAME['ROUND']} has ended!**")

                # Ensures all players can't talk in the channel
                await self.GAME_CHANNEL.set_permissions(self.PLAYER_ROLE, send_messages=False)
                
                await self.GAME["TRACKED_MSGS"][0].edit(content=m_line(
                f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!/n
                Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
                messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

                {self.make_timer(0)}"""))

                for t_msg in self.GAME["TRACKED_MSGS"][1:]:
                    try:
                        await t_msg.edit(content=m_line(
                        f"""🔍 **Invisible Rules: Round {self.GAME['ROUND']} (Phase {self.GAME['PHASE']})**

                        {self.make_timer(0, just_timestamp=True)}"""))

                        # Ensures the player can see the channel
                        await self.GAME_CHANNEL.set_permissions(t_msg.channel.recipient, overwrite=None)
                    except Exception:
                        pass
                
                for test_msg_info in self.GAME["PLAYER_TESTS"]:
                    if test_msg_info[5] == 0:
                        await test_msg_info[4].edit(view=None, content=
                        f"📝 **Round {self.GAME['ROUND']} Rules Test!**\nThe round has ended; you've run out of time!")

                self.GAME["INSPECTING"] = []
            
            if self.GAME["PERIOD_STEP"] == 3:
                await self.ANNOUNCE_CHANNEL.send(m_line(f"""
                The **Round {self.GAME['ROUND']} Rule** was:/n
                > **```{self.GAME['RULE_DESC'][self.GAME['ROUND']-1]}```**"""))
            
            if self.GAME["PERIOD_STEP"] == 5:
                await self.ANNOUNCE_CHANNEL.send("Test results are as follows:")
            
            if self.GAME["PERIOD_STEP"] == 7:
                results_list = [
                    # Username, total score, round score, test result, time, started test
                    [p, self.GAME["TOTAL_POINTS"][ind], 0, 0, 9999999, False]
                    for ind, p in enumerate(self.GAME["PLAYERS"])
                ]

                for ind, p in enumerate(results_list):
                    if p[0] not in self.GAME["TESTING"]:
                        continue
                    
                    p_ind = self.GAME["TESTING"].index(p[0])
                    p_test = self.GAME["PLAYER_TESTS"][p_ind]

                    results_list[ind][4] = p_test[5] if p_test[5] != 0 else 9999999
                    results_list[ind][5] = True

                    
                    ap_ind = self.GAME["ALL_PLAYERS"].index(p[0])
                    
                        
                    if p_test[5] != 0:
                        if self.GAME["PHASE"] == 1:
                            score = p_test[3].count(1)
                            
                            if score >= self.PARAM["PHASE_1_TEST_LEN"]-1:
                                results_list[ind][2] = self.GAME["MAX_POINTS"][self.GAME["ROUND"]]

                        else:
                            score = p_test[3].count(0)
                            
                            if results_list[ind][4] < 9999999:
                                results_list[ind][2] = max(ceil(self.GAME["MAX_POINTS"][self.GAME["ROUND"]]*(1
                                    -self.PARAM["MAX_TIME_PENALTY"]*results_list[ind][4]/self.PARAM["PHASE_2_ROUND_TIME"]
                                    -self.PARAM["WRONG_ANSWER_PENALTY"]*score)), 0)
                        
                        results_list[ind][3] = score
                        results_list[ind][1] += results_list[ind][2]
                        self.GAME["TOTAL_POINTS"][ind] = results_list[ind][1]
                        
                
                results_list = sorted(results_list, key=lambda m: -m[1])

                result_msgs = [f"🏆 **Standings after Round {self.GAME['ROUND']}**\n\n"]
                p_len = len(results_list)

                for ind, p in enumerate(results_list):

                    p_line = f"`[{ind+1}]` **{p[1]} pts** (+{p[2]}) <@{p[0].id}> --- "

                    if not p[5]:
                        p_line += "Did not start test\n"
                    
                    elif p[4] == 9999999:
                        p_line += "Did not finish test\n"

                    else:
                        m, s = (int(p[4] // 60), int(p[4] % 60))
                        m_str = f"{m}:{s:>02}"

                        p_line += f"**Finished in {m_str}** /// "
                        
                        if self.GAME["PHASE"] == 1:
                            p_line += f"{p[3]}/{self.PARAM['PHASE_1_TEST_LEN']} score"
                        else:
                            p_line += f"{p[3]} wrong answer(s)"
                        
                        p_line += "\n"

                    if len(result_msgs[-1] + p_line) >= 1950:
                        result_msgs.append("")
                    
                    result_msgs[-1] += p_line

                for msg in result_msgs:
                    await self.ANNOUNCE_CHANNEL.send(msg)
            
            if self.GAME["PERIOD_STEP"] == 19:
                new_round = self.GAME["ROUND"] + 1
                
                if self.GAME["ROUND"] >= len(self.GAME["RULES"]):
                    await self.ANNOUNCE_CHANNEL.send("Invisible Rules has finished!")
                    final_results = []

                    for p, score in zip(self.GAME["PLAYERS"], self.GAME["TOTAL_POINTS"]):
                        final_results.append([p.name, p.id, score])

                    final_results = "\n".join(["\t".join([str(r) for r in row]) for row in final_results])

                    with open('IR_Results.txt', 'w', encoding='utf-8') as f:
                        f.write(final_results)

                    # Send a log of results in a staff channel
                    await self.SERVER["MAIN"].get_channel(716131405503004765).send(file=dc.File('IR_Results.txt'))

                    os.remove('IR_Results.txt')
                    return False

                if self.GAME["ROUND"] != self.PARAM["PHASE_1_LEN"]:
                    await self.ANNOUNCE_CHANNEL.send(f"🔍 **Stand by! Round {new_round} will begin in 20 seconds!**")
                    await self.ANNOUNCE_CHANNEL.send(f"This round is worth **{self.GAME['MAX_POINTS'][self.GAME['ROUND']+1]}** points.")
                    self.GAME["PERIOD_STEP"] = -1
                    self.GAME["NEXT_PERIOD"] = int(time() + 20)
                    self.GAME["ROUND"] = -new_round

                else:
                    self.GAME["PHASE"] = 2
                    self.GAME["ROUND"] = 0
                    self.GAME["PERIOD_STEP"] = 0
                
                return
            
            self.GAME["PERIOD_STEP"] += 1
            return

        
        if self.GAME["ROUND"] < 0: # Ending an intermission between rounds
            round_t = self.PARAM[f"PHASE_{self.GAME['PHASE']}_ROUND_TIME"]

            self.GAME["TEST_GEN"].reset()

            self.GAME["ROUND"] *= -1

            self.GAME["INSPECTING"] = self.GAME["PLAYERS"].copy()
            self.GAME["TESTING"] = []
            self.GAME["PLAYER_TESTS"] = []

            self.GAME["NEXT_PERIOD"] = int(time() + round_t)
            # Round 1 gets less time bc it's a practice round
            if self.GAME["ROUND"] == 1:
                self.GAME["NEXT_PERIOD"] = int(time() + min(300, round_t))
            self.GAME["PERIOD_STEP"] = 0
            self.GAME["ROUND_RUNNING"] = True
            
            ann_timer = await self.ANNOUNCE_CHANNEL.send(m_line(
            f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!/n
            Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
            messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

            {self.make_timer(round_t)}"""))

            phase_msg = f" (Phase {self.GAME['PHASE']})" if self.PARAM['PHASE_1_LEN'] > 0 and self.PARAM['PHASE_2_LEN'] > 0 else ''
            await self.GAME_CHANNEL.send(f"🔍 **Invisible Rules: Round {self.GAME['ROUND']}{phase_msg}**")

            await self.GAME_CHANNEL.set_permissions(self.PLAYER_ROLE, send_messages=True)

            self.GAME["TRACKED_MSGS"] = [ann_timer]

            for p in self.GAME["PLAYERS"]:
                try:
                    msg = await p.send(m_line(
                    f"""🔍 **Invisible Rules: Round {self.GAME['ROUND']}{phase_msg}**

                    {self.make_timer(round_t, just_timestamp=True)}

                    Send **`ir/test`** to stop inspecting the rule and access the test!"""))

                    self.GAME["TRACKED_MSGS"].append(msg)
                except Exception:
                    pass

            return

        if self.GAME["ROUND"] == 0: # Intermission between phases
            message_delay = 4 # Amount of iterations (2s each) between messages
            
            if self.PARAM["PHASE_1_LEN"] == 0:
                self.GAME["PHASE"] = 2

            if self.GAME["PHASE"] == 1:
                m, s = [int(self.PARAM["PHASE_1_ROUND_TIME"] // 60), int(self.PARAM["PHASE_1_ROUND_TIME"] % 60)]
                m_str = f"{m} minute{'s' if m != 1 else ''}" + (f" {s} second{'s' if s != 1 else ''}" if s != 0 else "")

                lines = [
                    "🔍 **Welcome to Invisible Rules!**",

                    "```diff\n+ PHASE ONE: Legal Forensics```",

                    f"> For this phase, each round lasts **{m_str}**.",

                    m_line(f"""> Once the round starts, everyone playing will be able to **INSPECT** the current 
                    rule by sending messages in <#{self.GAME_CHANNEL.id}>. The bot will react to every message 
                    that doesn't use invalid characters with a ✅ **if it passes the rule**, or a ❌ **if it 
                    breaks the rule.** If a message **has invalid characters**, the bot will react with ❔ regardless 
                    of whether it passes the rule or not. You may send as many messages as you want. There is no 
                    penalty or reward for specifically sending messages that break or pass the rule. Valid characters 
                    are letters and spaces. Rules are case-insensitive. All other characters are invalid"""),

                    m_line(f"""> A player who is confident they figured out the rule can **DM me with the command 
                    `ir/test`** to stop INSPECTING and start **TESTING**. This command is **final** - you will be 
                    locked out of <#{self.GAME_CHANNEL.id}> and cannot go back to INSPECTING for the remainder of 
                    the round."""),

                    m_line(f"""> Once they switch to **TESTING**, players will receive a **test** comprised of 
                    {self.PARAM['PHASE_1_TEST_LEN']} messages. You must indicate, for each message, whether it 
                    PASSES or BREAKS the current rule. You will be given no immediate feedback on whether or not 
                    your answers are correct. After doing so for all {self.PARAM['PHASE_1_TEST_LEN']} messages, 
                    you will be **FINISHED** with the round."""),

                    m_line(f"""> Players that finish their test in time and score at least 
                    **{self.PARAM['PHASE_1_TEST_LEN']-1}/{self.PARAM['PHASE_1_TEST_LEN']}** on the test will 
                    receive a fixed amount of points that does not depend on speed or score."""),

                    m_line(f"""> **PHASE ONE: Legal Forensics** will last for the first **{self.PARAM['PHASE_1_LEN']} 
                    rounds** of the game."""),
                ]
                
                if self.PARAM["PHASE_2_LEN"] == 0:
                    lines = lines[2:-1]
                    lines[0] = f"> Each round lasts **{m_str}**."
            
            elif self.GAME["PHASE"] == 2:
                m, s = [self.PARAM["PHASE_2_ROUND_TIME"] // 60, self.PARAM["PHASE_2_ROUND_TIME"] % 60]
                m_str = f"{m} minute{'s' if m != 1 else ''}" + (f" {s} second{'s' if s != 1 else ''}" if s != 0 else "")
                decay_str = f"{self.PARAM['MAX_TIME_PENALTY']*100*60/self.PARAM['PHASE_2_ROUND_TIME']:.2f}%"
                wa_str = f"{self.PARAM['WRONG_ANSWER_PENALTY']*100:.2f}%"

                lines = [
                    "🔍 **It's time for Phase Two!**",

                    "```diff\n- PHASE TWO: Investigative Journalism```",

                    m_line(f"""> For this phase, each round lasts **{m_str}**. Points now depend on speed and 
                    accuracy."""),

                    m_line("""> The **INSPECTION** period will work the same as in PHASE ONE - you may send 
                    as many messages as you want, and you'll be told whether or not they break the rule, 
                    without any penalty."""),

                    m_line(f"""> To start **TESTING**, DM me with **`ir/test`**. In the PHASE TWO TEST, you will be 
                    sequentially shown a series of {self.PARAM['PHASE_2_TEST_LEN']} messages, one by one, and must 
                    answer whether or not they PASS or BREAK the current rule as they come."""),

                    m_line(f"""> The test is considered to be passed if the player gives correct answers for all 
                    messages. If you fail the test, **you will be sent back to INSPECTING**. You will be given no 
                    immediate feedback on whether or not your answers are correct (that is, until you're notified 
                    that you passed the test). You may take the test at most 10 times."""),

                    m_line(f"""> However, for this PHASE, **you may go back to INSPECTING even after starting a 
                    TEST** by DMing me with **`ir/inspect`**. You will be given access to <#{self.GAME_CHANNEL.id}> 
                    again and will be allowed to read/send more messages. Once you go back to TESTING using 
                    **`ir/test`** as usual, you will be given a completely new test."""),

                    m_line(f"""> Players that pass the test will receive an amount of points that decays by **{decay_str} 
                    every minute** and by **{wa_str} for every incorrect answer** they give at any point in the test. 
                    Players that don't pass the test, as well as players that passed the test but scored negative, will 
                    receive no points for the round."""),
                ]
                
                if self.PARAM["PHASE_1_LEN"] == 0:
                    lines = lines[2:]
                    lines[0] = f"> Each round lasts **{m_str}**."
                    lines[1] = m_line(f"""> Once the round starts, everyone playing will be able to **INSPECT** the current 
                    rule by sending messages in <#{self.GAME_CHANNEL.id}>. The bot will react to every message 
                    that doesn't use invalid characters with a ✅ **if it passes the rule**, or a ❌ **if it 
                    breaks the rule.** If a message **has invalid characters**, the bot will react with ❔ regardless 
                    of whether it passes the rule or not. You may send as many messages as you want. There is no 
                    penalty or reward for specifically sending messages that break or pass the rule. Valid characters 
                    are letters and spaces. Rules are case-insensitive. All other characters are invalid""")
                    lines[2] = m_line(f"""> To start **TESTING**, DM me with **`ir/test`**. You will be 
                    sequentially shown a series of {self.PARAM['PHASE_2_TEST_LEN']} messages, one by one, and must 
                    answer whether or not they PASS or BREAK the current rule as they come.""")
                    lines[4] = m_line(f"""> **You may go back to INSPECTING even after starting a 
                    TEST** by DMing me with **`ir/inspect`**. You will be given access to <#{self.GAME_CHANNEL.id}> 
                    again and will be allowed to read/send more messages. Once you go back to TESTING using 
                    **`ir/test`** as usual, you will be given a completely new test.""")

            # Post the messages every [message_delay] iterations
            if self.GAME["PERIOD_STEP"] % message_delay == 0:
                ind = self.GAME["PERIOD_STEP"] // message_delay

                if ind >= len(lines):
                    self.GAME["ROUND"] = -1 if self.GAME['PHASE'] == 1 else -(self.PARAM['PHASE_1_LEN']+1)
                    self.GAME["NEXT_PERIOD"] = int(time() + 30)
                    self.GAME["PERIOD_STEP"] = 0

                    phase_msg = f"Phase {self.GAME['PHASE']} and " if self.PARAM['PHASE_1_LEN'] > 0 and self.PARAM['PHASE_2_LEN'] > 0 else ''
                    await self.ANNOUNCE_CHANNEL.send(
                    f"🔍 **Stand by! {phase_msg}Round {-self.GAME['ROUND']} will begin in 30 seconds!**")
                    await self.ANNOUNCE_CHANNEL.send(f"This round is worth **{self.GAME['MAX_POINTS'][-self.GAME['ROUND']]}** points.")
                    return
                
                await self.ANNOUNCE_CHANNEL.send(lines[ind])
            
            self.GAME["PERIOD_STEP"] += 1
            
            return

    # Function that runs on each message
    async def on_message(self, message):
        msg = message.content

        if not self.GAME_STARTED:

            # Pre-game setup is limited solely to commands
            if not msg.lower().startswith("ir/"):
                return
            
            # Commands are limited solely to event administrators
            if message.author not in self.EVENT_ADMIN.members:
                return

            args = msg.split(" ")
            cmd = args[0][3:].lower()

            if cmd == "begin":
                player_role = dc.utils.get(self.SERVER["MAIN"].roles, id=int(self.PARAM["PLAYER_ROLE_ID"]))
                announce_channel = dc.utils.get(self.SERVER["MAIN"].channels, id=int(self.PARAM["ANNOUNCE_CHANNEL_ID"]))
                game_channel = dc.utils.get(self.SERVER["MAIN"].channels, id=int(self.PARAM["GAME_CHANNEL_ID"]))

                if player_role is None:
                    await message.channel.send(
                    "💀 **Can't start: PLAYER_ROLE_ID doesn't point to a valid role!**")
                    return
                
                if announce_channel is None:
                    await message.channel.send(
                    "💀 **Can't start: ANNOUNCE_CHANNEL_ID doesn't point to a valid channel!**")
                    return
                
                if game_channel is None:
                    await message.channel.send(
                    "💀 **Can't start: GAME_CHANNEL_ID doesn't point to a valid channel!**")
                    return
                
                players = player_role.members

                if len(players) == 0:
                    await message.channel.send("💀 **Can't start: the player role has no members!**")
                    return
                
                rule_count = len(self.GAME["RULES"])
                
                if rule_count == 0:
                    await message.channel.send("💀 **Can't start: no rules have been registered!**")
                    return
                
                if len(args) == 1 or args[1].lower() != "confirm":
                    current_params = "\n".join([f"**{k}**: {v}" for k, v in self.PARAM.items()])
                    await message.channel.send(
                    f"❓ **Do you wish to start the game?** Send `ir/begin confirm` to start!"
                    + f"\n\n**Parameters:**\n{current_params}"
                    + f"\n\n**Players:** {len(players)}\n**Rounds:** {rule_count}")
                    return
                
                self.PLAYER_ROLE = player_role
                self.ANNOUNCE_CHANNEL = announce_channel
                self.GAME_CHANNEL = game_channel
                self.GAME["PLAYERS"] = players
                self.GAME["TOTAL_POINTS"] = [0]*len(players)
                self.GAME["ALL_PLAYERS"] = players

                self.GAME_STARTED = True

                await message.channel.send("✅ **Invisible Rules is now starting.**")
                return

            if cmd == "modify": # Change parameters or view them
                if len(args) == 1:
                    current_params = "\n".join([f"**{k}**: {v}" for k, v in self.PARAM.items()])
                
                    await message.channel.send("📑 **Here are the current event parameters:**\n\n"
                    + current_params)
                    return
                
                parameter = args[1].upper()

                if parameter not in self.PARAM.keys():
                    await message.channel.send(
                    "❌ **That parameter is not available for this event!**")
                    return
                
                if len(args) == 2:
                    await message.channel.send(
                    f"💀 **You must include a new value for the {parameter} parameter!**")
                    return
                
                value = " ".join(args[2:])
                old_value = self.PARAM[parameter]
                old_type = type(self.PARAM[parameter])

                self.PARAM[parameter] = old_type(value)

                await message.channel.send(
                f"✅ **Successfully edited {parameter}** from\n> `{old_value}`\nto\n> `{value}`")
                return
            
            if cmd == "setrules":
                if len(message.attachments) == 0:
                    await message.channel.send(
                    f"💀 **Send a file containing the rule scripts!**")
                    return
                
                try:
                    await message.attachments[0].save(f"{message.id}_IR_RULES.py")

                    TEMP_IR_RULES = importlib.import_module(f"{message.id}_IR_RULES")

                    rule_funcs = [attr for attr in dir(TEMP_IR_RULES) if not attr.startswith("__") and attr.startswith("rule")]

                    RULES = [getattr(TEMP_IR_RULES, func) for func in rule_funcs]
                    RULE_DESC = [f.__doc__.strip() for f in RULES]
                    MAX_POINTS = TEMP_IR_RULES.MAX_POINTS

                    os.remove(f"{message.id}_IR_RULES.py")

                except Exception as err:
                    await message.channel.send(
                    "💀 **An error occurred while importing the rules file!**")

                    try: os.remove(f"{message.id}_IR_RULES.py")
                    except Exception: pass

                    raise err
                
                self.GAME["RULES"] = RULES
                self.GAME["RULE_DESC"] = RULE_DESC
                self.GAME["MAX_POINTS"] = MAX_POINTS

                await message.channel.send(f"✅ **Successfully imported {len(RULES)} rules!**")
                return
            
            if cmd == "settestgen":
                if len(message.attachments) == 0:
                    await message.channel.send(
                    f"💀 **Send a file containing the rule scripts!**")
                    return
                
                try:
                    await message.attachments[0].save(f"{message.id}_IR_TEST_GEN.py")

                    TEMP_IR_TEST_GEN = importlib.import_module(f"{message.id}_IR_TEST_GEN")
                    
                    await message.channel.send("Preprocessing test cases. This can take a few minutes.")
                    
                    TEST_GEN = TEMP_IR_TEST_GEN.TestGenerator()

                    os.remove(f"{message.id}_IR_TEST_GEN.py")

                except Exception as err:
                    await message.channel.send(
                    "💀 **An error occurred while importing the rules file!**")

                    try: os.remove(f"{message.id}_IR_TEST_GEN.py")
                    except Exception: pass

                    raise err
                
                self.GAME["TEST_GEN"] = TEST_GEN

                await message.channel.send(f"✅ **Successfully preprocessed the test cases!**")
                return

        else: # Game functions
            rnd = self.GAME["ROUND"]

            if not self.GAME["ROUND_RUNNING"]: # Only check messages if there's a round running
                return
            
            if message.channel == self.GAME_CHANNEL and message.author in self.GAME["INSPECTING"]:
                
                rule = self.GAME["RULES"][rnd - 1]
                
                verdict = rule(msg)
                if verdict == 1:
                    passed = "✅"
                elif verdict == 0:
                    passed = "❌"
                else:
                    passed = "❔"

                await message.add_reaction(passed)

                return

            if isinstance(message.channel, dc.DMChannel) and message.author in self.GAME["PLAYERS"]:
                if msg.lower() == "ir/test" and message.author in self.GAME["INSPECTING"]:

                    self.GAME["INSPECTING"].remove(message.author)
                    await self.GAME_CHANNEL.set_permissions(message.author, view_channel=False)

                    if self.GAME["PHASE"] == 1:
                        self.GAME["TESTING"].append(message.author)
                        
                        test_msgs = []
                        for _ in range(10):
                            test_msgs.append(self.generate_test_msg(message.author.id, self.GAME["ROUND"]))
                        
                        answer_sheet = [self.GAME["RULES"][rnd - 1](msg) for msg in test_msgs]

                        test_view = View()

                        pass_button = Button(label="Passes the rule", style=dc.ButtonStyle.green,
                        emoji="✅", custom_id=f"{message.author.id} 1")
                        pass_button.callback = self.step_through_test
                        test_view.add_item(pass_button)

                        break_button = Button(label="Breaks the rule", style=dc.ButtonStyle.red,
                        emoji="❌", custom_id=f"{message.author.id} 0")
                        break_button.callback = self.step_through_test
                        test_view.add_item(break_button)

                        test_dm_msg = await message.channel.send(
                        (f"📝 **Round {rnd} Rules Test!**\nAnswer all questions to finish the test!"
                        +f"\n\n{self.format_test_msg(test_msgs[0], 1)}"),
                        view=test_view)

                        # UserID, messages, answer sheet, player's answers, msg obj, finish time
                        self.GAME["PLAYER_TESTS"].append([message.author.id, test_msgs, 
                        answer_sheet, [], test_dm_msg, 0])
                    
                    else:
                        self.reset_test(message.author.id)
                        new_msg = self.generate_test_msg(message.author.id, self.GAME["ROUND"])
                        new_answer = self.GAME["RULES"][rnd - 1](new_msg)

                        test_view = View()

                        pass_button = Button(label="Passes the rule", style=dc.ButtonStyle.green,
                        emoji="✅", custom_id=f"{message.author.id} 1")
                        pass_button.callback = self.step_through_test
                        test_view.add_item(pass_button)

                        break_button = Button(label="Breaks the rule", style=dc.ButtonStyle.red,
                        emoji="❌", custom_id=f"{message.author.id} 0")
                        break_button.callback = self.step_through_test
                        test_view.add_item(break_button)
                            
                        n = 1

                        if message.author in self.GAME["TESTING"]:
                            u_ind = [
                                ind for ind in range(len(self.GAME["PLAYER_TESTS"]))
                                if self.GAME["PLAYER_TESTS"][ind][0] == int(message.author.id)
                            ]

                            try:
                                u_ind = u_ind[0]
                            except IndexError:
                                return

                            self.GAME["PLAYER_TESTS"][u_ind][1].append(new_msg)
                            self.GAME["PLAYER_TESTS"][u_ind][2].append(new_answer)

                            n = len(self.GAME["PLAYER_TESTS"][u_ind][1])
                        
                        test_dm_msg = await message.channel.send((f"📝 **Round {rnd} Rules Test!**\n"
                        +f"Answer all questions correctly to finish the test!"
                        +f"\n\n{self.format_test_msg(new_msg, n)}"),
                        view=test_view)

                        if message.author not in self.GAME["TESTING"]:
                            self.GAME["TESTING"].append(message.author)

                            # UserID, messages, answer sheet, player's answers, msg obj, finish time
                            self.GAME["PLAYER_TESTS"].append([message.author.id, [new_msg], 
                            [new_answer], [], test_dm_msg, 0])

                        else:
                            self.GAME["PLAYER_TESTS"][u_ind][4] = test_dm_msg

                    return

                if (msg.lower() == "ir/inspect" and message.author in self.GAME["TESTING"]
                and message.author not in self.GAME["INSPECTING"]):
                    if self.GAME["PHASE"] == 1:
                        await message.channel.send("You can't go back to inspecting after starting the test!")
                        return
                    
                    u_ind = [
                        ind for ind in range(len(self.GAME["PLAYER_TESTS"]))
                        if self.GAME["PLAYER_TESTS"][ind][0] == int(message.author.id)
                    ]
                    
                    try:
                        u_ind = u_ind[0]
                    except IndexError:
                        return
                    
                    if len(self.GAME["PLAYER_TESTS"][u_ind][3]) >= 9*self.PARAM["PHASE_2_TEST_LEN"]:
                        await message.channel.send("If you go back to inspecting now you'll run out of tests!")
                        return

                    self.GAME["INSPECTING"].append(message.author)

                    # Skip the remaining questions in the test
                    self.GAME["PLAYER_TESTS"][u_ind][3].append(-1)
                    while len(self.GAME["PLAYER_TESTS"][u_ind][3])%self.PARAM["PHASE_2_TEST_LEN"] != 0:
                        self.GAME["PLAYER_TESTS"][u_ind][1].append('')
                        self.GAME["PLAYER_TESTS"][u_ind][2].append(-1)
                        self.GAME["PLAYER_TESTS"][u_ind][3].append(-1)

                    await self.GAME_CHANNEL.set_permissions(message.author, overwrite=None)
                    await self.GAME["PLAYER_TESTS"][u_ind][4].edit(content="**Test hidden!**", view=None)

                    await message.channel.send(
                    m_line(f"""You have gone back to **inspecting** this round's rule! The test has been hidden 
                    from you.

                    Use **`ir/test`** to stop inspecting and go back to testing. Once you return to the test, **you 
                    will be presented with a new test.**

                    You are now able to see and talk in <#{self.GAME_CHANNEL.id}> again."""))

            return
    
    def format_test_msg(self, msg, n=None):
        word_count = len(msg.split(" "))
        letter_list = [c for c in list(msg.upper()) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        letters = len(letter_list)
        letters_used = sorted(list(set(letter_list)))

        info = ""
        if n is not None:
            if self.GAME["PHASE"] == 1:
                info = f"__**TEST - Message #{n}/{self.PARAM['PHASE_1_TEST_LEN']}**__\n"
            else:
                info = (f"__**TEST #{(n-1)//self.PARAM['PHASE_2_TEST_LEN']+1} - "
                +f"Message #{(n-1)%self.PARAM['PHASE_2_TEST_LEN']+1}**__\n")
            
        info += m_line(f"""
            > **```{msg}```**/n
            > Characters: `{len(msg)}`/n
            > Words: `{word_count}`/n
            > Letter Count: `{letters}`/n
            > Letters Used: `{''.join(letters_used)}`
        """)

        return info

    async def step_through_test(self, ctx):
        if not self.GAME["ROUND_RUNNING"]:
            await ctx.response.defer()
            return
        
        user, answer = ctx.data['custom_id'].split(" ")

        for i in self.GAME["INSPECTING"]:
            if i.id == int(user):
                return

        user_test_ind = [
            ind for ind in range(len(self.GAME["PLAYER_TESTS"]))
            if self.GAME["PLAYER_TESTS"][ind][0] == int(user)
        ]

        try:
            user_test_ind = user_test_ind[0]
        except IndexError:
            return
        
        n = len(self.GAME["PLAYER_TESTS"][user_test_ind][3])

        if int(answer) == int(self.GAME["PLAYER_TESTS"][user_test_ind][2][n]):
            self.GAME["PLAYER_TESTS"][user_test_ind][3].append(1)
        else:
            self.GAME["PLAYER_TESTS"][user_test_ind][3].append(0)
        
        n += 1

        rnd = self.GAME['ROUND']

        if self.GAME["PHASE"] == 1:
            if n < self.PARAM["PHASE_1_TEST_LEN"]:
                new_msg = self.GAME["PLAYER_TESTS"][user_test_ind][1][n]

                t_msg = (f"📝 **Round {rnd} Rules Test!**\nAnswer all questions to finish the test!"
                +f"\n\n{self.format_test_msg(new_msg, n+1)}")

                await ctx.response.edit_message(content=t_msg)
                return
            
            else:
                self.GAME["PLAYER_TESTS"][user_test_ind][5] = (
                    self.PARAM["PHASE_1_ROUND_TIME"] - (self.GAME["NEXT_PERIOD"] - time()))
                
                m, s = (
                    int(self.GAME["PLAYER_TESTS"][user_test_ind][5] // 60),
                    int(self.GAME["PLAYER_TESTS"][user_test_ind][5] % 60)
                )

                m_str = f"{m} minute{'s' if m != 1 else ''} {s} second{'s' if s != 1 else ''}"

                t_msg = (m_line(
                f"""📝 You have finished **Round {rnd}** in **{m_str}**!

                Your test results will be revealed once the round ends."""))

                await ctx.response.edit_message(content=t_msg, view=None)
                return
        
        else:
            required = self.PARAM["PHASE_2_TEST_LEN"]
            last_answers = self.GAME["PLAYER_TESTS"][user_test_ind][3][-required:]
            
            if 0 in last_answers or len(last_answers) < required or n%self.PARAM["PHASE_2_TEST_LEN"] != 0:
                if n >= 10*required:
                    t_msg = m_line(f"""📝 **Round {rnd} Rules Test!**

                    **You have ran out of tests (10) without being able to pass one.**""")

                    await ctx.response.edit_message(content=t_msg, view=None)
                elif n%self.PARAM["PHASE_2_TEST_LEN"] == 0:
                    player = [
                        p for p in self.GAME["PLAYERS"]
                        if p.id == int(user)
                    ]

                    try:
                        player = player[0]
                    except IndexError:
                        return
                    
                    self.GAME["INSPECTING"].append(player)

                    await self.GAME_CHANNEL.set_permissions(player, overwrite=None)
                    await self.GAME["PLAYER_TESTS"][user_test_ind][4].edit(content="**Test hidden!**", view=None)

                    await player.send(
                    m_line(f"""You have failed the test, so you have been sent back to **inspecting** 
                    this round's rule.

                    Use **`ir/test`** to stop inspecting and go back to testing. Once you return to the test, **you 
                    will be presented with a new test.**

                    You are now able to see and talk in <#{self.GAME_CHANNEL.id}> again."""))
                else:
                    new_msg = self.generate_test_msg(int(user), rnd)

                    self.GAME["PLAYER_TESTS"][user_test_ind][1].append(new_msg)

                    self.GAME["PLAYER_TESTS"][user_test_ind][2].append(
                        self.GAME["RULES"][rnd - 1](new_msg))

                    t_msg = (f"📝 **Round {rnd} Rules Test!**\n"
                    +f"Answer all the questions to finish the test!"
                    +f"\n\n{self.format_test_msg(new_msg, n+1)}")

                    await ctx.response.edit_message(content=t_msg)

                return
            
            else:
                self.GAME["PLAYER_TESTS"][user_test_ind][5] = (
                    self.PARAM["PHASE_2_ROUND_TIME"] - (self.GAME["NEXT_PERIOD"] - time()))
                
                m, s = (
                    int(self.GAME["PLAYER_TESTS"][user_test_ind][5] // 60),
                    int(self.GAME["PLAYER_TESTS"][user_test_ind][5] % 60)
                )

                m_str = f"{m} minute{'s' if m != 1 else ''} {s} second{'s' if s != 1 else ''}"

                t_msg = (m_line(
                f"""📝 You have finished **Round {rnd}** in **{m_str}**!

                Your last {required} answers were all correct. 
                It took you {len(self.GAME["PLAYER_TESTS"][user_test_ind][1])//self.PARAM["PHASE_2_TEST_LEN"]} attempts."""))

                await ctx.response.edit_message(content=t_msg, view=None)
                return
