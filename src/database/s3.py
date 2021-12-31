import datetime
import os
import time
from decimal import Decimal
from typing import Dict, Union

import discord
import psycopg2
from dotenv import load_dotenv

from bot import bot

load_dotenv()
db_name = "b-star"
# replace with own
conn = psycopg2.connect(
    host=os.getenv("HOST"),
    database=os.getenv("DATABASE"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD")
)

# tag or global
item = Dict[str, Union[str, int]]

table = conn.cursor()


def getTag(name: str) -> Union[item, None]:
    table.execute("""
    SELECT * FROM "b-star".public."b-star-dev"
    WHERE name = (%s)
    """,
                  (name,))
    item = table.fetchone()
    if item is None:
        return item

    return {
        "name": item[0],
        "program": item[1],
        "author": item[2],
        "uses": item[3],
        "created": item[4],
        "lastused": item[5],
        "lastupdated": item[6],
    }


def getGlobal(name: str) -> Union[item, None]:
    table.execute("""
    SELECT * FROM "b-star".public."b-star-dev-globals"
    WHERE name = (%s)
    """,
                  (name,))
    item = table.fetchone()
    if item is None:
        return item

    return {
        "name": item[0],
        "value": item[1],
        "type": item[2],
        "owner": item[3],
        "version": item[4]
    }


def tagExists(name: str):
    return getTag(name) is not None


def globalExists(name: str):
    return getGlobal(name) is not None


def isOwnerProgram(program_name: str, user_id: Union[int, str]):
    table.execute("""
    SELECT author FROM "b-star".public."b-star-dev"
    WHERE name = %s;
    """,
                  (program_name,))
    authorID = table.fetchone()
    return str(authorID[0]) == str(user_id)


def isOwnerGlobal(program_name: str, user_id: Union[int, str]):
    table.execute("""
    SELECT owner FROM "b-star".public."b-star-dev-globals"
    WHERE name = %s;
    """,
                  (program_name,))
    authorID = table.fetchone()
    return str(authorID[0]) == str(user_id)


def createTag(user: discord.User, name: str, code: str):
    now = Decimal(time.time())
    table.execute("""
    INSERT INTO "b-star".public."b-star-dev" (name, program, author, uses, created, lastused, lastupdated)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
                  (name, code, user.id, 0, now, now, now))
    conn.commit()


def updateTag(name: str):
    # Assume "name" program exists
    now = Decimal(time.time())
    table.execute("""
    UPDATE "b-star".public."b-star-dev"
    SET uses = uses + 1,
        lastused = %s
    WHERE name = %s
    """,
                  (now, name))


def editTag(name: str, code: str):
    now = Decimal(time.time())
    table.execute("""
    UPDATE "b-star".public."b-star-dev" 
    SET program = %s,
        lastupdated = %s
    WHERE name = %s
    """,
                  (code, now, name))


def deleteTag(name: str):
    table.execute("""
    DELETE FROM "b-star".public."b-star-dev"
    WHERE name = %s
    """,
                  (name,))
    conn.commit()


async def IDtoUser(user_id: int) -> discord.User:
    return await bot.fetch_user(user_id)


async def leaderboards(page: int):
    table.execute("""
    SELECT name,
           uses,
           author,
           created
    FROM "b-star".public."b-star-dev"
    ORDER BY uses DESC
    LIMIT 10
    OFFSET (%s * 10)
    """,
                  (page,))

    results = table.fetchall()
    firststep = []
    for index, tag in enumerate(results):
        firststep.append(
            f"{index + 1} : {tag[0]} :: {tag[1]} uses (written by {(await IDtoUser(tag[2])).name} at {tag[3]} UTC)")
    secondstep = "\n".join(firststep)
    board = f"```{secondstep}```"
    return board


async def infoTag(message, name: str):
    response = getTag(name)
    user = await IDtoUser(response["author"])
    return f"""**{name}** -- by {user.name} -- {response["uses"]} uses
Created on {response["created"]}
Last used on {response["lastused"]}
Updated on {response["lastupdated"]}```scala
{response["program"]}
```"""


def createGlobal(user: discord.User, name: str, code: str):
    table.execute("""
        INSERT INTO "b-star".public."b-star-dev-globals" (name, value, type, owner, version)
        VALUES (%s, %s, %s, %s, %s)
        """,
                  (name, code, 0, user.id, 1))
    conn.commit()


def editGlobal(user: discord.User, name: str, code: str):
    if not isOwnerGlobal(name, user.id):
        return

    global_to_edit = getGlobal(name)
    new_version_number = global_to_edit["version"] + 1

    table.execute("""
        INSERT INTO "b-star".public."b-star-dev-globals" (name, value, type, owner, version)
        VALUES (%s, %s, %s, %s, %s)
        """,
                  (name, code, 0, user.id, new_version_number))
