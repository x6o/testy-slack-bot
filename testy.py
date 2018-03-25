# -*- coding: utf-8 -*-
import os
import time
import re
from slackclient import SlackClient


# Configuration data

RTM_READ_DELAY = 1
INVOCATION_COMMAND = ".t"
BOT_API_KEY = "YOUR_API_KEY_HERE"

bot_id = None
tests_channel_id = "C8W99F119"
tests = []
slack_client = SlackClient(BOT_API_KEY)


# Helper methods

def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            print('\nNew event:')
            print(event)
            message = event["text"]
            return message, event["channel"], event["user"]
    return None, None, None

def filterTestsByKeyValue(key, value):
    return [element for element in tests if element[key].upper() == value.upper()]

def handle_command(command, channel, userid):
    response = None
    post_in_test_channel = False
    allowed_commands = ['list', 'clear']
    default_response = "Not sure what you mean. Try \"*{}* [_test name_]\" to assign a new test to yourself.\n\nOther commands:\n*.t list* - Displays active tests\n*.t clear* - Clear your active test.".format(INVOCATION_COMMAND)

    if command.startswith(INVOCATION_COMMAND):
        
        """
            args[0] -> invocation command
            args[1] -> command (or test name)
            args[2] -> param1
            args[3] -> param2
            ...
            args[n] -> paramN-1
        """
        args = command.split()

        if len(args) > 1:

            if args[1] in allowed_commands:

                # 'list' command
                if args[1] == 'list':
                    if len(tests) > 0:
                        finalTests = ""
                        for test in tests:
                            finalTests += u"<@{0}> - *{1}* \n".format(test['userId'], test['testName']).encode('utf-8')
                        response = "Current status:\n\n{}".format(finalTests)
                    else:
                        response = "No one is testing.. are we at :100:%??? :heart_eyes: :heart_eyes:"
                
                # 'clear' command
                if args[1] == 'clear':
                    if len(tests) > 0:
                        for test in tests:
                            if test['userId'] == userid:
                                test['testName'] = ":sleeping:"
                            response = "Test cleared."
            else:
                
                # if no known command, must be test name
                existingTests = filterTestsByKeyValue('testName', args[1])
                existingUsers = filterTestsByKeyValue('userId', userid)

                # check if test is already added
                if len(existingTests) == 0:
                    
                    #if not, add it to the user
                    if len(existingUsers) > 0:
                        for test in tests:
                            if test['userId'] == userid:
                                test['testName'] = args[1]
                    else:
                        # add new user if it doesn't exist yet
                        newEntry = { 'userId': userid, 'testName': args[1] }
                        tests.append(newEntry)
                    response = u'<@{0}> is now testing *{1}*.'.format(userid, args[1]).encode('utf-8')
                    post_in_test_channel = True
                else:
                    response = u"*{0}* is already being tested by <@{1}>!".format(args[1], existingTests[0]['userId']).encode('utf-8')

        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response)

        if post_in_test_channel and response and tests_channel_id and channel_channel_id != channel:
            # Post to #tests
            slack_client.api_call(
                "chat.postMessage",
                channel=tests_channel_id,
                text=response)


# Main

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Connected to Slack :D")
        bot_id = slack_client.api_call("auth.test")['user_id']
        while True:
            command, channel, userid = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, userid)
            time.sleep(RTM_READ_DELAY)
    else:
        print("\n\nConnection failed :/ See exception traceback. ^\n")
