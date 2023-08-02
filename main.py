import schedule
import time
from Block_Monitor import *

#Pool Id of Luganodes for monitoring
POOL_ID = 'pool1qvudfuw9ar47up5fugs53s2g84q3c4v86z4es6uwsfzzs89rwha'

if __name__ == '__main__':
    # Schedule the check_Block_produced_in_6hrs function to run every 6 hours
    schedule.every(6).hours.do(lambda: check_Block_produced_in_6hrs(POOL_ID))

    # Schedule the compare_scheduled_and_fetched_blocks function to run every 5 days (120 hours)
    schedule.every(5).days.do(lambda: compare_scheduled_and_fetched_blocks(POOL_ID))

    while True:
        
        #Checks if any scheduled task is due and execute it
        schedule.run_pending()
        time.sleep(1)
