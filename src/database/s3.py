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
    host="localhost",
    database="b-star",
    user="postgres",
    password="password"
)

tag = Dict[str, Union[str, int]]

table = conn.cursor()


def getTag(name: str) -> Union[tag, None]:
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


def tagExists(name: str):
    return getTag(name) is not None


def isOwner(program_name: str, id: Union[int, str]):
    table.execute("""
    SELECT author FROM "b-star".public."b-star-dev"
    WHERE name = %s;
    """,
                  (program_name,))
    authorID = table.fetchone()
    return str(authorID[0]) == str(id)


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


async def IDtoUser(id: int) -> discord.User:
    return await bot.fetch_user(id)


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
        firststep.append(f"{index + 1} : {tag[0]} :: {tag[1]} uses (written by {(await IDtoUser(tag[2])).name} at {tag[3]} UTC)")
    secondstep = "\n".join(firststep)
    board = f"```{secondstep}```"
    return board


def infoTag(message, name: str):
    response = getTag(name)
    user = IDtoUser(response["author"])
    return f"""**{name}** -- by {user.name} -- {response["uses"]} uses
Created on {response["created"]}
Last used on {response["lastused"]}
Updated on {response["lastupdated"]}```
{response["program"]}
```"""
