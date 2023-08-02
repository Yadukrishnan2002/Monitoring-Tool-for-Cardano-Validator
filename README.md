
# Monitoring Tool for Cardano Validator

The Luganode Block Monitoring Tool is a robust and indispensable utility meticulously crafted to oversee the block production process on the Luganode blockchain network. Tailored to meet the needs of Luganode node operators, this tool offers seamless monitoring capabilities and timely alerts, making it a crucial asset for ensuring the network's efficiency and reliability. With its powerful features, the Block Monitoring Tool empowers node operators to maintain optimal performance and stay informed about critical block production events in real-time.


## Tech Stack

**Client:** Python

**Api:** BlockFrost Api


## Features

- Block Production Alert: The tool actively tracks block production and sends real-time alerts if blocks have not been produced within the last 6 hours. This feature helps ensure the continuous and smooth functioning of the Luganode network.
- Scheduled Block Comparison: The tool compares the blocks produced with a provided leadership schedule file at every epoch (every 5 days). It meticulously checks for any missed scheduled blocks and promptly sends alerts to the concerned parties.
- Telegram Integration: The tool utilizes the Telegram API to deliver alerts and notifications directly to designated recipients. Stay informed of crucial events in real-time, even while on the go.
- Systemd Service: The Luganode Block Monitoring Tool is implemented as a systemd service, ensuring seamless operation in the background. It runs continuously and efficiently monitors the blockchain, which helps in focusing on other critical tasks with peace of mind.


## Code Description

**Main.py:**

The main.py file contains the main script that schedules and runs the block monitoring functions defined in the Block_Monitor.py module. It uses the schedule library to schedule two functions: check_Block_produced_in_6hrs to run every 6 hours, and compare_scheduled_and_fetched_blocks to run every 5 days (120 hours). The script fetches blocks from the Cardano blockchain, monitors block production, and sends alerts using the Telegram API.

**Block_Monitor.py**

The Block_Monitor.py file defines several functions used for monitoring block production on the Cardano blockchain. It interacts with the Cardano Mainnet API provided by Blockfrost and utilizes the datetime, time, schedule, and logging modules for various functionalities. The functions in this module fetch block data, compare scheduled and fetched blocks, and send alerts to users via Telegram when blocks are not produced in the expected time frames. It also maintains a log file to record monitoring events. The script can be used as a systemd service to run in the background and continuously monitor block production for a specific pool.



In addition, further in-depth code details and explanations will be provided within the code itself, in the form of comments, to offer a more comprehensive understanding of the functionalities and logic behind each function and step


## Run Locally

Clone the project

```bash
  git clone https://github.com/Yadukrishnan2002/Monitoring-Tool-for-Cardano-Validator.git
```

Go to the project directory

```bash
  cd Monitoring-Tool-for-Cardano-Validator
```

Install dependencies

```bash
  pip install schedule
```

### Run the monitoring tool directly

Make sure to replace all the placeholders with their respective values before running the component

Run the tool

```bash
  python main.py
```

### Configure the monitoring tool as systemd service (Mac OS)

Move the plist file to to the LaunchDaemons directory

```bash
  sudo mv com.block_monitoring_tool.plist /Library/LaunchDaemons/
```
Set the ownership of the plist file to the root user and the wheel group

```bash
  sudo chown root:wheel /Library/LaunchDaemons/com.block_monitoring_tool.plist
```

Set read and write permissions for the root user and read-only permisions for others

```bash
  sudo chmod 644 /Library/LaunchDaemons/com.block_monitoring_tool.plist
```

Enable the Block monitoring tool to run as a background agent during system startup using the MacOS launchd service management system

```bash
  sudo launchctl load /Library/LaunchDaemons/com.block_monitoring_tool.plist
```

Check the status of the Block monitoring tool service if it is loaded and running successfully.

```bash
  sudo launchctl list | grep com.block_monitoring_tool
```

Now the service will be up and running in the background. 

To stop the service from launchd

```bash
  sudo launchctl unload /Library/LaunchDaemons/com.block_monitoring_tool.plist
```

## Contact

**Yadu Krishnan U**

Email: yadus2002@gmail.com


## Acknowledgements

 - [Cardano Documentaton](https://docs.cardano.org/new-to-cardano/introduction/)
 - [Cardano Explorer](https://cexplorer.io/)
 - [BlockFrost API](https://blockfrost.io/)
 - [Telegram API](https://core.telegram.org/bots/api)
