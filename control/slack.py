import os
import config as conf
from slack import WebClient
from time import sleep
from control.dispatcher import dispatch, DispatchOptions
import re

def slack_interact(dummy,state):
    while True:
        try:
            with open('slack.log','a') as fslack:
                slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

                if "channel" in conf.slack_channel_type:
                    channel_id = conf.slack_channel_name
                    mode = "name"
                elif "im" in conf.slack_channel_type:
                    res = slack_web_client.users_list(types=conf.slack_channel_type)
                    channel_id = [channel['id'] for channel in res['members'] if channel['name'] == conf.slack_channel_name][0]
                    mode = "user"
                res = slack_web_client.users_conversations(types=conf.slack_channel_type)
                conversation_id = [conv['id'] for conv in res['channels'] if conv[mode] == channel_id][0]
                print("Monitoring Slack {} {} with conversation id {}".format(conf.slack_channel_type, conf.slack_channel_name, channel_id), file=fslack)

                while True:
                    messages_to_process = []
                    last_processed_ts = state['slack_last_processed_ts']
                    messages_res_iterator = slack_web_client.conversations_history(channel=conversation_id, oldest=last_processed_ts)
                    for messages_res in messages_res_iterator:
                        messages_to_process.extend([{k: r[k] for k in ['ts','user','text']} for r in messages_res['messages'] if r['ts'] > last_processed_ts])
                    messages_to_process = sorted(messages_to_process, key=lambda k: k['ts'])

                    for message in messages_to_process:
                        print("Processing message: {}".format(message), file=fslack)
                        message_split = message['text'].split(' ')
                        if re.match(DispatchOptions.CURR_TEMP.value, message['text'].lower()):
                            currtemp = dispatch(op=DispatchOptions.CURR_TEMP, state=state)
                            answer = "The current temperature is {} F".format(currtemp)
                        elif re.match(DispatchOptions.GET_SETTEMP.value, message['text'].lower()):
                            settemp = dispatch(op=DispatchOptions.GET_SETTEMP, state=state)
                            answer = "The current target temperature is {} F".format(settemp)
                        elif re.match(DispatchOptions.SETTEMP.value, message['text'].lower()):
                            oldtemp = state['settemp']
                            settemp = message_split[1]
                            dispatch(op=DispatchOptions.SETTEMP, state=state, body=settemp)
                            answer = "Changed target temp {} -> {} F".format(oldtemp, settemp)
                        elif re.match(DispatchOptions.IS_AWAKE.value, message['text'].lower()):
                            isawake = dispatch(op=DispatchOptions.IS_AWAKE, state=state)
                            answer = "The machine is {}awake".format("" if isawake == "True" else "not ")
                        elif re.match(DispatchOptions.SCHEDULE.value, message['text'].lower()):
                            sched_enabled = dispatch(op=DispatchOptions.SCHEDULE, state=state, body=message_split[1])
                            answer = "Schedule is now {}abled".format("en" if sched_enabled else "dis")
                        elif re.match(DispatchOptions.SCHED_DISABLED_OP.value, message['text'].lower()):
                            prev_sched_op = state['sched_disabled_op']
                            sched_op = dispatch(op=DispatchOptions.SCHED_DISABLED_OP, state=state, body=message_split[1])
                            answer = "Schedule disabled op {} -> {}".format(prev_sched_op, sched_op)
                        elif re.match(DispatchOptions.SET_WAKE.value, message['text'].lower()):
                            wake = message_split[1]
                            weekday_or_weekend = message_split[2]
                            oldwake = state["{}_wake_time".format(weekday_or_weekend)]
                            dispatch(op=DispatchOptions.SET_WAKE, state=state, body=message_split[1:])
                            answer = "{} wake changed {} -> {}".format(weekday_or_weekend, oldwake, wake)
                        elif re.match(DispatchOptions.SET_SLEEP.value, message['text'].lower()):
                            sleep_req = message_split[1]
                            weekday_or_weekend = message_split[2]
                            oldsleep = state["{}_sleep_time".format(weekday_or_weekend)]
                            dispatch(op=DispatchOptions.SET_SLEEP, state=state, body=message_split[1:])
                            answer = "{} sleep changed {} -> {}".format(weekday_or_weekend, oldsleep, sleep_req)
                        elif re.match(DispatchOptions.ALLSTATS.value, message['text'].lower()):
                            allstats = dispatch(op=DispatchOptions.ALLSTATS, state=state)
                            answer = "All stats: {}".format(allstats)
                        elif re.match(DispatchOptions.REBOOT.value, message['text'].lower()):
                            answer = "Rebooting..."
                            response = slack_web_client.chat_postMessage(channel="{}".format(conversation_id), text=answer)
                            dispatch(op=DispatchOptions.REBOOT, state=state)
                            continue
                        elif re.match(DispatchOptions.SHUTDOWN.value, message['text'].lower()):
                            answer = "Shutting down..."
                            response = slack_web_client.chat_postMessage(channel="{}".format(conversation_id), text=answer)
                            dispatch(op=DispatchOptions.SHUTDOWN, state=state)
                            continue
                        elif re.match(DispatchOptions.HC.value, message['text'].lower()):
                            ok = dispatch(op=DispatchOptions.HC, state=state)
                            answer = "Everything is {}".format(ok)
                        else:
                            options = dispatch(op=DispatchOptions.LIST, state=state)
                            answer = "The possible commands are: {}".format(options)
                        response = slack_web_client.chat_postMessage(channel="{}".format(conversation_id), text=answer)
                        print("Setting the last processed time to {}".format(response['ts']), file=fslack)
                        state['slack_last_processed_ts'] = response['ts']
                    sleep(conf.slack_sample_time)
        except:
            print("Failue in slack client... Retrying.")
            sleep(conf.slack_sample_time)
