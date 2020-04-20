#  -*- utf-8 -*-
import pyautogui
import paho.mqtt.client as mqtt
import json
import string
import re
from regex_dict import RegexDict


HOST = "mqtt.beebotte.com"
TOPIC = "[channel]/[resource]"
TOKEN = "[token]"
CACEPT = "mqtt.beebotte.com.pem"
PORT = 8883

r_command_dict = {}


def set_variables_to_vars_dict(_input_str):
    words = [word for word in re.findall(r'[a-z]+[0-9]*|[0-9]+', _input_str) if word != '']
    command_vars_dict = {}
    if words:
        for i in range(len(words)):
            command_vars_dict['w'+str(i+1)] = words[i]
    return command_vars_dict


def convert_speech_input(_speech_input_str):
    vars_dict = set_variables_to_vars_dict(_speech_input_str)
    converted_command = string.Template(r_command_dict[_speech_input_str])
    return converted_command.safe_substitute(vars_dict)


def on_connect(client, userdata, flags, response_code):
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    recog_result = json.loads(msg.payload.decode("utf-8"))["data"]
    # 音声認識結果のスペースを詰める
    speech_input = recog_result.replace(' ', '')
    print('received: '+speech_input)

    try:
        # Google Homeの半角単語は大文字で始まるため小文字に
        result = convert_speech_input(speech_input.lower()).split('`')

        reserved_word = ['enter', 'esc']
        for word in result:
            if word in reserved_word:
                pyautogui.press(word)
            else:
                pyautogui.typewrite(word, interval=0)

    except KeyError:
        print('Key Error')


if __name__ == '__main__':
    with open('vim_commands.json', 'r', encoding='utf-8') as ref_json:
        r_command_dict = RegexDict(json.load(ref_json))
        ref_json.close()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("token:%s" % TOKEN)
    client.tls_set(CACEPT)
    client.connect(HOST, port=PORT, keepalive=60)
    client.loop_forever()
