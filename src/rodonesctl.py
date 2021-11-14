#!/usr/bin/env python3

import docker
from os import getuid, getgid
from os.path import join
import sys

client = docker.from_env()


WORKSPACE_DIR = "/home/rodones/workspace"
# WORKSPACE_DIR = "/home/gokberk/Desktop/Rodones/workspace/"


def run():
    env = ["WORKSPACE_NAME=test"]
    with open(join(WORKSPACE_DIR, ".env")) as f:
        env.extend(f.readlines())

    client.containers.run(
        "rodones/colmap:test",
        "test_ok",
        detach=True,
        privileged=True,
        volumes=[f"{join(WORKSPACE_DIR, 'data', 'test')}:/working",
                 f"{join(WORKSPACE_DIR, 'docker', 'colmap', 'scripts')}:/scripts"],
        working_dir="/working",
        environment=env,
        user=f'{getuid()}:{getgid()}',
    )


def get():
    container = client.containers.list()[0]
    keywords = ["Registering", "Image sees", "Matching"]

    chunk = bytearray()
    for data in container.logs(stream=True, tail=1000):
        if data == b'\n':
            line = chunk.decode("utf-8").strip()
            if any(map(lambda kw: kw in line, keywords)):
                print(line)
            chunk = bytearray()
        else:
            chunk.extend(data)

    result = container.wait()
    container.remove()
    print(result)


if len(sys.argv) > 1 and sys.argv[1] == "get":
    get()
else:
    run()
