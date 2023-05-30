# Stupid simple ping module
# Compatible only with linux and macOs!
# Requires a pingPlugin.ini config file with the following structure:
# [Ping]
# HOST = <host_to_ping>

import os


def pluginMain(host = "", messageOnSuccess = False):
    trueHost = ""
    if host is None or host is "":
        import configparser
        if os.path.isfile('auth.ini'):
            configFile = configparser.ConfigParser()
            configFile.read('pingPlugin.ini')
            trueHost = configFile['Ping']['HOST']
        else:
            raise FileNotFoundError('File "pingPlugin.ini" not found! Please create it accordingly to the documentation and rerun the plugin!')
    else:
        trueHost = host
    response = os.system('ping -c 1 ' + trueHost)

    returnMessage = ""
    if response == 0 and messageOnSuccess:
        returnMessage = f"The host {trueHost} is up!"
    elif response != 0:
        returnMessage = f"The host {trueHost} is down!"
    return returnMessage

# Stuff to display if directly run. The initial \033[93m and the final \033[0m are for coloring the string.
if __name__ == "__main__":
    print(f"\033[93mThis is a personalAlerter plugin! Please do not run it directly but import it in personalAlerter.\033[0m")