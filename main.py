from config import Settings, Client


Settings.validate()

if __name__ == '__main__':
    Client().run(Settings.TOKEN)