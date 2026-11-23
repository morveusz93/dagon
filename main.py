import logging

from config import DISCORD_TOKEN
from dagon import Dagon


def main():
    Dagon().run(DISCORD_TOKEN, log_level=logging.INFO, root_logger=True)


if __name__ == "__main__":
    main()
