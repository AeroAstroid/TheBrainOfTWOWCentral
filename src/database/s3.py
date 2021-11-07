import datetime
import os
from typing import Dict, Union

import boto3
import discord
from dotenv import load_dotenv

load_dotenv()
db_name = "b-star"
db = boto3.client(
    "dynamodb",
    aws_access_key_id=os.getenv("DB_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("DB_SECRET_KEY"),
    region_name="eu-west-2"
)

# db = s3.Bucket(db_name)
Response = Dict[str, any]


def getTag(name: str) -> Union[Response, None]:
    response = db.get_item(
        TableName=db_name,
        Key={
            "name": {"S": name}
        }
    )
    try:
        response["Item"]
    except KeyError:
        return None

    return {
        "name": response["Item"]["name"]["S"],
        "ownerID": response["Item"]["ownerID"]["N"],
        "data": response["Item"]["data"]["B"].decode(),
        "creationDate": response["Item"]["creationDate"]["S"],
        "updateDate": response["Item"]["updateDate"]["S"],
        "uses": response["Item"]["uses"]["N"],
    }


def tagExists(name: str):
    return getTag(name) is not None


def isOwner(name: str, id: Union[int, str]):
    return getTag(name)["ownerID"] == str(id)


def createTag(user: discord.User, name: str, code: str):
    db.put_item(
        TableName=db_name,
        Item={
            "name": {"S": name},
            "ownerID": {"N": str(user.id)},
            "data": {"B": code.encode()},
            "creationDate": {"S": str(datetime.datetime.utcnow())},
            "updateDate": {"S": str(datetime.datetime.utcnow())},
            "uses": {"N": str(0)},
        }
    )


def updateTag(name: str):
    db.update_item(
        TableName=db_name,
        Key={
            "name": {"S": name}
        },
        ExpressionAttributeValues={
            ":inc": {"N": str(1)},
        },
        UpdateExpression="ADD uses :inc"
    )


def editTag(name: str, code: str):
    db.update_item(
        TableName=db_name,
        Key={
            "name": {"S": name}
        },
        ExpressionAttributeValues={
            ":code": {"B": code.encode()},
            ":newDate": {"S": str(datetime.datetime.utcnow())},
        },
        ExpressionAttributeNames={
            "#data": "data"
        },
        UpdateExpression="SET #data = :code, updateDate = :newDate",
    )


def deleteTag(name: str):
    db.delete_item(
        TableName=db_name,
        Key={
            "name": {"S": name}
        }
    )


def IDtoUser(message, id: str) -> discord.User:
    return message.guild.get_member(int(id))


def infoTag(message, name: str):
    response = getTag(name)
    user = IDtoUser(message, response["ownerID"])
    return f"""**{name}** -- by {user.name} -- {response["uses"]} uses
Created on {response["creationDate"]}
Updated on {response["updateDate"]}```
{response["data"]}
```"""
