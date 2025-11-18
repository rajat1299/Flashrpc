import os

import uuid

from random import SystemRandom

import pydantic

from packaging import version



class RandomUtils(object):

    @staticmethod

    def gen_uid():

        return uuid.uuid4().hex



    @staticmethod

    def gen_token(size=256):

        if size % 2 != 0:

            raise ValueError("Size in bits must be an even number.")

        return (

            uuid.UUID(int=SystemRandom().getrandbits(size / 2)).hex

            + uuid.UUID(int=SystemRandom().getrandbits(size / 2)).hex

        )



gen_uid = RandomUtils.gen_uid

gen_token = RandomUtils.gen_token



def is_pydantic_pre_v2():

    return version.parse(pydantic.VERSION) < version.parse("2.0.0")



def pydantic_serialize(model, **kwargs):

    if is_pydantic_pre_v2():

        return model.json(**kwargs)

    else:

        return model.model_dump_json(**kwargs)



def pydantic_parse(model, data, **kwargs):

    if is_pydantic_pre_v2():

        return model.parse_obj(data, **kwargs)

    else:

        return model.model_validate(data, **kwargs)

