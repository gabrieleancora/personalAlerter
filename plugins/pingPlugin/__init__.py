# Simple ping plugin for personalAlterter
# Compatible only with linux and macOs!
# Requires a pingPlugin.ini config file with the following structure:
# [Ping]
# HOST = <host_to_ping>
import datetime
import os
import pathlib


def pluginMain(host : str, longReturnMessage : bool, lastRuntime : datetime.datetime):
    trueHost = ""
    myPath = pathlib.Path(__file__).parent
    if host is None or host == "":
        import configparser
        configPath = os.path.join(myPath, 'pingPlugin.ini')
        if os.path.isfile(configPath):
            configFile = configparser.ConfigParser()
            configFile.read(configPath)
            trueHost = configFile['Ping']['HOST']
        else:
            raise FileNotFoundError('File "pingPlugin.ini" not found! Please create it accordingly to the documentation and rerun the plugin!')
    else:
        trueHost = host
    response = os.system('ping -c 1 ' + trueHost + ' > /dev/null 2>&1')

    returnMessage = []
    if response == 0:
        if longReturnMessage:
            returnMessage.append(f"The host {trueHost} is up!")
        else:
            returnMessage.append("0")
    elif response != 0:
        if longReturnMessage:
            returnMessage.append(f"The host {trueHost} is down!")
        else:
            returnMessage.append("1")
    return returnMessage


# Stuff to display if directly run. The initial \033[93m and the final \033[0m are for coloring the string.
if __name__ == "__main__":
    print(f"\033[93mThis is a personalAlerter plugin! Please do not run it directly but import it in personalAlerter.\033[0m")