from setuptools import setup, find_packages

setup(
    name="BoAmps-Carbon",
    version="0.1.0",
    description="Track emissions and system usage during training.",
    packages=find_packages(),
    install_requires=[
        "torch",
        "codecarbon",
        "psutil",
        "requests",
    ],
    python_requires=">=3.6",
)
