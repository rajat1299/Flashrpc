from setuptools import setup, find_packages



with open("requirements.txt") as fp:

    install_requires = [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]

setup(

    name="fasterpc",

    version="0.1.0",

    author="Your Name",

    description="A fast and durable bidirectional JSON RPC channel over websockets and fastapi.",

    packages=find_packages(),

    classifiers=[

        "Programming Language :: Python :: 3",

        "Operating System :: OS Independent",

    ],

    python_requires=">=3.9",

    install_requires=install_requires,

)

