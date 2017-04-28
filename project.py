from piazza_api import Piazza
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mining import *
import re, smtplib, sys, time

'''
    To receive email notifications, please correctly fill in your credentials below, and notice:
    1) Do not use illinois.edu email account as sender
    2) Ensure 2-Step Verification is turned OFF
    3) Go to https://myaccount.google.com/lesssecureapps, and turn on the option to "Allow less secure apps"
'''
sender = ""
receiver = ""
password = ""


# https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
def cleanHtml(raw_text):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_text)

    return cleantext


def generatequeries():
    ## To do: return students' queries into each query per line in .txt
    pass




def sendEmail(course, cid):
    url = "https://piazza.com/class/" + course + "?cid=" + cid
    body = "We've found the following topic(s) that you might be interested in: " + url

    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Piazza Notification Tool - New Topic Posted"
        msg['From'] = sender
        msg['To'] = receiver
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

        server.close()
        log_msg = time.strftime("%c") + "-   " + url + "\n\n"
        with open("log.txt", "a") as f:
            f.write(log_msg)
            f.close()
            # print "email sent!"

    except:
        # something went wrong, write error to log
        print "ERROR: email delivery failed"
        log_msg = time.strftime("%c") + "   -   ERROR: email delivery failed\n\n"
        with open("log.txt", "a") as f:
            f.write(log_msg)
            f.close()
        sys.exit()

if __name__ == "__main__":
    print "starting...\n"
    p = Piazza()
    email, password = "", ""
    # Login with credentials, just for ease of testing
    # Create a credential.txt with first line email, second line password
    with open("credential.txt", "r") as f:
        data = f.readlines()
        if len(data) == 2:
            email, password = data
    if email != "" and password != "":
        p.user_login(email=email.rstrip(), password=password.rstrip())
    else:
        p.user_login()

    # cs410 = "iy0x6bnqsx33fe"

    target_course, last_cid = "", 0
    data = list()
    topics = list()

    # read in course url and last post id that we've checked 
    with open("prepare.txt", "r") as f1:
        with open("log.txt", "a") as f2:
            data = f1.readlines()
            if len(data) != 3 or not data[0] or not data[1] or not data[2]:
                info = "ERROR: please make sure you've provided the correct info in correct format in prepare.txt"
                print info
                f2.write(time.strftime("%c") + "   -   " + info + "\n\n")
                sys.exit()
            # separating topics, fixed.
            topics = [x.strip() for x in data[0].split(',')]
            target_course = str(data[1].strip())
            last_cid = int(data[2].strip())

            f2.close()
            f1.close()

    course = p.network(target_course)

    result = []
    with open("./postsdataset/transit.dat", "w") as f:
        max_cid = 0
        # get limit+1 posts. E.g. limit=10 will only get you 9 posts
        posts = course.iter_all_posts(limit=51)

        for post in posts:
            if "#pin" in str(post["history"][0]):
                continue

            cid = str(post["nr"])
            max_cid = max(max_cid, int(cid))
            if int(cid) == last_cid:
                break

            print "cid: " + cid + "\n"

            text_vector = list()
            content = post["history"]
            title = (content[0]["subject"])
            content = content[0]["content"]
            main_text = cleanHtml(content).encode("utf-8")
            f.write("*Title*" + "\n")
            f.write(title + "\n")
            f.write("*Main*"+ "\n")
            f.write(main_text + "\n")

            text_vector.append(title.strip())
            text_vector.append(main_text.strip())
            f.write("*Follows*" + "\n")
            for child in post["children"]:
                if child.has_key("history"):
                    tmp = child["history"][0]
                    if tmp.has_key("content"):
                        text = tmp["content"].encode("utf-8")
                        text = cleanHtml(text)
                        text_vector.append(text.strip())
                        # f.write(text + "\n")
                        f.write(text)

                if child.has_key("subject"):
                    text = child["subject"].encode("utf-8")
                    text = cleanHtml(text)
                    text_vector.append(text.strip())
                    # f.write(text + "\n")
                    f.write(text)


                if child.has_key("children"):
                    for c in child["children"]:
                        text = c["subject"].encode("utf-8")
                        text = cleanHtml(text)
                        text_vector.append(text.strip())
                        # f.write(text + "\n")
                        f.write(text)
            f.write("\n")
            scores = []
            for topic in topics:
                score = pure_score(topic, text_vector)
                scores.append(score)
            # Could possibly add some weights for each topic
            if sum(scores)!= 0:
                result.append([sum(scores), text_vector])
    # where the results are outputed
    print sorted(result, key = lambda x : x[0], reverse=True)


    # change format and transform to .dat for Metapy
    with open("./postsdataset/transit.dat", "r") as f1:
        with open("./postsdataset/postsdataset.dat", "w") as f2:
            line = f1.readline()
            while line:
                if line == "*Title*\n":
                    line = f1.readline()
                    f2.write(line)
                    line = f1.readline() ## To Main line
                    line = f1.readline()
                    while line and line != "*Follows*\n":
                        f2.write(line.strip()+" ")
                        line = f1.readline()
                    f2.write("\n")
                    line = f1.readline()
                    while line and line != "*Title*\n":
                        f2.write(line.strip("\n").strip()+" ")
                        line = f1.readline()
                    f2.write("\n")
        f1.readline()
        f1.close()
    f2.close()


    f.close()
    # data[2] = max_cid
    with open("prepare.txt", "w") as f:
        f.write(data[0])
        f.write(data[1])
        f.write(str(data[2]))
        f.close()

    print "done!\n"
