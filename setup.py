import sys

from setuptools import setup

_ = setup(
    name="beets-disccrusher",
    version="0.1",
    description="beets plugin to crush discs for specified media types to single disc.",
    author="Henry Oberholtzer",
    license="MIT",
    platforms="ALL",
    packages=["beetsplug"],
    install_requires=[
        "beets>=2.5.1",
        "typing-extensions" if sys.version_info < (3, 12) else "",
    ],
    python_requires=">=3.10"
)
