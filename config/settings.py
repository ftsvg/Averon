from os import getenv
from dotenv import load_dotenv

load_dotenv()

from content import SETTINGS_ERRORS


class Settings:
    TOKEN: str = getenv("TOKEN")

    @classmethod
    def validate(cls) -> None:
        if not cls.TOKEN:
            raise RuntimeError(SETTINGS_ERRORS['missing_token']['message'])