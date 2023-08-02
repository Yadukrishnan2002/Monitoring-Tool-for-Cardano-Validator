import requests
import datetime
import time
import schedule



BASE_URL = 'https://cardano-mainnet.blockfrost.io/api/v0'
API_KEY = 'mainnetyNY3Fu4wG0pHFvMaqjTbNl0WDrPjWOJw' 
Bot_TOKEN = "6627033145:AAEApKdmRMBiq9eIPV4ZrXmglhzPeIKoF1I"
User_chat_id = "763577920"

get_updates_url = f"https://api.telegram.org/bot{Bot_TOKEN}/getUpdates"
response = requests.get(get_updates_url).json()

resList = response['result']
chatID = []

for res in resList:
    chatID.append(res['message']['chat']['id'])


def read_scheduled_blocks(file_path):
    scheduled_blocks = []
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split('                   ')
            if len(values) == 2:
                slotno, utc_time_str = values
                try:
                    utc_time = datetime.datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S UTC")
                    scheduled_blocks.append((int(slotno), utc_time))
                except ValueError:
                    print(f"Invalid UTC time format in line: {line}")
            else:
                print(f"Invalid format in line: {line}")
    return scheduled_blocks


def fetch_blocks_by_pool_id(pool_id):
    url = f'{BASE_URL}/pools/{pool_id}/blocks'
    headers = {'project_id': API_KEY}
    params = {'order' : 'desc'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        blocks_hashes = response.json()
        return blocks_hashes
    except requests.exceptions.RequestException as e:
        print('Error fetching blocks:', e)
        return None


def fetch_block_by_hash(block_hash):
    url = f'{BASE_URL}/blocks/{block_hash}'
    headers = {'project_id': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        block_info = response.json()
        return block_info
    except requests.exceptions.RequestException as e:
        print(f'Error fetching block {block_hash}:', e)
        return None



def fetch_blocks_within_epoch(pool_id):
    blocks_hashes = fetch_blocks_by_pool_id(pool_id)
    current_time = int(time.time())
    five_days_ago = current_time - 5 * 24 * 60 * 60

    blocks_within_time_range = []
    for block_hash in blocks_hashes:
        block_info = fetch_block_by_hash(block_hash)
        if block_info is not None:
            block_timestamp = block_info['time']
            if block_timestamp >= five_days_ago and block_timestamp <= current_time:
                slotno = block_info['slot']
                utc_time = datetime.datetime.fromtimestamp(block_info['time'])
                blocks_within_time_range.append((slotno,utc_time))

    return blocks_within_time_range


def fetch_latest_block(pool_id):

    fetched_blocks = []

    block_hashes = fetch_blocks_by_pool_id(pool_id)
    for i in block_hashes:
        block_info = fetch_block_by_hash(i)
        fetched_blocks.append(block_info)

    sorted_blocks = sorted(fetched_blocks, key=lambda x: x['time'], reverse=True)

    return sorted_blocks[0]

    

def check_Block_produced_in_6hrs(pool_id):

    print("Checking If any Blocks have been produced in 6 hours")

    latest_block = fetch_latest_block(pool_id)

    current_time = int(time.time())
    time_difference = current_time - latest_block['time']

    time_limit = 6 * 60 * 60

    if(time_difference > time_limit):

        for User_chatid in chatID:
            message = "!!!ALERT!!! \nNo Blocks produced in the last 6 hours"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"
            requests.get(url).json()

        print(message)

    else:

        for User_chatid in chatID:
            message = "Blocks have been produced in the last 6 hours"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"
            requests.get(url).json()

        print(message)


def compare_scheduled_and_fetched_blocks(pool_id):

    print("Checking if all the Scheduled Blocks have been produced or not")

    scheduled_blocks = read_scheduled_blocks('LeadershipSchedule.txt')
    blocks_within_epoch = fetch_blocks_within_epoch(pool_id)

    Missing_Blocks = []
    for fetchedBlock in blocks_within_epoch:
        if fetchedBlock not in scheduled_blocks:
            Missing_Blocks.append(fetchedBlock[0])

    print(len(Missing_Blocks)) 

    if(len(Missing_Blocks) > 0):
        for User_chatid in chatID:
            message = "!!!ALERT!!! \nSome Scheduled blocks are missed in the current Epoch"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"
            requests.get(url).json()

        print(Missing_Blocks)
    
    else:
        for User_chatid in chatID:
            message = "All the Scheduled blocks have been successfully produced in the current Epoch"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"

        requests.get(url).json()
    
 

