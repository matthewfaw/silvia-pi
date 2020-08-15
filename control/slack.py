import os
import config as conf
from slack import WebClient
from time import sleep

def slack_interact(dummy,state):
    while True:
        try:
            with open('slack.log','a') as fslack:
                slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

                res = slack_web_client.conversations_list()
                channel_id = [channel['id'] for channel in res['channels'] if channel['name'] == conf.slack_channel][0]
                print("Monitoring Slack channel {} with channel id {}".format(conf.slack_channel, channel_id), file=fslack)

                while True:
                    messages_to_process = []
                    last_processed_ts = state['slack_last_processed_ts']
                    messages_res_iterator = client.conversations_history(channel=channel_id)
                    for messages_res in messages_res_iterator:
                        messages_to_process.extend([{k: r[k] for k in ['ts','user','text']} for r in res['messages'] if r['ts'] > last_processed_ts])
                    messages_to_process = sorted(messages_to_process, key: lambda k: k['ts'])

                    for message in messages_to_process:
                        print("Processing message: {}".format(message))
                        response = client.chat_postMessage(channel="#{}".format(conf.slack_channel), text="Derp")
                        state['slack_last_processed_ts'] = message['ts']
                    sleep(conf.slack_sample_time)
        except:
            print("Encountered an error... Restarting Slack connection.", file=fslack)
