import feedparser, datetime, time, re, os, urllib, argparse, json, sys, requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def help_menu():
    parser = argparse.ArgumentParser(description="TempMailSpy v1.0", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-cf', "--config_file", type=argparse.FileType('r'), help='Initial Config File')
    parser.add_argument('-bt', "--backup_time", type=int, help='How many minutes does the script run?', default=1)
    parser.add_argument('-rd', "--request_delay", type=int, help='Delays between requests(second)', default=5)
    parser.add_argument('-m', "--mode", type=str, help='Mode? Grep/All', default='G', choices=['G','A'])
    parser.add_argument('-n', "--notification", type=str, help='Notification', choices=['Telegram','Slack'])

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        global args
        global json_file_data
        global backup_time
        global request_delay
        global mode
        global save
        global notification

        args = parser.parse_args()
        json_file_data = json.loads(args.config_file.read())  # read config
        backup_time = args.backup_time
        request_delay = args.request_delay
        mode = args.mode
        notification = args.notification

    return args

def save_results(results, output_json):
    # Write the results to a JSON file
    with open(output_json, 'w') as json_file:
        if results:
            json.dump(results, json_file, indent=4)
        else:
            print("No results to write to the file.")

def notify_telegram(msg):
    msg_new = quote(msg)
    token = json_file_data['Main']['Token']['Telegram']['Telegram Token']
    chatid = json_file_data['Main']['Token']['Telegram']['Telegram Chat ID']
    command = "curl -s -X POST" + " \"https://api.telegram.org/bot" + str(token) + "/sendMessage?chat_id=" + str(chatid) + "&text=" + msg_new +"\""+ " >/dev/null"
    os.system(command)

def notify_slack(msg):
    token = json_file_data['Main']['Token']['Slack']['Slack Bot User OAuth Token']
    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel="#general",text=msg)
    except SlackApiError as e:
        print(f"Hata oluştu: {e.response['error']}")



