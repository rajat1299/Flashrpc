import pytest

from pydantic import BaseModel, validator, ValidationError

from fasterpc.schemas import RpcRequest



# 1. Define a model with a validator

class ValidatedArgs(BaseModel):

    age: int



    @validator('age')

    def check_age(cls, v):

        if v < 0:

            raise ValueError('must be positive')

        return v



def test_validation():

    # Valid case

    m = ValidatedArgs(age=10)

    assert m.age == 10



    # Invalid case - this confirms Pydantic is enforcing rules

    with pytest.raises(ValidationError):

        ValidatedArgs(age=-1)



if __name__ == "__main__":

    test_validation()

    print("✅ Pydantic Validator Test Passed")
