import sqlite3
from datetime import datetime
import os.path
import io

conn = sqlite3.connect("/Users/user/OneDrive/Chat Fiction Project/Hillary Clinton Emails/database/database.sqlite")
cursor = conn.cursor()
cursor.execute("""
    SELECT
         MetadataSubject,
         dense_rank() over (
             order by MetadataSubject
             ) as ThreadId,
         MetadataTo,
         Persons.Name,
         MetadataDateSent,
         ExtractedDateSent,
         ExtractedBodyText
         FROM Emails
         JOIN Persons on Persons.id = Emails.SenderPersonId
         Order by ThreadId, MetadataDateSent desc, ExtractedDateSent desc
         """
         )
rows = cursor.fetchall()

def conversation_block(subject, sender, receipient, sent_date, body): #formats the emails for Twee
    return("""
    Subject: {0}
    From: {1}
    To: {2}
    Sent: {3}

    {4}
    <hr>
    """.format(subject, sender, receipient, sent_date, body)
)

def cont_block(body_text):  #wraps the continue macro around text
    return("""
    <<cont keypress append>>
        {0}
    <</cont>>
    """.format(body_text)
    )

def thread_block(line, msg_array): #creates the thread block
    thread_text = (\
            cont_block(conversation_block(\
            msg_array[line][0],\
            msg_array[line][3],\
            msg_array[line][2],\
            msg_array[line][5],\
            msg_array[line][6]\
            )))
    
    line = line + 1

    while msg_array[line][1] == msg_array[line-1][1] and line < len(msg_array):
        thread_text = (\
            cont_block(conversation_block(\
            msg_array[line][0],\
            msg_array[line][3],\
            msg_array[line][2],\
            msg_array[line][5],\
            msg_array[line][6]\
            ) + thread_text))
        line = line + 1 
              
    return (line, thread_text)

def thread_page(thread_title, message_block):
    return("""
    :: {0}
    [[Back|Main]]
    
    {1}
    """.format(thread_title, message_block)
    )

def write_twee_thread(thread_title, body_text):
    save_path = 'C:/Users/user/OneDrive/Chat Fiction Project/Hillary Clinton Emails/threads/'
    completeName = os.path.join(\
        save_path,\
        "".join([c for c in thread_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()\
        +".txt")         
    
    with io.open(completeName, "w", encoding="utf-8") as f:
        f.write(body_text)

    return()

row_tracker = 0

while row_tracker < len(rows) and row_tracker < 400:
    block = thread_block(row_tracker, rows)
    row_tracker = block[0] + 1
    print(row_tracker)
    print(thread_page(rows[row_tracker][0], block[1]))
    write_twee_thread(rows[row_tracker][0], thread_page(rows[row_tracker][0], block[1]))