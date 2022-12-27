import os
import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, Union

import discord
# import psycopg2
from dotenv import load_dotenv

from Commands.b_star.bot import bot

load_dotenv()
databaseName = os.environ.get("DATABASE") or "UNKNOWN"
db_name = "\"" + databaseName + "\""
# global conn: psycopg2.connect
# global table: psycopg2._psycopg.connection


# replace with own
def connectToDatabase():
    global conn, table
    # conn = psycopg2.connect(
    #     host=os.environ.get("HOST"),
    #     database=os.environ.get("DATABASE"),
    #     user=os.environ.get("USER"),
    #     password=os.environ.get("PASSWORD")
    # )
    # conn.autocommit = True
    table = conn.cursor()


# tag or global
item = Dict[str, Union[str, int]]



def getTag(name: str) -> Union[item, None]:
    table.execute(f"""
    SELECT * FROM {db_name}.public."b-star-dev"
    WHERE name = (%s)
    """,
                  (name,))
    item = table.fetchone()
    conn.commit()
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
    table.execute(f"""
    SELECT * FROM {db_name}.public."b-star-dev-globals"
    WHERE name = (%s)
    """,
                  (name,))
    item = table.fetchone()
    conn.commit()
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
    table.execute(f"""
    SELECT author FROM {db_name}.public."b-star-dev"
    WHERE name = %s;
    """,
                  (program_name,))
    authorID = table.fetchone()
    return str(authorID[0]) == str(user_id)


def isOwnerGlobal(program_name: str, user_id: Union[int, str]):
    table.execute(f"""
    SELECT owner FROM {db_name}.public."b-star-dev-globals"
    WHERE name = %s;
    """,
                  (program_name,))
    authorID = table.fetchone()
    return str(authorID[0]) == str(user_id)


def createTag(user: discord.User, name: str, code: str):
    now = Decimal(time.time())
    table.execute(f"""
    INSERT INTO {db_name}.public."b-star-dev" (name, program, author, uses, created, lastused, lastupdated)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
                  (name, code, user.id, 0, now, now, now))
    conn.commit()


def updateTag(name: str):
    # Assume "name" program exists
    now = Decimal(time.time())
    table.execute(f"""
    UPDATE {db_name}.public."b-star-dev"
    SET uses = uses + 1,
        lastused = %s
    WHERE name = %s
    """,
                  (now, name))
    conn.commit()


def editTag(name: str, code: str):
    now = Decimal(time.time())
    table.execute(f"""
    UPDATE {db_name}.public."b-star-dev" 
    SET program = %s,
        lastupdated = %s
    WHERE name = %s
    """,
                  (code, now, name))
    conn.commit()


def deleteTag(name: str):
    table.execute(f"""
    DELETE FROM {db_name}.public."b-star-dev"
    WHERE name = %s
    """,
                  (name,))
    conn.commit()


def unixToReadable(unix: int):
    return datetime.utcfromtimestamp(unix).strftime("%Y-%m-%d %H:%M:%S UTC")


async def IDtoUser(user_id: int) -> discord.User:
    return await bot.fetch_user(user_id)


async def leaderboards(page: int):
    table.execute(f"""
    SELECT name,
           uses,
           author,
           created
    FROM {db_name}.public."b-star-dev"
    ORDER BY uses DESC
    LIMIT 10
    OFFSET (%s * 10)
    """,
                  (page,))

    results = table.fetchall()
    firststep = []
    for index, tag in enumerate(results):
        firststep.append(
            f"{index + 1} : {tag[0]} :: {tag[1]} uses (written by {(await IDtoUser(tag[2])).name} at {unixToReadable(tag[3])})")
    secondstep = "\n".join(firststep)
    board = f"```{secondstep}```"
    return board


async def infoTag(name: str):
    response = getTag(name)
    user = await IDtoUser(response["author"])
    return f"""**{name}** -- by {user.name} -- {response["uses"]} uses
Created on {unixToReadable(response["created"])}
Last used on {unixToReadable(response["lastused"])}
Updated on {unixToReadable(response["lastupdated"])}```scala
{response["program"]}
```"""


def createGlobal(user: discord.User, name: str, code: str):
    table.execute(f"""
        INSERT INTO {db_name}.public."b-star-dev-globals" (name, value, type, owner, version)
        VALUES (%s, %s, %s, %s, %s)
        """,
                  (name, code, 0, user.id, 1))
    conn.commit()


def editGlobal(user: discord.User, name: str, code: str):
    if not isOwnerGlobal(name, user.id):
        return

    global_to_edit = getGlobal(name)
    new_version_number = global_to_edit["version"] + 1

    table.execute(f"""
        UPDATE {db_name}.public."b-star-dev-globals"
        SET value = %s,
            version = %s
        WHERE name = %s
        """,
                  (code, new_version_number, name))
    conn.commit()


def fileLimitCheck(file):
    return len(file) > 150_000  # 150kb
