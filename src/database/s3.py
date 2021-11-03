import datetime
from typing import Dict

import boto3
import discord

db_name = "b-star"
s3 = boto3.client("s3")


# db = s3.Bucket(db_name)
Response = Dict[str, any]


def createTag(user: discord.User, name: str, code: str):
    s3.put_object(
        Bucket=db_name,
        Key=name,
        Body=code.encode(),
        Metadata={
            "ownerid": str(user.id),
            "creationdate": str(datetime.datetime.utcnow()),
            "updatedate": str(datetime.datetime.utcnow())
        }
    )


def getTag(name: str) -> Response:
    response = s3.get_object(Bucket=db_name, Key=name)
    return {
        "body": response["Body"].read().decode(),
        "meta": response["Metadata"]
    }


def tagExists(name: str):
    print("WIP")


def IDtoUser(message, id: str) -> discord.User:
    return message.guild.get_member(int(id))


def infoTag(message, name: str):
    response = getTag(name)
    print(response["meta"])
    user = IDtoUser(message, response["meta"]["ownerid"])
    return f"""**{name}** -- by {user.name} -- -999 uses
Created on {response["meta"]["creationdate"]}```
{response["body"]}
```"""
