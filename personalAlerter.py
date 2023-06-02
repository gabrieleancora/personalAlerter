import importlib
import requests
import os
import configparser
from time import sleep
from datetime import datetime, timezone
from multiprocessing import Process

DEBUG = False

# TELEGRAM VARIABLES DO NOT TOUCH, USE THE CONFIG FILE INSTEAD
TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHANNEL_ID = ''
REFRESH_TIME_MINUTES = 0
LASTRUNTIME = ''

def mainLoop():
    BACKOFF_RETRIES = 0

    # Gets last runtime if available and replaces default value. Prints it for debug purposes
    lastRuntime = datetime.fromisoformat('2000-01-01T00:00:00+00:00')
    if LASTRUNTIME != '':
        lastRuntime = datetime.fromisoformat(LASTRUNTIME)
    if DEBUG:
        consolePrint('lastruntime: ' + str(lastRuntime))

    while True:
        try:
            consolePrint("Starting main loop...")
            # Alerts the user if the bot wasn't online for any number of loops
            if BACKOFF_RETRIES > 0:
                consolePrint(f"Sending a message to the Telegram channel to inform that the bot is back online.\nIt was offline for {BACKOFF_RETRIES} loops.")
                send_tg_message(f"The bot couldn't perfrom any network related checks or send messages using Telegram for {BACKOFF_RETRIES} times because of connection problems.")
                BACKOFF_RETRIES = 0

            if os.path.isfile('pluginList.cfg'):
                pluginList = []
                with open('pluginList.cfg', 'r') as pluginListFile:
                    fileLines = pluginListFile.readlines()
                    # Remove comments and empty lines
                    pluginLines = [x for x in fileLines if not x.startswith('#')]
                    pluginLines = [x.strip() for x in pluginLines if x.strip()]

                    # For each plugin checks if the optional arguments are available and saves them.
                    # If no args are avaialble the default values will be used (False, empty additional args)
                    for pluginStr in pluginLines:
                        splittedCfg = pluginStr.split(',')
                        if len(splittedCfg) > 0:
                            pluginToBeAdded = []
                            # Creates a new plugin "list" with the plugin name, the bool indicating if it's a rich message
                            # (if not provided in the pluginList.cfg False will be provided) and the optional parameters string
                            # (if not provided in the pluginList.cfg an empty string will be provided).
                            pluginToBeAdded.append(splittedCfg[0])
                            try:
                                if splittedCfg[1].lower() == 'true':
                                    pluginToBeAdded.append(True)
                                else:
                                    pluginToBeAdded.append(False)
                            except IndexError:
                                pluginToBeAdded.append(False)
                            try:
                                if len(splittedCfg[2].strip()) > 0:
                                    pluginToBeAdded.append(splittedCfg[2].strip())
                                else:
                                    pluginToBeAdded.append("")
                            except IndexError:
                                pluginToBeAdded.append("")

                            pluginList.append(pluginToBeAdded)

                if DEBUG:
                    consolePrint(f"Finished checking the plugin list. Running them now. Found {len(pluginList)} plugins.")

                for plugin in pluginList:
                    if DEBUG:
                        consolePrint(f"Plugin: {plugin[0]}, richPrint: {plugin[1]}, argc: {plugin[2]}. ")

                    richResponse = plugin[1]
                    pluginFullName = 'plugins.' + plugin[0]

                    # Loads the plugin and executes it using the args passed from the file cfg
                    pluginLib = importlib.import_module(pluginFullName, "plugins")
                    response = pluginLib.pluginMain(plugin[2], richResponse, lastRuntime)
                    del pluginLib
                    if richResponse == True:
                        for msg in response:
                            send_tg_message(msg, True)
                    else:
                        for msg in response:
                            send_tg_message(msg)

            lastRuntime = datetime.now(timezone.utc)

            # Saves last runtime
            timeConfig = configparser.ConfigParser()
            timeConfig.read('config.ini')
            timeConfig['Main']['LASTRUNTIME'] = lastRuntime.isoformat()
            with open('config.ini', 'w') as cfgWriter:
                timeConfig.write(cfgWriter)
            sleep(REFRESH_TIME_MINUTES * 60)

        # Network related execptions and file not found execptions doesn't stop the loop from running since they
        # are only blocking the sending of messages to the chat.
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as networkExceptionObj:
            consolePrint(f"There was a connection error, retrying after {REFRESH_TIME_MINUTES} minutes.")
            consolePrint("The exception was: " + str(networkExceptionObj))
            BACKOFF_RETRIES += 1
        except FileNotFoundError as fileNotFoundExceptionObj:
            consolePrint("There was a file exception:\n" + str(fileNotFoundExceptionObj))
            send_tg_message("The bot had a problem and didn't find a file, probably a missing configuration file from a plugin?"
                            "\nPlease check the console for more informations about the error."
                            "\nThis error doesn't stop the main loop.")
        except Exception as genericExceptionObj:
            consolePrint("There was an exception:\n" + str(genericExceptionObj), "error")
            send_tg_message("The bot had a problem and possibly crashed. Please check the console for more informations about the error.")
            exit(1)
        finally:
            consolePrint("Ending loop...")


