#!/usr/bin/env python3

import json
import asyncio
import multiprocessing
import importlib
import socket

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy import and_
from sqlalchemy.sql import select

FIREWORKS = """
                          ,
                       \  :  /
                    `. __/ \__ .'
                    _ _\     /_ _
                       /_   _\\
                     .'  \ /  `.
                       /  :  \\
                          '
          ,                               ,
       \  :  /                         \  :  /
    `. __/ \__ .'                   `. __/ \__ .'
    _ _\     /_ _                   _ _\     /_ _
       /_   _\                         /_   _\\
     .'  \ /  `.                     .'  \ /  `.
       /  :  \                         /  :  \\
          '                               '
"""

EXPLOSION = """
                                 :
                       !H.     :H       .:          :
                       .H.     ! .                 :
                .        oH.  oo ooo.. :
                 !!..    ooooooooooooHH.     !.:
  :                 H:ooooooooooooooooo  :.H                   .
         ..     .   .oooooooooooooooooo.:oH:.
            :.! . .oooooooooooooooooooooo!::!   .  .: :
               .: oooooooooooooooooooIooo! :!!:::
                 oooooooooooooooMooooooooHH!H:
                .ooooooooooooooooooooOII!! !o o
   :  :  :  H   IooooooooooooooWoooooMoHoIoH!.:H! .::          .   .
                 ooooooooooooooooooOooOH!!oH: ...
                  .oooooooHoooOoooOooIoooHHIH:.
                .H .::oo!ooIIOOOooIoIIoH!.::::I.: .
            .   .    :o:Ooo:HOoHIIHHoHHoIH::  . . .!.
     .            . .!H!: oHI!o!oooooo!!oHH..         :!   .
                   : !.  .:.H.:!:!!.!H: ...H               .
                 ! .    .!:   :: ::  !H     .:..
                                H.       .
                               :
"""

engine = create_engine("sqlite:///:memory:", echo=False)
metadata = MetaData()

recipes = Table(
    "recipes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("material1", String),
    Column("material2", String),
    Column("result", String),
)
metadata.create_all(engine)

conn = engine.connect()
conn.execute(
    recipes.insert(),
    [
        {
            "id": 0,
            "material1": "sparkling powder",
            "material2": "red dye",
            "result": "Red fireworks are surely look nice, but please launch it outside.\033[0;31m"
            + FIREWORKS
            + "\033[0m",
        },
        {
            "id": 1,
            "material1": "sparkling powder",
            "material2": "green dye",
            "result": "Green fireworks are surely look nice, but please launch it outside.\033[0;32m"
            + FIREWORKS
            + "\033[0m",
        },
        {
            "id": 2,
            "material1": "sparkling powder",
            "material2": "blue dye",
            "result": "Blue fireworks are surely look nice, but please launch it outside.\033[0;34m"
            + FIREWORKS
            + "\033[0m",
        },
        {
            "id": 3,
            "material1": "explosive powder",
            "material2": "red dye",
            "result": "As soon as you crafted item, you saw a bright red explosion, powerfull enough to kick you out of the store.\033[0;31m"
            + EXPLOSION
            + "\033[0m",
        },
        {
            "id": 4,
            "material1": "explosive powder",
            "material2": "green dye",
            "result": "As soon as you crafted item, you saw a bright green explosion, powerfull enough to kick you out of the store.\033[0;32m"
            + EXPLOSION
            + "\033[0m",
        },
        {
            "id": 5,
            "material1": "explosive powder",
            "material2": "blue dye",
            "result": "As soon as you crafted item, you saw a bright blue explosion, powerfull enough to kick you out of the store.\033[0;34m"
            + EXPLOSION
            + "\033[0m",
        },
    ],
)


class AtelierException:
    def __init__(self, e):
        self.message = repr(e)


class MaterialRequest:
    pass


class MaterialRequestReply:
    def __init__(self):
        self.material1 = list(
            set([i[0] for i in conn.execute(select([recipes.c.material1]))])
        )
        self.material2 = list(
            set([i[0] for i in conn.execute(select([recipes.c.material2]))])
        )


class RecipeCreateRequest:
    def __init__(self, materials):
        self.materials = materials


class RecipeCreateReply:
    def __init__(self, m1, m2):
        query = select([recipes.c.result]).where(
            and_(recipes.c.material1 == m1, recipes.c.material2 == m2)
        )
        result = conn.execute(query).fetchone()[0]
        self.result = result


def dict_to_object(d):
    if "__class__" in d:
        class_name = d.pop("__class__")
        module_name = d.pop("__module__")
        if (module_name not in ["__main__"]) and (
            not module_name.startswith("sqlalchemy")
        ):
            # no unintended solutions plz
            raise ModuleNotFoundError(f"No module named {module_name}")

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

        if isinstance(obj, MaterialRequest):
            response = MaterialRequestReply()
        elif isinstance(obj, RecipeCreateRequest):
            materials = obj.materials.split(",")
            response = RecipeCreateReply(materials[0], materials[1])
        else:
            response = AtelierException("unknown message")

    except Exception as e:
        response = AtelierException(e)
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
