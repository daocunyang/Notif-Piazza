from piazza_api import Piazza
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


'''
    TODO: complete the following function to check whether the current post 
          is relevant to the current topic
    topic - the topic that the user is interested in (e.g. BM25, PLSA, etc)
    text_vector - an array of strings representing current post
                  text_vector[0] = title of the post
                  text_vector[1] = main content of the post 
                  text_vector[2:] = the students' answer, the instructors' answer, all other comments
    return value: True if relevant, False otherwise
'''


def isRelevant(topic, text_vector):
    if topic in text_vector[0] + text_vector[1] + text_vector[3]:
        return True
    return False

'''
    Calculates the similarity between a topic and a sentence([paragraph)
    topic - the topic that the user is interested in (e.g. BM25, PLSA, etc)
    sentence - a sentence that we want to know the similariy of
    return value: A number indicating the similarity.
'''
def calc_similarity(topic, sentence):
    # Need to be implemented better:
    # My idea: Suppose the topic is a k-gram word
    # Try to find the best matching from k-gram to (k-1, k-2) to 1-gram between the topic and the sentence
    # Best matching is defined as: whether a exact n-gram word appeared in sentence whenever n is >= 2.
    ## (Therefore this is either 0 or 1) and the highest similar word similarity for 1-gram word. (Real Value (0, 1))
    # Assign different weights to this matching: this part should be carefully designed
    # Below is a super naive version.
    if topic in sentence:
        return 1
    return 0


'''
    Calculates the similarity between a single! topic and a post
    topic - the topic that the user is interested in (e.g. BM25, PLSA, etc)
    text_vector - an array of strings representing current post
                  text_vector[0] = title of the post
                  text_vector[1] = main content of the post
                  text_vector[2:] = the students' answer, the instructors' answer, all other comments
    return value: A number indicating the similarity.
'''

def pure_score(topic, text_vector):
    # All number chosen arbitrary
    if topic == "":
        return 0.0
    _score = 0.0

    # Somewhere needs to be fixed, text vector should always contain at least 4 elements,
    # even if student/instructor do not answer.(that entry should be "")
    while text_vector.__len__() < 4:
        text_vector.append("")
    _score += 3 * calc_similarity(topic, text_vector[0]) + 2 * calc_similarity(topic, text_vector[1]) + \
              1.5 * calc_similarity(topic, text_vector[3]) + 1 * calc_similarity(topic, text_vector[2]) + \
              0.5*sum([calc_similarity(topic, _comment) for _comment in text_vector[4:]])
    return _score


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
    with open("test.txt", "w") as f:
        max_cid = 0
        # get limit+1 posts. E.g. limit=10 will only get you 9 posts
        posts = course.iter_all_posts(limit=21)

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

            f.write(title + "\n")
            f.write(main_text + "\n")

            text_vector.append(title.strip())
            text_vector.append(main_text.strip())

            for child in post["children"]:
                if child.has_key("history"):
                    tmp = child["history"][0]
                    if tmp.has_key("content"):
                        text = tmp["content"].encode("utf-8")
                        text = cleanHtml(text)
                        text_vector.append(text.strip())
                        f.write(text + "\n")

                if child.has_key("subject"):
                    text = child["subject"].encode("utf-8")
                    text = cleanHtml(text)
                    text_vector.append(text.strip())
                    f.write(text + "\n")

                if child.has_key("children"):
                    for c in child["children"]:
                        text = c["subject"].encode("utf-8")
                        text = cleanHtml(text)
                        text_vector.append(text.strip())
                        f.write(text + "\n")
            scores = []
            for topic in topics:
                score = pure_score(topic, text_vector)
                scores.append(score)
            # Could possibly add some weights for each topic
            result.append([sum(scores), text_vector])
    print sorted(result, key = lambda x : x[0], reverse=True)
    f.close()
    data[2] = max_cid
    with open("prepare.txt", "w") as f:
        f.write(data[0])
        f.write(data[1])
        f.write(str(data[2]))
        f.close()

    print "done!\n"
