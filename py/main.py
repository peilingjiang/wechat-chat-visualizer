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

    mode = 3
    width = 6000
    height = 2000
    colors = [
        [0.0118, 0.3529, 0.4549],
        [0.9412, 0.0196, 0.3216],
        [0.9, 0.6]
    ]

    illustration = plt.figure()
    ax = illustration.add_subplot(111, aspect = 'equal')
    ax.set_xlim([0, width])
    ax.set_ylim([0, height])

    maxNum = max([sum(x) for x in db.values()])
    unitHeight = height / maxNum
    unitWidth = width / (len(db) + 1)

    for day in db:
        marker = 0
        if mode == 1:
            # Mode 1 Overlap
            maxInd = db[day].index(max(db[day])) # Either Send or Receive are larger
            for i in range(maxInd, maxInd + 2 * (-1) ** maxInd, (-1) ** maxInd):
                ax.add_patch(patches.Rectangle(
                    (day * unitWidth, 0),
                    unitWidth,
                    db[day][i] * unitHeight,
                    linewidth = 0,
                    color = tuple(colors[i] + [colors[2][marker]])
                ))
                marker += 1
        
        elif mode == 2:
            # Mode 2 Accumulate
            minInd = db[day].index(min(db[day]))
            for i in range(minInd, minInd + 2 * (-1) ** minInd, (-1) ** minInd):
                ax.add_patch(patches.Rectangle(
                    (day * unitWidth, marker * db[day][1 - i] * unitHeight),
                    unitWidth,
                    db[day][i] * unitHeight,
                    linewidth = 0,
                    color = tuple(colors[i] + [colors[2][0]])
                ))
                marker += 1

        elif mode == 3:
            # Mode 3 Mirror
            for i in range(2):
                ax.add_patch(patches.Rectangle(
                    (day * unitWidth, height / 2),
                    unitWidth,
                    db[day][i] * unitHeight * (-1) ** (1 - i),
                    linewidth = 0,
                    color = tuple(colors[i] + [colors[2][0]])
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