def yopmail():
    log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    greps = json_file_data['Main']['Keywords']  # Get Grep Keywords
    Mail_Links = json_file_data['Main']['Mail_Links']['YOPMail']  # Get Mail Links
    __ = (len(Mail_Links) * 15) * (int(backup_time * 60) / int(request_delay))
    zib = int(__)
    result_mail_output = [[None for _ in range(5)] for _ in range(zib)]

    print("\n" + "The time that request has been made " + log_time + "\n")
    print("---------------------------------------------------------\n")
    print("Finding Gems! - yopMail")

    start_time = time.time()
    end_time = start_time + backup_time * 60
    index = 0
    result_links = set()  # to store links for checking uniqueness
    while time.time() < end_time:
        for bg in range(0, len(Mail_Links)):
            yopMailRSS = feedparser.parse(Mail_Links[bg])

            for x in range(0, len(yopMailRSS.entries)):
                yopMailRSS_mails = yopMailRSS.entries[x]
                if mode == "G":
                    for aa in range(0, len(greps)):
                        if re.search(greps[aa], yopMailRSS_mails.title):
                            if yopMailRSS_mails.link in result_links:
                                #print("This link is already in the array: " + yopMailRSS_mails.link)
                                continue
                            result_links.add(yopMailRSS_mails.link)
                            print("\n" + greps[aa] + " Found!")
                            print("Request_Time => " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            print("Mail Title => " + yopMailRSS_mails.title)
                            print("Mail_Sender => " + yopMailRSS_mails.summary)
                            print("Mail_Link => " + yopMailRSS_mails.link)
                            print("Telegram Link => " + urllib.parse.quote(yopMailRSS_mails.link))  # For Telegram
                            result_mail_output[index][0] = "YOPMail"
                            result_mail_output[index][1] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            result_mail_output[index][2] = yopMailRSS_mails.title
                            result_mail_output[index][3] = yopMailRSS_mails.summary
                            result_mail_output[index][4] = yopMailRSS_mails.link
                            if notification == "Telegram":
                                notify_telegram("Gem Found!( Keyword = "+greps[aa]+"\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])

                            if notification == "Slack":
                                notify_slack("Gem Found!( Keyword = "+greps[aa]+"\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])

                            index = index + 1
                else:
                    if yopMailRSS_mails.link in result_links:
                        #print("This link is already in the array: " + yopMailRSS_mails.link)
                        continue
                    result_links.add(yopMailRSS_mails.link)
                    print(" Found!")
                    print("Request_Time " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    print("Mail Title " + yopMailRSS_mails.title)
                    print("Mail_Sender " + yopMailRSS_mails.summary)
                    print("Mail_Link " + yopMailRSS_mails.link)
                    print("Telegram Link " + urllib.parse.quote(yopMailRSS_mails.link))  # For Telegram
                    result_mail_output[index][0] = "YOPMail"
                    result_mail_output[index][1] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result_mail_output[index][2] = yopMailRSS_mails.title
                    result_mail_output[index][3] = yopMailRSS_mails.summary
                    result_mail_output[index][4] = yopMailRSS_mails.link
                    if notification == "Telegram":
                        notify_telegram("\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])
                    if notification == "Slack":
                            notify_slack("\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])
                    index = index + 1

        time.sleep(request_delay)

    print("\n ---yopMAIL FINISHED---\n")
    results = []  # This list will store the results in dictionary format

    for y in range(len(result_mail_output)):
        if result_mail_output[y][0] is not None:
            result_dict = {
                "MailType": result_mail_output[y][0],
                "RequestTime": result_mail_output[y][1],
                "MailTitle": result_mail_output[y][2],
                "MailSender": result_mail_output[y][3],
                "MailLink": result_mail_output[y][4],
            }
            results.append(result_dict)
    return results


def tempmail_plus():
    log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    greps = json_file_data['Main']['Keywords']
    Mail_Links2 = json_file_data['Main']['Mail_Links']['TempMail_Plus']
    __ = (len(Mail_Links2) * 15) * (int(backup_time * 60) / int(request_delay))
    zib = int(__)
    result_mail_output = [[None for _ in range(5)] for _ in range(zib)]

    print("\n" + "The time that request has been made " + log_time + "\n")
    print("---------------------------------------------------------\n")
    print("Finding Gems! - Tempmail_Plus")

    start_time = time.time()
    end_time = start_time + backup_time * 60
    index = 0
    result_links = set() 
    result_mail_ids = set()  # to store mail ids for checking uniqueness
    while time.time() < end_time:
        for gb in range(0, len(Mail_Links2)):
            response = requests.get(Mail_Links2[gb])
            if response.status_code == 200:
                data = response.json()
                for xz in range (len(data["mail_list"])):
                    if mode == "G":
                        for aa in range(0, len(greps)):
                            if re.search(greps[aa], data["mail_list"][xz]["subject"], re.I):
                                if data["mail_list"][xz]["mail_id"] in result_mail_ids:
                                    #print(f"This mail_id is already in the array: {data['mail_list'][xz]['mail_id']}")
                                    continue
                                result_mail_ids.add(data["mail_list"][xz]["mail_id"])
                                print("\n" + greps[aa] + " Found!")
                                print("Request_Time => " + data["mail_list"][xz]["time"])
                                print("Mail Title => " + data["mail_list"][xz]["subject"])
                                print("Mail_Sender => " + data["mail_list"][xz]["from_mail"])
                                print("Mail_Sender_Name => " + data["mail_list"][xz]["from_name"])
                                print("Mail Link: "+"https://tempmail.plus/en/#!mail/"+str(data["mail_list"][xz]["mail_id"]))
                                result_mail_output[index][0] = "TempMail_Plus"
                                result_mail_output[index][1] = data["mail_list"][xz]["time"]
                                result_mail_output[index][2] = data["mail_list"][xz]["subject"]
                                result_mail_output[index][3] = data["mail_list"][xz]["from_mail"]
                                result_mail_output[index][4] = "https://tempmail.plus/en/#!mail/"+str(data["mail_list"][xz]["mail_id"])
                                if notification == "Telegram":
                                    notify_telegram("Gem Found!( Keyword = "+greps[aa]+"\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])
                                if notification == "Slack":
                                    notify_slack("Gem Found!( Keyword = "+greps[aa]+"\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])
                                index = index + 1
                    else:
                        if data["mail_list"][xz]["mail_id"] in result_mail_ids:
                            #print(f"This mail_id is already in the array: {data['mail_list'][xz]['mail_id']}")
                            continue
                        result_mail_ids.add(data["mail_list"][xz]["mail_id"])
                        print(" Found!")
                        print("Request_Time: "+data["mail_list"][xz]["time"])
                        print("Mail_Title: "+data["mail_list"][xz]["subject"])
                        print("Mail_Sender: "+data["mail_list"][xz]["from_mail"])
                        print("Mail_Sender_Name: "+data["mail_list"][xz]["from_name"])
                        print("Mail Link: "+"https://tempmail.plus/en/#!mail/"+str(data["mail_list"][xz]["mail_id"]))
                        result_mail_output[index][0] = "TempMail_Plus"
                        result_mail_output[index][1] = data["mail_list"][xz]["time"]
                        result_mail_output[index][2] = data["mail_list"][xz]["subject"]
                        result_mail_output[index][3] = data["mail_list"][xz]["from_mail"]
                        result_mail_output[index][4] = "https://tempmail.plus/en/#!mail/"+str(data["mail_list"][xz]["mail_id"])
                        if notification == "Telegram":
                            notify_telegram("\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])
                        if notification == "Slack":
                            notify_slack("\nService: "+result_mail_output[index][0]+"\nRequest Time: "+result_mail_output[index][1]+"\nMail Title: "+result_mail_output[index][2]+"\nMail Sender: "+result_mail_output[index][3]+"\nMail Link::"+result_mail_output[index][4])
                        index = index + 1
            else:
                print(f"Request failed with status code {response.status_code}")

        time.sleep(request_delay)

    print("\n ---TEMPMAIL_PLUS FINISHED---\n")
    results = []  # This list will store the results in dictionary format

    for y in range(len(result_mail_output)):
        if result_mail_output[y][0] is not None:
            result_dict = {
                "MailType": result_mail_output[y][0],
                "RequestTime": result_mail_output[y][1],
                "MailTitle": result_mail_output[y][2],
                "MailSender": result_mail_output[y][3],
                "MailLink": result_mail_output[y][4],
            }
            results.append(result_dict)

    return results


# Execution starts from here
if __name__ == "__main__":
    help_menu()
    if notification == "Telegram":
        notify_telegram('The script has started')
    if notification == "Slack":
        notify_slack('The script has started')
    

    with ThreadPoolExecutor() as executor:
        yopmail_future = executor.submit(yopmail)
        tempmail_plus_future = executor.submit(tempmail_plus)
        yopmail_results = yopmail_future.result()
        tempmail_plus_results = tempmail_plus_future.result()
        combined_results = yopmail_results + tempmail_plus_results
        log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = log_time+"_results.json"
        save_results(combined_results, file_name)
    if notification == "Telegram":
        notify_telegram('The script has finished')
    if notification == "Slack":
        notify_slack('The script has started')
    
