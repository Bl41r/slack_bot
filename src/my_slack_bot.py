"""My first slack bot.

Inspired by tutorial at:
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""


import os
import time
from slackclient import SlackClient
import requests
import re
import schedule

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
MASTER_ID = os.environ.get("MASTER_ID") or 1
TEST_CHANNEL = 'C3EKFEUKH'

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMANDS = ["grade", "order", "attack", "sleep", "book", "what is the book of the day?"]

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def find_book_of_day():
    """Find the book of the day from packtpub."""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(
        'https://www.packtpub.com/packt/offers/free-learning',
        headers=headers)

    if response.status_code == 200:
        regex_search = re.search('<div class=\"dotd-title\">\\n(\\t)*<h2>\\n(\\t)*(.*?)(?=\\t)',
                                 response.text,
                                 re.DOTALL)
        return 'Book of the day from packtpub: ' + regex_search.group(3)\
            + '\nhttps://www.packtpub.com/packt/offers/free-learning'
    else:
        return 'Error with status code: ' + response.status_code + \
            ': ' + response.reason


def do_response(cmd, body):
    """Handle the commands."""
    body = ' '.join(body)
    command_dict = {
        'grade': 'Yesss.  Grading ' + body,
        'order': 'Ordering ' + body,
        'attack': 'I will ssstrike ' + body + ' down.',
        'sleep': 'zZzZz ... zZzZz ...',
        'what is the book of the day?': find_book_of_day(),
        'book': find_book_of_day(),
    }
    return command_dict[cmd]


def handle_command(command, channel):
    """Receive commands directed at the bot and determines if valid."""
    command = command.split()
    response = "I cannot undersssstand you."

    if command[0].lower() in EXAMPLE_COMMANDS:
        response = do_response(command[0], command[1:])
    elif ' '.lower().join(command) in EXAMPLE_COMMANDS:
        response = do_response(' '.join(command), '')

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """Parse output, listening for triggering information."""
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            print(output)
            if output and 'text' in output and AT_BOT in output['text']:
                if output['user'] == MASTER_ID:
                    # return text after the @ mention, whitespace removed
                    print('command:',
                          output['text'].split(AT_BOT)[1].strip().lower(),
                          'channel:', output['channel'])

                    return (output['text'].split(AT_BOT)[1].strip().lower(),
                            output['channel'])
                else:
                    slack_client.api_call("chat.postMessage", channel=channel,
                                          text="hisssss!", as_user=True)
                    print('Command issued not from master.')

    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 2    # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("py_bot connected and running!")
        schedule.every().day.at("12:22").do(handle_command, 'book', TEST_CHANNEL)
        time.sleep(1)
        while True:

            try:
                tmp = parse_slack_output(slack_client.rtm_read())
                command, channel = tmp
                schedule.run_pending()
            except:
                print('error: ', tmp)

            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
