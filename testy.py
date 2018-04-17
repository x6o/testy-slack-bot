# -*- coding: utf-8 -*-
import time
import firebase_admin
from slackclient import SlackClient
from firebase_admin import credentials, db


# Configuration data

cred = credentials.Certificate('FIREBASE_CERT.JSON')
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'YOUR_DATABASE_URL'
})
ref = db.reference()
tests_ref = ref.child('tests')

RTM_READ_DELAY = 1
INVOCATION_COMMAND = ".t"
ALLOWED_COMMANDS = {
    'list'              : ['list', 'l'],
    'clear'             : ['clear', 'c'],
    'say'               : ['say', 's'],
    'listForbidden'     : ['listForbidden', 'lf'],
    'addForbidden'      : ['addForbidden', '+f'],
    'removeForbidden'   : ['removeForbidden', '-f']
}
BOT_API_KEY = "YOUR_API_KEY_HERE"
ADMIN_USER_IDS = ['U8GA33W6B']

bot_id = None
tests_channel_id = "C8W99F119" # prod: "C8W99F119" test: "G9S6NDXE0"
tests = []
forbidden_tests = []
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
    print 'key:'
    print key
    print 'val:'
    print value

    print tests
    return [element for element in tests if tests[element][key].upper() == value.upper()]

def handle_command(command, channel, userid):
    response = None
    post_in_test_channel = False
    default_response = """
Not sure what you mean. Try \"*{}* _TestName_\" to assign a new test to yourself.

Other commands:
*.t* - Returns this list of commands.
*.t* list, l - Lists the current status of the tests.
*.t* clear, c - Clears the test assigned to the user that invoked the command.
*.t* listForbidden, lf - See list of forbidden classes/tests.
*.t* addForbidden, +f _TestName_ - Add _TestName_ to forbidden list.
*.t* removeForbidden, -f _TestName_ - Remove _TestName_ from forbidden list.
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

            tests = tests_ref.get()
            mainCommand = args[1]

            # 'list' command
            if mainCommand in ALLOWED_COMMANDS['list']:

                if tests and len(tests) > 0:
                    finalTests = ""
                    for test in tests:
                        finalTests += u"<@{0}> - *{1}* \n".format(tests[test]['userId'], tests[test]['testName']).encode('utf-8')
                    response = "Current status:\n\n{}".format(finalTests)
                else:
                    response = "No one is testing.. are we at :100:%??? :heart_eyes: :heart_eyes:"
            # 'clear' command
            elif mainCommand in ALLOWED_COMMANDS['clear']:

                if tests and len(tests) > 0:
                    for test in tests:
                        if tests[test]['userId'] == userid:
                            tests[test]['testName'] = ":sleeping:"
                        response = "Test cleared."
                        tests_ref.set(tests)
            # 'say' command
            elif mainCommand in ALLOWED_COMMANDS['say']:

                if (userid in ADMIN_USER_IDS) and args[2]:
                    # Announce param1 in #tests
                    slack_client.api_call(
                        "chat.postMessage",
                        channel=tests_channel_id,
                        text=args[2])
                    response = "Announced in test channel."
            # 'listForbidden' command
            elif mainCommand in ALLOWED_COMMANDS['listForbidden']:
                fb_testsRef = ref.child('fbtests')
                fb_tests = fb_testsRef.get()
                if fb_tests and len(fb_tests) > 0:
                    final_fb_tests = ""
                    for fb_test in fb_tests:
                        final_fb_tests += u"*{0}*\n".format(fb_tests[fb_test]['testName']).encode('utf-8')
                    response = "Please ignore these classes:\n\n{}".format(final_fb_tests)
                else:
                    response = "Nothing to see. Happy testing!"
            # 'addForbidden' command
            elif mainCommand in ALLOWED_COMMANDS['addForbidden']:
                fb_testsRef = ref.child('fbtests')
                fb_tests = fb_testsRef.get()
                testName = args[2] or None

                if testName:
                    if not fb_tests:
                        existingFbTests = []
                    else:
                        existingFbTests = [element for element in fb_tests if fb_tests and fb_tests[element]['testName'].upper() == testName.upper()]

                    if len(existingFbTests) == 0:
                        # add new forbidden test
                        newEntry = { 'testName': testName }
                        fb_testsRef.push(newEntry)
                        response = "*{0}* has been added to the list of forbidden tests.\n_Type *.t listForbidden* or *.t lf* to see the entire list._".format(testName).encode('utf-8')
                        post_in_test_channel = True
                    else:
                        response = "Already in list.\n_Type *.t listForbidden* or *.t lf* to see the list._"
                        
            # 'removeForbidden' command
            elif mainCommand in ALLOWED_COMMANDS['removeForbidden']:
                fb_testsRef = ref.child('fbtests')
                fb_tests = fb_testsRef.get()
                testName = args[2] or None

                if fb_tests and len(fb_tests) > 0:
                    found = False
                    for fb_test in fb_tests:
                        if fb_tests[fb_test]['testName'] == testName:
                            found = True
                            fb_tests[fb_test]['testName'] = None
                            fb_testsRef.set(fb_tests)
                            response = "*{0}* has been removed from the list of forbidden tests.\n_Type *.t listForbidden* or *.t lf* to see the entire list._".format(testName).encode('utf-8')
                            post_in_test_channel = True
                        
                    if not found:
                        response = "*{0}* has not been found on list. _Type *.t listForbidden* or *.t lf* to see the entire list._".format(testName).encode('utf-8')

            else:
                
                # if no known command, must be test name
                testName = mainCommand

                # check if forbidden test
                fb_testsRef = ref.child('fbtests')
                fb_tests = fb_testsRef.get()
                print fb_tests
                print testName
                isForbiddenTest = False
                if fb_tests and len(fb_tests) > 0:
                    for fb_test in fb_tests:
                        if fb_tests[fb_test]['testName'].upper() == testName.upper():
                            isForbiddenTest = True
                            response = "*{0}* is in the list of forbidden tests!\n_Type *.t listForbidden* or *.t lf* to see the entire list._".format(testName).encode('utf-8')

                if not isForbiddenTest:
                    existingTests = [element for element in tests if tests and tests[element]['testName'].upper() == testName.upper()]
                    existingUsers = [element for element in tests if tests and tests[element]['userId'].upper() == userid.upper()]

                    # check if test is already added
                    if len(existingTests) == 0:
                        
                        #if not, add it to the user
                        if len(existingUsers) > 0:
                            for test in tests:
                                if tests[test]['userId'] == userid:
                                    tests[test]['testName'] = testName
                                    tests_ref.set(tests)
                        else:
                            # add new user if it doesn't exist yet
                            newEntry = { 'userId': userid, 'testName': testName }
                            tests_ref.push(newEntry)

                        response = u'<@{0}> is now testing *{1}*.'.format(userid, testName).encode('utf-8')
                        post_in_test_channel = True
                    else:
                        response = u"*{0}* is already being tested by <@{1}>!".format(testName, tests[existingTests[0]]['userId']).encode('utf-8')

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
                print 'Error :('
                pass

    else:
        print("\n\nConnection failed :/ See exception traceback. ^\n")
