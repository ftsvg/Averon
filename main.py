from config import Client, Settings


Settings.validate()

if __name__ == '__main__':
    Client().run(Settings.TOKEN)