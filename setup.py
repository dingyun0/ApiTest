from setuptools import setup, find_packages

setup(
    name="text_to_video",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
    ],
) 