import os
import config as conf
from slack import WebClient
from time import sleep
from control.dispatcher import dispatch, DispatchOptions
import re

def get_client():
    return WebClient(token=os.environ['SLACK_BOT_TOKEN'])

def get_conversation_id(client=None):
    slack_web_client = client if client is not None else get_client()
    if "channel" in conf.slack_channel_type:
        channel_id = conf.slack_channel_name
        mode = "name"
    elif "im" in conf.slack_channel_type:
        res = slack_web_client.users_list(types=conf.slack_channel_type)
        channel_id = [channel['id'] for channel in res['members'] if channel['name'] == conf.slack_channel_name][0]
        mode = "user"
    res = slack_web_client.users_conversations(types=conf.slack_channel_type)
    conversation_id = [conv['id'] for conv in res['channels'] if conv[mode] == channel_id][0]
    return conversation_id

def get_messages(client, conversation_id, since_ts):
    messages_to_process = []
    messages_res_iterator = client.conversations_history(channel=conversation_id, oldest=since_ts)
    for messages_res in messages_res_iterator:
        messages_to_process.extend([{k: r[k] for k in ['ts','user','text']} for r in messages_res['messages'] if r['ts'] > since_ts])
    return sorted(messages_to_process, key=lambda k: k['ts'])

def send_message(client, conversation_id, message):
    return client.chat_postMessage(channel="{}".format(conversation_id), text=message)

def get_response_for(message, state, client, conversation_id):
    message_split = message.split(' ')
    message = message.lower()
    if re.match(DispatchOptions.CURR_TEMP.value, message):
        currtemp = dispatch(op=DispatchOptions.CURR_TEMP, state=state)
        return "The current temperature is {} F".format(currtemp)
    elif re.match(DispatchOptions.GET_SETTEMP.value, message):
        settemp = dispatch(op=DispatchOptions.GET_SETTEMP, state=state)
        return "The current target temperature is {} F".format(settemp)
    elif re.match(DispatchOptions.SETTEMP.value, message):
        oldtemp = state['settemp']
        settemp = message_split[1]
        dispatch(op=DispatchOptions.SETTEMP, state=state, body=settemp)
        return "Changed target temp {} -> {} F".format(oldtemp, settemp)
    elif re.match(DispatchOptions.IS_AWAKE.value, message):
        isawake = dispatch(op=DispatchOptions.IS_AWAKE, state=state)
        return "The machine is {}awake".format("" if isawake == "True" else "not ")
    elif re.match(DispatchOptions.SCHEDULE.value, message):
        sched_enabled = dispatch(op=DispatchOptions.SCHEDULE, state=state, body=message_split[1])
        return "Schedule is now {}abled".format("en" if sched_enabled else "dis")
    elif re.match(DispatchOptions.SCHED_DISABLED_OP.value, message):
        prev_sched_op = state['sched_disabled_op']
        sched_op = dispatch(op=DispatchOptions.SCHED_DISABLED_OP, state=state, body=message_split[1])
        return "Schedule disabled op {} -> {}".format(prev_sched_op, sched_op)
    elif re.match(DispatchOptions.SET_WAKE.value, message):
        wake = message_split[1]
        weekday_or_weekend = message_split[2]
        oldwake = state["{}_wake_time".format(weekday_or_weekend)]
        dispatch(op=DispatchOptions.SET_WAKE, state=state, body=message_split[1:])
        return "{} wake changed {} -> {}".format(weekday_or_weekend, oldwake, wake)
    elif re.match(DispatchOptions.SET_SLEEP.value, message):
        sleep_req = message_split[1]
        weekday_or_weekend = message_split[2]
        oldsleep = state["{}_sleep_time".format(weekday_or_weekend)]
        dispatch(op=DispatchOptions.SET_SLEEP, state=state, body=message_split[1:])
        return "{} sleep changed {} -> {}".format(weekday_or_weekend, oldsleep, sleep_req)
    elif re.match(DispatchOptions.ALLSTATS.value, message):
        allstats = dispatch(op=DispatchOptions.ALLSTATS, state=state)
        return "All stats: ```{}```".format(allstats)
    elif re.match(DispatchOptions.REBOOT.value, message):
        answer = "Rebooting..."
        response = send_message(client=client, conversation_id=conversation_id, message=answer)
        dispatch(op=DispatchOptions.REBOOT, state=state)
        return
    elif re.match(DispatchOptions.SHUTDOWN.value, message):
        answer = "Shutting down..."
        response = send_message(client=client, conversation_id=conversation_id, message=answer)
        dispatch(op=DispatchOptions.SHUTDOWN, state=state)
        return
    elif re.match(DispatchOptions.HC.value, message):
        ok = dispatch(op=DispatchOptions.HC, state=state)
        return "Everything is {}".format(ok)
    else:
        options = dispatch(op=DispatchOptions.LIST, state=state)
        return "The possible commands are: ```{}```".format(options)

def slack_interact(dummy,state):
    while True:
        try:
            with open('slack.log','a') as fslack:
                slack_web_client = get_client()

                conversation_id = get_conversation_id(client=slack_web_client)
                print("Monitoring Slack {} {} with conversation id {}".format(conf.slack_channel_type, conf.slack_channel_name, conversation_id), file=fslack)

                while True:
                    last_processed_ts = state['slack_last_processed_ts']
                    messages_to_process = get_messages(client=slack_web_client, conversation_id=conversation_id, since_ts=last_processed_ts)

                    for message in messages_to_process:
                        print("Processing message: {}".format(message), file=fslack)
                        answer = get_response_for(message=message['text'], state=state, client=slack_web_client, conversation_id=conversation_id)
                        response = send_message(client=slack_web_client, conversation_id=conversation_id, message=answer)
                        print("Setting the last processed time to {}".format(response['ts']), file=fslack)
                        state['slack_last_processed_ts'] = response['ts']
                    sleep(conf.slack_sample_time)
        except:
            print("Failue in slack client... Retrying.")
            sleep(conf.slack_sample_time)
