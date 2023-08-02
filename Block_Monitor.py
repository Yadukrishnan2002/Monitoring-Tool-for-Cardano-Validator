import requests
import datetime
import time
import schedule
import logging


# Set up the url and API key for the Blockfrost api
BASE_URL = 'https://cardano-mainnet.blockfrost.io/api/v0'
API_KEY = 'mainnetyNY3Fu4wG0pHFvMaqjTbNl0WDrPjWOJw' 

# Provide the bot token id of telegram bot
Bot_TOKEN = "6627033145:AAEApKdmRMBiq9eIPV4ZrXmglhzPeIKoF1I"


# Using the get_updates_url, fetch the ChatID of all the individuals who have registered with the newly created bot
# This is done to send the alert signals to all the participants who have registered with the bot
get_updates_url = f"https://api.telegram.org/bot{Bot_TOKEN}/getUpdates"
response = requests.get(get_updates_url).json()

resList = response['result']
chatID = []

for res in resList:
    chatID.append(res['message']['chat']['id'])


# Setting up the logging configuration:
# filename: Name of the log file to store the logs
# level: Logging levels to be captured
# format: sets the format of the log message
logging.basicConfig(
    filename='block_monitoring_tool.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function that logs a message to the log file
def log_print(msg):
    logging.info(msg)



# Function which reads the content from the given Leadership Schedule text file and parse the date into a list of tuples
# Each tuple contains the slot number and the corresponding UTC time 
def read_scheduled_blocks(file_path):
    scheduled_blocks = []
    with open(file_path, 'r') as file:
        for line in file:

            # Splits the line using the delimiter to extract values
            values = line.strip().split('                   ')

            # Check if the line contains exactly two values (slot number and UTC time)
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


# Function which fetches the blocks produced by a specific pool ID from the Cardano blockchain usng the Blockfrost API
# The response will be a json file that consists of the block hashes
def fetch_blocks_by_pool_id(pool_id):
    url = f'{BASE_URL}/pools/{pool_id}/blocks'
    headers = {'project_id': API_KEY}
    params = {'order' : 'desc'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        blocks_hashes = response.json()

        # Returns the list of block hashes fetched from the API
        return blocks_hashes
    except requests.exceptions.RequestException as e:
        print('Error fetching blocks:', e)
        return None


# Function which fetches the detailed information about a specific block using its unique block hash
def fetch_block_by_hash(block_hash):
    url = f'{BASE_URL}/blocks/{block_hash}'
    headers = {'project_id': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        block_info = response.json()

        # Returns a dictionary containing block information
        return block_info
    except requests.exceptions.RequestException as e:
        print(f'Error fetching block {block_hash}:', e)
        return None


# This Function makes use of the above two functions to get the list of blocks with its information
# It then returns all the blocks that fall between the specified time range of an epoch, ie 5 days
def fetch_blocks_within_epoch(pool_id):
    blocks_hashes = fetch_blocks_by_pool_id(pool_id)

    #Calculates the time stamp of the current time
    current_time = int(time.time())

    # Calculates the time stamp for five days ago from the current time
    five_days_ago = current_time - 5 * 24 * 60 * 60

    blocks_within_time_range = []
    for block_hash in blocks_hashes:
        block_info = fetch_block_by_hash(block_hash)
        if block_info is not None:
            block_timestamp = block_info['time']

            #Checks if the block falls within the time range of the current epoch
            if block_timestamp >= five_days_ago and block_timestamp <= current_time:
                slotno = block_info['slot']

                #Converts timestamp to UTC Time format
                utc_time = datetime.datetime.fromtimestamp(block_info['time'])
                blocks_within_time_range.append((slotno,utc_time))

    return blocks_within_time_range


# Function which fetches the latest block produced by a specified pool ID
def fetch_latest_block(pool_id):

    fetched_blocks = []

    block_hashes = fetch_blocks_by_pool_id(pool_id)
    for i in block_hashes:
        block_info = fetch_block_by_hash(i)
        fetched_blocks.append(block_info)

    # Sort the fetched_blocks list based on the 'time' key in descending order of time, with the latest block first
    sorted_blocks = sorted(fetched_blocks, key=lambda x: x['time'], reverse=True)

    # Returns the first element of the sorted_blocks list, which is the latest block produced
    return sorted_blocks[0]

    

def check_Block_produced_in_6hrs(pool_id):

    log_print("\nChecking If any Blocks have been produced in 6 hours")

    latest_block = fetch_latest_block(pool_id)

    current_time = int(time.time())
    time_difference = current_time - latest_block['time']

    time_limit = 6 * 60 * 60

    if(time_difference > time_limit):

        for User_chatid in chatID:
            message = "!!!ALERT!!! \nNo Blocks produced in the last 6 hours"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"
            requests.get(url).json()

        log_print(message)

    else:

        for User_chatid in chatID:
            message = "Blocks have been produced in the last 6 hours"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"
            requests.get(url).json()

        log_print(message)


def compare_scheduled_and_fetched_blocks(pool_id):

    log_print("\nChecking if all the Scheduled Blocks have been produced or not")

    scheduled_blocks = read_scheduled_blocks('LeadershipSchedule.txt')
    blocks_within_epoch = fetch_blocks_within_epoch(pool_id)

    Missing_Blocks = []
    # for fetchedBlock in blocks_within_epoch:
    #     if fetchedBlock not in scheduled_blocks:
    #         Missing_Blocks.append(fetchedBlock[0])

    for scheduledblock in scheduled_blocks:
        if scheduledblock not in blocks_within_epoch:
            Missing_Blocks.append(scheduledblock[0])


    print(len(Missing_Blocks)) 

    if(len(Missing_Blocks) > 0):
        for User_chatid in chatID:
            message = f"!!!ALERT!!! \n\nScheduled blocks with the below SlotNos are missing in the current Epoch\n\n{Missing_Blocks}"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"
            requests.get(url).json()

        log_print(Missing_Blocks)
    
    else:
        for User_chatid in chatID:
            message = "All the Scheduled blocks have been successfully produced in the current Epoch"
            url = f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={User_chatid}&text={message}"

        requests.get(url).json()
    
 

