import json
import random
import string
from datetime import timedelta

from user.models import Satellite


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def start_import():
    with open("tmp/default_satellites.json", "r") as file:
        data = json.load(file)

    satellites = data["satellites"]
    for satellite in satellites:
        username = get_random_string(5)
        Satellite.objects.create(
            **{
                **satellite,
                "interval": timedelta(seconds=satellite["interval"]),
                "system": True,
                "allow_auth": False,
                "username": username,
                "password": username,
                "is_original": True,
            }
        )


def main():
    start_import()
