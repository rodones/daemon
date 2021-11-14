#!/usr/bin/env python3

from functools import reduce
import docker
import docker.types
from os import getuid, getgid
from os.path import join
from sys import exit, argv
from signal import signal, SIGINT


client = docker.from_env()

WORKSPACE_DIR = "/home/rodones/workspace"
# WORKSPACE_DIR = "/home/gokberk/Desktop/Rodones/workspace/"


def run(working, *cmd):
    env = [f"WORKSPACE_NAME={working}"]
    with open(join(WORKSPACE_DIR, ".env")) as f:
        env.extend(map(
            lambda line: line.strip(),
            filter(lambda line: not line.startswith("#"), f.readlines())
        ))

    container = client.containers.run(
        "rodones/colmap:gpu-latest",
        cmd,
        detach=True,
        privileged=True,
        device_requests=[
            docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
        ],
        volumes=[f"{join(WORKSPACE_DIR, 'data', working)}:/working",
                 f"{join(WORKSPACE_DIR, 'docker', 'colmap', 'scripts')}:/scripts",
                 f"{join(WORKSPACE_DIR, 'docker', 'colmap', 'vocab-trees')}:/vocab-trees"],
        working_dir="/working",
        environment=env,
        user=f'{getuid()}:{getgid()}',
    )

    print("NAME".ljust(20), "COMMAND".ljust(30), "CREATED", sep=" ")
    name = container.attrs["Name"][1:]
    cmd = " ".join(container.attrs["Config"]["Cmd"])[:30]
    created = container.attrs["Created"].split(".")[0].replace("T", " ")
    print(name.ljust(20), cmd.ljust(30), created, sep=" ")


def logs():
    signal(SIGINT, lambda x, y: exit(0))

    container = client.containers.list()[0]
    keywords = ["Registering", "Image sees", "Matching", "Processed file"]

    chunk = bytearray()
    for data in container.logs(stream=True, tail=1000):
        if len(data) == 1:
            if data == b'\n':
                line = chunk.decode("utf-8").strip()
                if any(map(lambda kw: kw in line, keywords)):
                    print(line)
                chunk = bytearray()
            else:
                chunk.extend(data)
        else:
            line = data.decode("utf-8").strip()
            if any(map(lambda kw: kw in line, keywords)):
                print(line)
    result = container.wait()
    container.remove()
    print(result)


def get_rodones_containers():
    return list(filter(
        lambda container: any(map(lambda tag: tag.startswith("rodones"), container.image.tags)),
        client.containers.list()
    ))


def ls():
    containers = get_rodones_containers()

    def get_name(container): return container.attrs["Name"][1:]
    def get_cmd(container): return " ".join(container.attrs["Config"]["Cmd"])
    def get_created(container): return container.attrs["Created"].split(".")[0].replace("T", " ")
    column_lenses = [get_name, get_cmd]

    max_lengths = tuple(
        reduce(
            lambda curr, acc: tuple(map(min, zip(curr, acc))),
            map(
                lambda container: map(lambda method: len(method(container)), column_lenses),
                containers
            )
        )
    )
    print("#".ljust(2), "NAME".ljust(max_lengths[0]), "COMMAND".ljust(max_lengths[1]), "CREATED", sep="  ")
    for id, container in enumerate(containers):
        name = get_name(container)
        cmd = get_cmd(container)
        created = get_created(container)
        print(str(id).ljust(2), name.ljust(max_lengths[0]), cmd.ljust(max_lengths[1]), created, sep="  ")


if len(argv) > 1:
    globals()[argv[1]](*argv[2:])
