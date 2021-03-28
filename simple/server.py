#!/usr/bin/env python3

import json
import asyncio
import multiprocessing
import importlib
import socket


class UpperException:
    def __init__(self, e):
        self.message = repr(e)


class UpperRequest:
    def __init__(self, text):
        self.text = text


class UpperReply:
    def __init__(self, text):
        self.result = text


def dict_to_object(d):
    if "__class__" in d:
        class_name = d.pop("__class__")
        module_name = d.pop("__module__")
        # if module_name not in ["__main__"]:
        #     raise ModuleNotFoundError(f"I can't use the classes from {module_name}")

        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)

        obj = class_.__new__(class_)
        obj.__dict__.update(d)
    else:
        obj = d

    return obj


def object_to_dict(o):
    res = {}
    res["__class__"] = str(o.__class__.__name__)
    res["__module__"] = (
        "__main__" if str(o.__module__) == "__mp_main__" else str(o.__module__)
    )
    res.update(o.__dict__)
    return res


async def handle_client(client, loop):

    try:
        dat = await loop.sock_recv(client, 2000)
        obj = json.loads(dat, object_hook=dict_to_object)

        if isinstance(obj, UpperRequest):
            text = obj.text.upper()
            # text = obj.text.capatalize("upper")
            response = UpperReply(text)
        else:
            response = UpperException("unknown message")

    except Exception as e:
        response = UpperException(e)
        print(e)

    response = json.dumps(response, default=object_to_dict).encode("ascii")
    await loop.sock_sendall(client, response)
    client.shutdown(socket.SHUT_RDWR)


def run_server(client):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handle_client(client, loop))


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 8081))
    server.listen(1)

    while True:
        client, address = server.accept()

        process = multiprocessing.Process(target=run_server, args=(client,))
        process.daemon = True
        process.start()
