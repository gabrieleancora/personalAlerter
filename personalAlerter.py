import requests
import os
import configparser
from time import sleep
from datetime import datetime
from multiprocessing import Process

### Importlib usage
# miaLibreria = importlib.import_module('fileSenzaPy')
# miaLibreria.funzione(<parametri>)
# del miaLibreria
# sys.modules.pop('fileSenzaPy')


# TELEGRAM VARIABLES DO NOT TOUCH, USE THE CONFIG FILE INSTEAD
TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHANNEL_ID = ''
REFRESH_TIME_MINUTES = 0

def loop():
    BACKOFF_RETRIES = 0
    timePassed = 0
    while True:
        try:
            print("Doing things...")
            if BACKOFF_RETRIES > 0:
                consolePrint(f"Sending a message to the Telegram channel to inform that the bot is back online.\nIt was offline for {BACKOFF_RETRIES} checks.")
                send_tg_message(f"The bot couldn't check for new manga for {BACKOFF_RETRIES} times because of connection problems.")
                BACKOFF_RETRIES = 0
            while timePassed < (REFRESH_TIME_MINUTES * 60):
                print("Fake checking modules")
                timePassed = timePassed + 10
                sleep(10)
        except Exception as e:
            consolePrint("There was an exception:\n" + str(e), "error")
            send_tg_message("The bot crashed, please check the console for more informations about the error.")
            exit(1)
        finally:
            print("Closing now...")
    

def send_tg_message(message, markdown = False):
    message = message.replace("%", "%25")
    message = message.replace("&", "%26")
    message = message.replace("<", "%3C")
    message = message.replace(">", "%3E")
    apend = ""
    if markdown == True:
        apend = "&parse_mode=Markdown"
    response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHANNEL_ID}&text={message}{apend}")
    


def consolePrint(message: str, type = ""):
    header = ""
    tail = ""
    if type == "error":
        header = "\033[91m"
        tail = "\033[0m"
    elif type == "warning":
        header = "\033[93m"
        tail = "\033[0m"
    elif type == "header":
        header = "\033[95m"
        tail = "\033[0m"
    header = header + "[" + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "] "
    print(header + message + tail)

if __name__ == "__main__":
    # Check for config file and loads it
    if os.path.isfile('auth.ini'):
        config = configparser.ConfigParser()
        config.read('auth.ini')
        TELEGRAM_BOT_TOKEN = config['Telegram']['TG_BOT_TOKEN']
        TELEGRAM_CHANNEL_ID = config['Telegram']['TG_CHANNEL_ID']
        REFRESH_TIME_MINUTES = config.getint('Main', 'REFRESH_TIME_MINUTES')
        if TELEGRAM_BOT_TOKEN == "" or TELEGRAM_CHANNEL_ID == "":
            consolePrint("Please fill all the required informations to make the bot work!", "error")
            exit(1)
        consolePrint("Program initialized, starting the main loop.", "header")
        # Sending a message to the Telegram channel to inform that the bot has started.
        # In case of no connection, the bot will start anyway without sending the message.
        try:
            send_tg_message(f"Bot initialized successfully!\nThe refresh interval is currently set at {REFRESH_TIME_MINUTES} minutes.")
        except Exception as e:
            consolePrint(f"There was an error while sending the initialization message to the Telegram channel: {e}", "warning")
            consolePrint("The bot will continue to run, but the initialization message won't be sent.", "warning")
        mainProcess = Process(target=loop, name="Main loop process")
        mainProcess.start()
        consolePrint(f"Sleeping for {REFRESH_TIME_MINUTES} mins.\nThe bot will check for new modules once every 10 seconds.")
        # The "main" loop
        while(True):
            inputCommand = input()
            if inputCommand == "quit":
                consolePrint("Closing the main program...")
                mainProcess.terminate()
                exit(0)
            
    else:
        consolePrint("Error: the file auth.ini wasn't found. Please insert all the required fields and rerun the program.", "error")
        with open('auth.ini', 'w') as f:
            f.write("[Main]\nREFRESH_TIME_MINUTES = \n\n[Telegram]\nTG_BOT_TOKEN = \nTG_CHANNEL_ID = \n")
