#!/usr/bin/python3
import requests
import json
from bs4 import BeautifulSoup

def main():
    auth_f = open("./config/auth.json", "r")
    auth = json.load(auth_f)

    if auth["username"] == "" or auth["password"] == "":
        print("username or password is empty!")
        print("Did you add your username and password in \"config/auth.json\" file?")
        exit()

    login_credential = {
        "username":auth["username"],
        "password":auth["password"]
    }
    
    with requests.Session() as ses:
        print("Sending login request...")
        rsp = ses.post("http://lms.ui.ac.ir/login", data=login_credential)
        if "برنامه هفتگی" in rsp.text:
            print("Logged in")
            cl = json.load(open("./config/class.json", "r"))
            for cl_code in cl:
                rsp = ses.get(f"http://lms.ui.ac.ir/group/{cl_code}")
                extract_data(rsp, cl_code)

        elif "مشخصاتی که وارد کرده اید معتبر نمی باشد" in rsp.text:
            print(f"Login Failed, your username/password is incorrect status_code={rsp.status_code}")
            exit()
        elif rsp.status_code == 404:
            print(f"Not found, the page might've been moved! status_code={rsp.status_code}")
            exit()
        else:
            print(f"Unexpected error occured! status_code={rsp.status_code}")

  

#         rsp_txt = f.read()
#         

def extract_data(res, cl_code):
    FEED_SELECTOR        = "#activity-feed > li.wall-action-item div.feed_item_body"
    AUTHOR_NAME_SELECTOR = "span.feed_item_posted > a.feed_item_username"
    MSG_BODY_SELECTOR    = "span.feed_item_posted > span.feed_item_bodytext"
    TIMESTAMP_SELECTOR   =  "li.feed_item_option_date span.timestamp"

    site_soup = BeautifulSoup(res.text, 'html.parser')
        
    authors    = site_soup.select(FEED_SELECTOR + " " + AUTHOR_NAME_SELECTOR)
    messages   = site_soup.select(FEED_SELECTOR + " " + MSG_BODY_SELECTOR)
    timestamps = site_soup.select(FEED_SELECTOR + " " + TIMESTAMP_SELECTOR)

    # considering every message has the author, message body and timestamp
    msg_count = len(authors)

    for i in range(msg_count):
        authors[i]    = authors[i].text
        messages[i]   = messages[i].text
        timestamps[i] = timestamps[i].text

    # Creates the file in case of absence
    file = open(f"./latest_fetch/class_{cl_code}_timestamps.txt", "a")
    file.close()

    # Takes a copy of the old file content
    file = open(f"./latest_fetch/class_{cl_code}_timestamps.txt", "r")
    file_old = file.read()
    file.close()

    cl = json.load(open("./config/class.json", "r"))

    if file_old == f"{timestamps}":
        print(f"{cl_code}: No new messages in class {cl[cl_code]}")
    else:
        print(f"{cl_code}: You have new messages in class {cl[cl_code]}!")

        with open(f"./latest_fetch/class_{cl_code}_timestamps.txt", 'w') as f:
            f.write(f"{timestamps}")


if __name__ == "__main__":
    main()
