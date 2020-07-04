import hashlib
import sqlite3
import pandas as pd
from datetime import date, timedelta
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

# Delete the following line if secret.py doesn't exist
from secret import secret


def get_date(createTime):
    return date(1970, 1, 1) + timedelta(seconds = int(createTime))

def build_num_db(msgs):
    """
    Build the database for the numbers of messages for each day.
    """
    dayOne = get_date(min(msgs['CreateTime']))
    days = {} # dict of lists of 2, [num_send, num_receive]
    for i in range(len(msgs)):
        deltaDate = (get_date(msgs['CreateTime'][i]) - dayOne).days
        if deltaDate not in days:
            days[deltaDate] = [0, 0]
        if msgs['Des'][i] == 0:
            # Send
            days[deltaDate][0] += 1
        else:
            # Receive
            days[deltaDate][1] += 1
    return days

def build_num_illustration(db):

    width = 2000
    height = 2000
    colors = [
        (0.0118, 0.3529, 0.4549, 0.5),
        (0.9412, 0.0196, 0.3216, 0.3)
    ]

    illustration = plt.figure()
    ax = illustration.add_subplot(111, aspect = 'equal')
    ax.set_xlim([0, width])
    ax.set_ylim([0, height])

    maxNum = max([sum(x) for x in db.values()])
    unitHeight = height / maxNum
    unitWidth = width / (len(db) + 1)

    for day in db:
        for i in range(2):
            ax.add_patch(patches.Rectangle(
                (day * unitWidth, 0),
                unitWidth,
                db[day][i] * unitHeight,
                linewidth = 0,
                color = colors[i]
            ))
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    illustration.savefig(time.ctime().strip().replace('  ', '_').replace(' ', '_').replace(':', '') + '.png', format = 'png', bbox_inches = 'tight')

if __name__ == "__main__":
    # secret = {
    #     'target': '...' # Original WeChat ID
    # }
    target = secret['target'] # Modify

    # Put 'MM.sqlite' inside 'data' folder
    with sqlite3.connect(r'data/MM.sqlite') as con:
        # TableVer, MesLocalID, MesSvrID, CreateTime, Message, Status, ImgStatus, Type, Des
        # Des == 0 Send out, Des == 1 Receive
        history = pd.read_sql_query("select * from Chat_" + str(hashlib.md5(target.encode()).hexdigest()), con)

        # Numbers of messages
        numDb = build_num_db(history)
        build_num_illustration(numDb)

