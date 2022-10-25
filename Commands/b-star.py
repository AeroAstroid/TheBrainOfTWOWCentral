import os
import time

from dotenv import load_dotenv

from Helper.__comp import *
# from bot import bot
from Commands.bstar.src.database.s3 import createTag, getTag, infoTag, updateTag, isOwnerProgram, editTag, deleteTag, \
    leaderboards, \
    connectToDatabase
from Commands.bstar.src.interpreter.function_deco import setupFunctions
from Commands.bstar.src.interpreter.run import runCode

prod = os.environ.get("IS_HEROKU", False)


async def accept_file_or_message(ctx, message):
    if len(ctx.message.attachments) > 0:
        attachment = ctx.message.attachments[0]
        try:
            await attachment.save(f"Config/{ctx.message.id}.txt")
        except Exception:
            raise "Include a program to save!"
        file = open(f"Config/{ctx.message.id}.txt", "r", encoding="utf-8").read()
        os.remove(f"Config/{ctx.message.id}.txt")
        if attachment.size >= 150_000:
            raise "File is too large! (150KB MAX)"
        else:
            return file
    else:
        return message


def setup(BOT):
    BOT.add_cog(Bstar(BOT))


class Bstar(cmd.Cog):
    '''B* in TBOTC'''

    # Extra arguments to be passed to the command
    FORMAT = "`(*server_args)`"
    CATEGORY = "SERVER"
    EMOJI = CATEGORIES[CATEGORY]
    ALIASES = ['tag', 'b*']

    def __init__(self, BRAIN):
        self.BRAIN = BRAIN
        # load_dotenv()
        setupFunctions()
        # connectToDatabase()
        # print(bot.user.name)
        # print(bot.user.id)
        global startTime  # global variable to be used later for uptime
        startTime = time.time()  # snapshot of time when listener sends on_ready

    @cmd.slash_command(name="tag")
    @cmd.cooldown(1, 2)
    async def slash_bstar(self, ctx, server=''):
        '''
        B* but as a slash command!!
        '''
        print("WIP")
        return

    @cmd.command(aliases=ALIASES)
    async def bstar(self, ctx, *server_args):
        match server_args[0]:
            case "create":
                """Creates a B* tag with your code"""
                name = server_args[1]
                message = server_args[2:]

                if len(name) < 50:
                    try:
                        createTag(ctx.author, name, await accept_file_or_message(ctx, message))
                        await ctx.send(f"Tag `{name}` created!")
                    except Exception as e:
                        await ctx.send(e)
                else:
                    await ctx.send(f"The name \"`{name}`\" is too long!")
                    # except:
                    #     await ctx.send("Tag creation failed")

            case "run":
                """Run B* code""".join("")
                code = " ".join(server_args[1:])

                try:
                    output = runCode(await accept_file_or_message(ctx, code), ctx.author)
                    await ctx.send(output)
                except Exception as e:
                    await ctx.send(e)

            case "tag":
                """Runs a B* tag"""
                message = server_args[1]
                arguments = server_args[2:]

                tagObject = getTag(message)
                if tagObject is not None:
                    code = tagObject["program"]
                    # TODO: this is float only rn, do support for int in the future
                    argument_list = arguments.split(" ")

                    output = runCode(code, ctx.author, argument_list)
                    await ctx.send(output)

                    # If all goes well, then increment the use
                    updateTag(message)
                else:
                    await ctx.send(f"There's no program under the name `{message}`!")

            case "info":
                """Gives infomation and source code about a B* tag"""
                message = server_args[1]

                await ctx.send(await infoTag(ctx, message))

            case "leaderboard":
                """Shows the leaderboard of tags sorted by uses"""
                page = server_args[1]

                await ctx.send(await leaderboards(page))

            case "edit":
                """Edit one of your B* tags"""
                name = server_args[1]
                message = server_args[2:]

                if isOwnerProgram(name, ctx.author.id):
                    try:
                        editTag(name, await accept_file_or_message(ctx, message))
                        await ctx.send(f"Tag `{name}` edited!")
                    except Exception as e:
                        await ctx.send(e)
                else:
                    await ctx.send(f"You aren't the owner of tag `{name}`!")

            case "delete":
                """Delete one of your B* tags"""
                name = server_args[1]

                if isOwnerProgram(name, ctx.author.id):
                    deleteTag(name)
                    await ctx.send(f"Tag `{name}` deleted!")
                else:
                    await ctx.send(f"You aren't the owner of tag `{name}`!")

            case "_":
                print("Unknown Command!")

        return
