import os
import config as conf
from slack import WebClient
from time import sleep
from control.dispatcher import dispatch

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
                    messages_res_iterator = slack_web_client.conversations_history(channel=channel_id)
                    for messages_res in messages_res_iterator:
                        messages_to_process.extend([{k: r[k] for k in ['ts','user','text']} for r in messages_res['messages'] if r['ts'] > last_processed_ts])
                    messages_to_process = sorted(messages_to_process, key=lambda k: k['ts'])

                    for message in messages_to_process:
                        print("Processing message: {}".format(message), file=fslack)
                        message_split = message['text'].split(' ')
                        if "curr_temp" in message['text']:
                            currtemp = dispatch(op="curr_temp", state=state)
                            answer = "The current temperature is {} F".format(currtemp)
                        elif "get_settemp" in message['text']:
                            settemp = dispatch(op="get_settemp", state=state)
                            answer = "The current target temperature is {} F".format(settemp)
                        elif "settemp" in message['text']:
                            oldtemp = state['settemp']
                            settemp = message_split[1]
                            dispatch(op="settemp", state=state, body=settemp)
                            answer = "Changed target temp {} -> {} F".format(oldtemp, settemp)
                        elif "is_awake" in message['text']:
                            isawake = dispatch(op="is_awake", state=state)
                            answer = "The machine is {}awake".format("" if isawake == "True" else "not ")
                        elif "schedule" in message['text']:
                            sched_enabled = dispatch(op="schedule", state=state, body=message_split[1])
                            answer = "Schedule is now {}abled".format("en" if sched_enabled else "dis")
                        elif "set_wake" in message['text']:
                            wake = message_split[1]
                            weekday_or_weekend = message_split[2]
                            oldwake = state["{}_wake_time".format(weekday_or_weekend)]
                            dispatch(op="set_wake", state=state, body=message_split[1:])
                            answer = "{} wake changed {} -> {}".format(weekday_or_weekend, oldwake, wake)
                        elif "set_sleep" in message['text']:
                            sleep_req = message_split[1]
                            weekday_or_weekend = message_split[2]
                            oldsleep = state["{}_sleep_time".format(weekday_or_weekend)]
                            dispatch(op="set_sleep", state=state, body=message_split[1:])
                            answer = "{} sleep changed {} -> {}".format(weekday_or_weekend, oldsleep, sleep_req)
                        elif "all_stats" in message['text']:
                            allstats = dispatch(op="all_stats", state=state)
                            answer = "All stats: {}".format(allstats)
                        elif "reboot" in message['text']:
                            answer = "Rebooting..."
                            response = slack_web_client.chat_postMessage(channel="#{}".format(conf.slack_channel), text=answer)
                            dispatch(op="restart", state=state)
                            continue
                        elif "shutdown" in message['text']:
                            answer = "Shutting down..."
                            response = slack_web_client.chat_postMessage(channel="#{}".format(conf.slack_channel), text=answer)
                            dispatch(op="restart", state=state)
                            continue
                        elif "hc" in message['text']:
                            ok = dispatch(op="hc", state=state)
                            answer = "Everything is {}".format(ok)
                        else:
                            options = dispatch(op="list", state=state)
                            answer = "The possible commands are: {}".format(options)
                        response = slack_web_client.chat_postMessage(channel="#{}".format(conf.slack_channel), text=answer)
                        print("Setting the last processed time to {}".format(response['ts']), file=fslack)
                        state['slack_last_processed_ts'] = response['ts']
                    sleep(conf.slack_sample_time)
        except:
            print("Failue in slack client... Retrying.")
