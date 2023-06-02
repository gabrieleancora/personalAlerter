# personalAlerter  
Plugin-based Telegram alerter for monitoring websites, network devices, weather and much more!  

### Key features:
- Flexible plugin support
- Alerts directly on your device using Telegram
- _Almost_ realtime new plugin discovery - without a need to restart
- Flexible alert times
- Portable and easy to setup

### A new - maybe not needed - way to have a central, modular alert system on Telegram.

This software is something that I wanted to make after I copied the redditTelegram _once more_ to use it as code base
for another project: what if all the common parts were in common and only the real checks where separate files?  
The core itself, personalAlerter.py, doesn't do anything on it's own, but if you add some python packages that follow
the [template](plugins/pluginTemplate) plugin layout, you can easily add cusom alerts!  
Inside this repo a [ping plugin](plugins/pingPlugin) is available to show how a simple ping to check if alive plugin works.

~~A subreddit watcher will soon follow so you will be able to have the same functionality of 
[rssTelegramBot2.0](https://github.com/gabrieleancora/rssTelegramBot2.0) (also called Reddit manga alert bot)
in a new, more complete and flexible, software.~~ I didn't consider the implications of receiving messages, so for now this part is in pause and I'll mantain more actively the rssTelegramBot2.0

Future alert-type of programs will be developed as plugins for this software.

## How does the software works?  
After an initial setup, the main program will enter on a loop, with a configurable wait time between each run.  
On every run, it will read the pluginList.cfg file to check which plugin should be loaded, if they will have a rich 
(markdown) output and eventually other parameters that have to be passed to the plugin itself.  
The plugins will be then executed, in load order, and eventual return message will be sent using Telegram to the specified 
channel.

