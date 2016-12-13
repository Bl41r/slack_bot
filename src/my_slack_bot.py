"""My first slack bot.

Inspired by tutorial at:
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""


import os
import time
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
MASTER_ID = os.environ.get("MASTER_ID") or 1

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMANDS = ["grade", "order", "attack", "sleep"]

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def do_response(cmd, body):
    """Handle the commands."""
    body = ' '.join(body)
    command_dict = {
        'grade': 'Yesss.  Grading ' + body,
        'order': 'Ordering ' + body,
        'attack': 'I will ssstrike ' + body + ' down.',
        'sleep': 'zZzZz ... zZzZz ...',
    }
    return command_dict[cmd]


def handle_command(command, channel):
    """Receive commands directed at the bot and determines if valid."""
    command = command.split()
    response = "I cannot undersssstand you."
    if command[0] in EXAMPLE_COMMANDS:
        response = do_response(command[0], command[1:])
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
        while True:
            try:
                tmp = parse_slack_output(slack_client.rtm_read())
                command, channel = tmp
                # print('it worked:', command, channel)
            except:
                print('error: ', tmp)

            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
