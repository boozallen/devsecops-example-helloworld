'''
Created on Aug 24, 2016

@author: rob.proper
'''

class Result:

    PASS = 'pass'
    ERROR = 'error'
    FAILURE = 'failure'

    @staticmethod
    def convert(result, numberOfErrors = 0, numberOfFailures = 0): 
        if not result or (len(result.errors) > numberOfErrors):
            return Result.ERROR
        elif len(result.failures) > numberOfFailures:
            return Result.FAILURE
        else:
            return Result.PASS