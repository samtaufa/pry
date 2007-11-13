from distutils.core import setup

setup(
        name = "pry",
        version = "0.1",
        description = "A unit testing framework and coverage engine.",
        author = "Aldo Cortesi",
        author_email = "aldo@nullcube.com",
        url = "http://www.nullcube.com",
        packages = [
            "libpry",
        ],
        scripts = [
            "pry"
        ]
)
