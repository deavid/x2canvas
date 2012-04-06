# coding: UTF8
from autoconfig.autoconfig import AutoConfigTemplate, ConfigReader
import sys

Config = None
config_filelist = ['config.ini']

class ConfigGlobal(AutoConfigTemplate):
    """
    novnc=string:libraries/noVNC
    """
        

def reloadConfig(saveTemplate = False):
    global Config, config_filelist
    Config = ConfigReader(files=config_filelist, saveConfig = saveTemplate)
    Config.Global = ConfigGlobal(Config,section = "global")
    
    if saveTemplate:
        f1w = open(saveTemplate, 'wb')
        Config.configini.write(f1w)
        f1w.close()
    else:
        if Config.errors:
            print "INFO: ** La configuracion esta desactualizada, ejecute <python config.py update > para actualizarla ** "


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'savetemplate':
            global config_filelist 
            config_filelist = []
            reloadConfig(saveTemplate = 'config.template.ini')
        elif sys.argv[1] == 'update':
            reloadConfig(saveTemplate = 'config.ini')
    else:
        reloadConfig()


if __name__ == "__main__": main()
else: reloadConfig()
