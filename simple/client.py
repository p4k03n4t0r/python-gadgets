#!/usr/bin/env python3

import sys
import json
import asyncio
import importlib

# from sqlalchemy import *


class UpperException:
    def __init__(self, e):
        self.message = repr(e)


class UpperRequest:
    def __init__(self, text):
        self.text = text


class UpperReply:
    pass


def object_to_dict(c):
    res = {}
    res["__class__"] = str(c.__class__.__name__)
    res["__module__"] = str(c.__module__)
    res.update(c.__dict__)
    return res


def dict_to_object(d):
    if "__class__" in d:
        class_name = d.pop("__class__")
        module_name = d.pop("__module__")
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)

        inst = class_.__new__(class_)
        inst.__dict__.update(d)
    else:
        inst = d

    return inst


async def rpc_client(message):
    message = json.dumps(message, default=object_to_dict)

    reader, writer = await asyncio.open_connection(sys.argv[1], int(sys.argv[2]))
    writer.write(message.encode())
    data = await reader.read(2000)
    writer.close()

    res = json.loads(data, object_hook=dict_to_object)
    if isinstance(res, UpperException):
        print("Exception: " + res.message)
        exit(1)

    return res


loop = asyncio.get_event_loop()
req = UpperRequest("hello")
res = loop.run_until_complete(rpc_client(req))

print("\nResult :\n" + res.result)

loop.close()
