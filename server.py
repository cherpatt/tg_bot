import requests
import json
import telebot
import threading
import time
address_list = ['0x8aceab8167c80cb8b3de7fa6228b889bb1130ee8','0x76c49d0e2b00ded0611862f0713c624a9bd0a432','0xc333e80ef2dec2805f239e3f1e810612d294f771','0xef22c14f46858d5ac61326497b056974167f2ee1']
ETHERSCAN_KEY = '42T1XZPXVCNZDDW6DW2AAA1TNZ853U91VP'
BOT_KEY = '5159902342:AAGEdMb2Kh6HHofUgyHYckSw3ZdNxTHhKqo'
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func
def transactions(wallet: str = None) -> list:
    assert(wallet is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet,
        'startblock': 14315669,
        'endblock': 99999999,
        'offset': 1,
        'sort': 'desc',
        'apikey': ETHERSCAN_KEY
    }
    
    response = requests.get('https://api.etherscan.io/api', params=url_params)
    response_parsed = json.loads(response.content)
    assert(response_parsed['message'] == 'OK')
    txs = response_parsed['result']
    # print(txs[0].keys())
    return [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp'], 'blockNumber' : tx['blockNumber']} \
         for tx in txs ]

def update_prev_block(prev_data,cur_data):
    for i in cur_data.keys():
        if(i not in prev_data.keys()):
            prev_data[i] = {
                'blockNumber' : 0
            }
        prev_data[i]['blockNumber'] = cur_data[i][0]['blockNumber']
    return prev_data
def send_notificate(prev_data,cur_data,bot,subscibe_address_list):
    for i in cur_data.keys():
        if(i in prev_data.keys()):
            if cur_data[i][0]['blockNumber'] > prev_data[i]['blockNumber'] :
                #send noti
                for individual_id in subscibe_address_list :
                    bot.send_message(individual_id,'{} '.format(cur_data[i][0]))
                    # print('send noti')
                pass
        if(len(prev_data.keys()) == 0) :
            for individual_id in subscibe_address_list :
                bot.send_message(individual_id,'{} '.format(cur_data[i][0]))
                # print('send noti')

#Main 
@background 
def background_main(bot,subscibe_address_list,prev_data,new_data) :
    while True :
        # print('start')
        for i in address_list : 
            result = transactions(i)
            new_data[result[0]['from']] = result
        send_notificate(prev_data,new_data,bot,subscibe_address_list)
        prev_data = update_prev_block(prev_data,new_data)
        time.sleep(60*3)
#Main

# print(len(result))
# print(result[0]['blockNumber'])
subscibe_address_list = ['1205802901'] #initial wallet 1205802901
bot = telebot.TeleBot(BOT_KEY, parse_mode=None)
prev_data = {}
new_data = {}

@bot.message_handler(commands=['add_wallet_listener'])
def handle_add_wallet_listener(message):
    subscibe_address_list.append(message.chat.id)
    bot.send_message(message.chat.id,'add {} into subsciber'.format(message.chat.id))

@bot.message_handler(commands=['get_listening_wallets'])
def handle_get_listening_wallets(message):
    if str(message.chat.id) in subscibe_address_list:
        reply_data = 'You are currently subscribed to events from : '
        reply_data += ',\n'.join(map(str,prev_data.keys()))
        bot.reply_to(message,reply_data )

@bot.message_handler(commands=['get_all_subscribe_wallet'])
def handle_get_all_subscribe_wallet(message):
    str_reply = ''
    for i in subscibe_address_list :
        str_reply += '{},\n'.format(str(i))
    bot.reply_to(message,str_reply)

@bot.message_handler(commands=['get_lastest_tx'])
def handle_get_lastest_tx(message):
    str_reply = ''
    print(prev_data)
    for i in prev_data.keys() : 
        print(i)
        str_reply += 'wallet {} have lastest block at {} \n'.format(i,prev_data[i]['blockNumber']) 
    bot.reply_to(message,str_reply)

background_main(bot,subscibe_address_list,prev_data,new_data)
bot.infinity_polling(interval=0, timeout=20)
