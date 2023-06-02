# This is a template for a plugin, with the essential functions and the parameters that will be passed from the main program.
# Use it as starting point to develop your plugin.
# Remember: each plugin is stateless, they will run from zero each time. You will have to save your data, if needed,
# inside the plugin folder or somewhere remote. The last run time will be provided as parameter in UTC timezone im the
# following format: "%Y-%m-%dT%H:%M:%S+00:00" .
# If an empty string will be returned at the end of pluginMain, no message will be sent via Telegram.

import datetime


def pluginMain(parametersString : str, longReturnMessage : bool, lastRuntime : datetime.datetime):

    return ''


# Stuff to display if directly run. The initial \033[93m and the final \033[0m are for coloring the string.
if __name__ == "__main__":
    print(f"\033[93mThis is a personalAlerter plugin! Please do not run it directly but import it in personalAlerter.\033[0m")
