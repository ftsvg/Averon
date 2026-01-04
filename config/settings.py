from os import getenv
from dotenv import load_dotenv

load_dotenv()

from content import SETTINGS_ERRORS


class Settings:
    TOKEN: str = getenv("TOKEN")
    DBUSER: str = getenv("DBUSER")
    DBPASS: str = getenv("DBPASS")
    DBNAME: str = getenv("DBNAME")
    DBENDPOINT: str = getenv("DBENDPOINT")

    @classmethod
    def validate(cls) -> None:
        if not cls.TOKEN:
            raise RuntimeError(SETTINGS_ERRORS['missing_token']['message'])
        
        if not all([cls.DBUSER, cls.DBPASS, cls.DBNAME, cls.DBENDPOINT]):
            raise RuntimeError(SETTINGS_ERRORS["missing_database_credentials"]["message"])