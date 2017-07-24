'''
Created on Aug 24, 2016

@author: rob.proper
'''

import os.path, sys

class Bootstrap:

    @staticmethod
    def loadModulesFromPath(pathName):
        Bootstrap.convertArgumentsToVariables([pathName])
        path = Bootstrap.getVariable(pathName)
        if not path:
            Bootstrap.verbose("Environment variable '{0}' not found".format(pathName))
            return
        paths = path.split(os.pathsep)
        for dirname in paths:
            Bootstrap.verbose("Checking {0} for modules".format(dirname))
            for name in os.listdir(dirname):
                if name != 'browsertest' and os.path.isdir(dirname + os.sep + name):
                    package_path = dirname + os.sep + name
                    #if os.path.isfile(package_path + os.sep + "setup.py"):
                    if package_path in sys.path:
                        #print "Module {0} already on path".format(name)
                        pass
                    else:
                        Bootstrap.verbose("Adding module {1} from {0}".format(package_path, name))
                        sys.path.append(package_path)
                else:
                    Bootstrap.verbose("Skipping {0}".format(name))

    @staticmethod
    def getVariable(name):
        return os.getenv(Bootstrap.convertArgumentToVariableName(name))

    @staticmethod
    def convertArgumentsToVariables(names):
        for arg in sys.argv:
            for name in names:
                Bootstrap.argToEnv(arg, name)

    @staticmethod
    def argToEnv(arg, name):
        prefix = "--" + name
        if not arg or not arg.startswith(prefix):
            return

        prefix = prefix + "="
        if arg.startswith(prefix):
            value = arg.replace(prefix, "")
        else:
            value = "TRUE"

        variable = Bootstrap.convertArgumentToVariableName(name)
        Bootstrap.verbose("set environment variable {0} to '{1}'".format(variable, value))
        os.environ[variable] = value
        return value

    @staticmethod
    def convertArgumentToVariableName(name):
        prefix = "--"
        if name.startswith(prefix):
            name.replace(prefix, "")
        name = name.replace("-", "_")
        name = name.upper()
        return name

    @staticmethod
    def verbose(text):
        isVerbose = os.getenv("VERBOSE_BOOTSTRAP")
        if isVerbose:
            print(text)
