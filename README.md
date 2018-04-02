
# Testy - Slack bot

### What is it?

Testy is a simple bot to track the unit tests being worked on by a team. The source code is inside [testy.py](testy.py) - the rest of the files are necessary for Heroku deployment.

### How does it work?

Testy monitors the channels it has been invited to and also the private messages sent to it.
When it detects a message that starts with the invocation command (**.t** in our case), it parses it
and acts accordingly.

### What commands can it handle?

* **.t** - Returns this list of commands.
* **.t** _testName_ - Assigns _testName_ to the user that invoked the command. Notice that the test name can't have spaces.
* **.t** list, l - Lists the current status of the tests.
* **.t** clear, c - Clears the test assigned to the user that invoked the command.

### Prerequisites 

* For Heroku deployment
    * [Heroku CLI](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
    * [git](https://git-scm.com/downloads)
* For slack bot
    * [SlackClient](https://pypi.python.org/pypi/slackclient)

### License

This project is licensed under GNU General Public License v3.0 - see the [LICENCE.md](LICENCE.md) file for details.

### Future improvements

These are some of the functionalities that would really make this a superb bot:
* Ability to assign more than one test to a user.
* Add a **.t coverage** command to be able to check and update current test coverage of the project.
* Persistent storage, although this doesn't seem like a big concern ATM (Heroku is pretty reliable).
* Ability for it to make me a cup of coffee.

## Acknowledgments

* [Official guide to deploy app](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)
* [Official guide about worker](https://devcenter.heroku.com/articles/background-jobs-queueing)
* [Guided "Simple twitter-bot with Python, Tweepy and Heroku"](http://briancaffey.github.io/2016/04/05/twitter-bot-tutorial.html)