# Send a message using Telegram web API after replacing some unsafe characters. Also splits the message if necessary.
def send_tg_message(message : str, markdown = False):
    # Replace URL unsafe characters
    message = message.replace("%", "%25")
    message = message.replace("&", "%26")
    message = message.replace("<", "%3C")
    message = message.replace(">", "%3E")
    apend = ""
    if markdown == True:
        apend = "&parse_mode=Markdown"

    # cut the message string every 4000 chars to comply with Telegram message length limitations (4096 chars after parsing)
    cuttedMsg = message[0:4000]
    while len(message) > 0:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHANNEL_ID}&text={cuttedMsg}{apend}")
        message = message[4000:]
        cuttedMsg = message[0:4000]


# To print messages on the stdout with a timestamp, useful for logging.
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
    print(header + message + tail, flush=True)


# Code executed at the beginning to initalize the parameters and to start the main loop.
if __name__ == "__main__":
    # Check for config file and loads it
    if os.path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        TELEGRAM_BOT_TOKEN = config['Telegram']['TG_BOT_TOKEN']
        TELEGRAM_CHANNEL_ID = config['Telegram']['TG_CHANNEL_ID']
        mainConfig = config['Main']
        LASTRUNTIME = mainConfig.get('LASTRUNTIME', '')
        REFRESH_TIME_MINUTES = mainConfig.getint('REFRESH_TIME_MINUTES')
        if TELEGRAM_BOT_TOKEN == "" or TELEGRAM_CHANNEL_ID == "":
            consolePrint("Please fill all the required informations to make the bot work!", "error")
            exit(1)
        if not os.path.isfile('pluginList.cfg'):
            consolePrint("Please create a pluginList.cfg file contaning the list of plugins to be executed! See the documentation on github for more info.", "error")
            exit(1)
        consolePrint("Program initialized, starting the main loop.", "header")

        # Saves last runtime
        newLastruntime = datetime.now(timezone.utc).isoformat()
        config['Main']['LASTRUNTIME'] = newLastruntime
        with open('config.ini', 'w') as cfgWriter:
            config.write(cfgWriter)

        # Sending a message to the Telegram channel to inform that the bot has started.
        # In case of no connection, the bot will start anyway without sending the message.
        try:
            send_tg_message(f"PersonalAlerter initialized successfully!\nThe refresh interval is currently set at {REFRESH_TIME_MINUTES} minutes.")
        except Exception as e:
            consolePrint(f"There was an error while sending the initialization message to the Telegram channel: {e}", "warning")
            consolePrint("The bot will continue to run, but the initialization message won't be sent.", "warning")
        mainProcess = Process(target=mainLoop, name="Main loop process")
        mainProcess.start()
        consolePrint(f"The bot will check for new modules once every run.")

        # The "main" loop
        while(True):
            inputCommand = input()
            if inputCommand == "exit":
                consolePrint("Closing the main program...")
                if mainProcess.is_alive():
                    mainProcess.terminate()
                exit(0)
            elif inputCommand == "status":
                consolePrint(f"The main process is{('' if mainProcess.is_alive() else ' not')} alive.\nThe current exit code is {mainProcess.exitcode}\nDebug mode is {'enabled' if DEBUG else 'disabled'}.")
            elif inputCommand == "debug":
                DEBUG = not DEBUG
                consolePrint(f"Toggled debug mode. Debug mode is now {'Active' if DEBUG else 'Deactivated'}.")
            elif inputCommand == "help":
                consolePrint("Available commands:\nstatus = prints main loop status\ndebug = toggles debug mode\nexit = exit the program")

    else:
        consolePrint("Error: the file config.ini wasn't found. Please insert all the required fields and rerun the program.", "error")
        with open('config.ini', 'w') as f:
            f.write("[Main]\nREFRESH_TIME_MINUTES = \n\n[Telegram]\nTG_BOT_TOKEN = \nTG_CHANNEL_ID = \n")
