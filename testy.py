# -*- coding: utf-8 -*-
import time
from slackclient import SlackClient


# Configuration data

RTM_READ_DELAY = 1
INVOCATION_COMMAND = ".t"
ALLOWED_COMMANDS = {
    'list' : ['list', 'l'],
    'clear': ['clear', 'c'],
    'say'  : ['say']
}
BOT_API_KEY = "YOUR_API_KEY_HERE"
ADMIN_USER_IDS = ['U8GA33W6B']

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
    default_response = """
Not sure what you mean. Try \"*{}* _TestName_\" to assign a new test to yourself.

Other commands:
*.t* - Returns this list of commands.
*.t* list, l - Lists the current status of the tests.
*.t* clear, c - Clears the test assigned to the user that invoked the command.
""".format(INVOCATION_COMMAND)

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

            mainCommand = args[1]

            # 'list' command
            if mainCommand in ALLOWED_COMMANDS['list']:

                if len(tests) > 0:
                    finalTests = ""
                    for test in tests:
                        finalTests += u"<@{0}> - *{1}* \n".format(test['userId'], test['testName']).encode('utf-8')
                    response = "Current status:\n\n{}".format(finalTests)
                else:
                    response = "No one is testing.. are we at :100:%??? :heart_eyes: :heart_eyes:"
            # 'clear' command
            elif mainCommand in ALLOWED_COMMANDS['clear']:

                if len(tests) > 0:
                    for test in tests:
                        if test['userId'] == userid:
                            test['testName'] = ":sleeping:"
                        response = "Test cleared."
            # 'say' command
            elif mainCommand in ALLOWED_COMMANDS['say']:

                if (userid in ADMIN_USER_IDS) and args[2]:
                    # Announce param1 in #tests
                    slack_client.api_call(
                        "chat.postMessage",
                        channel=tests_channel_id,
                        text=args[2])
                    response = "Announced in test channel."

            else:
                
                # if no known command, must be test name
                testName = mainCommand
                existingTests = filterTestsByKeyValue('testName', testName)
                existingUsers = filterTestsByKeyValue('userId', userid)

                # check if test is already added
                if len(existingTests) == 0:
                    
                    #if not, add it to the user
                    if len(existingUsers) > 0:
                        for test in tests:
                            if test['userId'] == userid:
                                test['testName'] = testName
                    else:
                        # add new user if it doesn't exist yet
                        newEntry = { 'userId': userid, 'testName': testName }
                        tests.append(newEntry)
                    response = u'<@{0}> is now testing *{1}*.'.format(userid, testName).encode('utf-8')
                    post_in_test_channel = True
                else:
                    response = u"*{0}* is already being tested by <@{1}>!".format(testName, existingTests[0]['userId']).encode('utf-8')

        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response)

        if post_in_test_channel and response and tests_channel_id and tests_channel_id != channel:
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
            try:
                command, channel, userid = parse_bot_commands(slack_client.rtm_read())
                if command:
                    handle_command(command, channel, userid)
                time.sleep(RTM_READ_DELAY)
            except:
                pass

    else:
        print("\n\nConnection failed :/ See exception traceback. ^\n")
