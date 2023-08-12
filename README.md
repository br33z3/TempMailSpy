# TempMailSpy

## Description

TempMailSpy is a Python-based tool designed to monitor and extract mail data from temporary mail platforms such as YOPMail and TempMail_Plus. The program allows you to specify keywords to search for within the subject lines of incoming mail messages and supports both Telegram and Slack for notifications.

The main features of TempMailSpy are:

1. Ability to set custom request delays and backup times.
2. Flexible filtering mode with two options, 'Grep' (searches for specific keywords) and 'All' (retrieves all available mail data).
3. Automated notifications via Slack or Telegram when matches are found.

## Dependencies

The program requires the following libraries to be installed:

- `feedparser`
- `requests`
- `argparse`
- `slack_sdk`

## Tested On
- `Python: 3.10.9`
- `feedparser: 6.0.10`
- `requests: 2.31.0`
- `argparse: 1.4.0`
- `slack_sdk: 3.19.5`

You can install them using pip:
```shell
pip3 install -r requirements.txt
```
## Usage
First, configure the settings of the program according to your needs by modifying the provided config file.

You can run the program with the following command:
```shell
python main.py -cf config.json -bt 1 -rd 5 -m G -n Slack
```
Where:
- `-cf or --config_file : Initial Config File`
- `-bt or --backup_time : How many minutes does the script run? (default=1)`
- `rd or --request_delay : Delays between requests in seconds (default=5)`
- `m or --mode : Mode (G for Grep or A for All)`
- `n or --notification : Notification method (Slack or Telegram)`


## Notifications

To receive notifications, you'll need to provide valid credentials for your preferred platform (Slack or Telegram) in the configuration file.

## License
This project is licensed under the MIT License.
