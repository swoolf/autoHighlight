import sys
import boto3
import db
import sqlite3
from xml.dom.minidom import parseString

create_hits_in_live = False

environments = {
        "live": {
            "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
            "preview": "https://www.mturk.com/mturk/preview",
            "manage": "https://requester.mturk.com/mturk/manageHITs",
            "reward": "0.01"
        },
        "sandbox": {
            "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
            "preview": "https://workersandbox.mturk.com/mturk/preview",
            "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
            "reward": "0.02"
        },
}
mturk_environment = environments["live"] if create_hits_in_live else environments["sandbox"]

def main():
    profile_name = sys.argv[2] if len(sys.argv) >= 3 else None
    session = boto3.Session(profile_name=profile_name)
    client = session.client(
        service_name='mturk',
        region_name='us-east-1',
        endpoint_url=mturk_environment['endpoint'],
    )

    conn = sqlite3.connect('goals.db')

    # db.delAll(conn, 'goals')
    # db.csv2db(conn, 'gifs.csv')
    # db.printDB(conn)
    #
    # db2MT(client, conn)
    # db.printDB(conn)

    getMTfromDB(client, conn)
    db.printDB(conn)

def getClient(session, isLive):
    mturk_environment = environments["live"] if isLive else environments["sandbox"]
    client = session.client(
        service_name='mturk',
        region_name='us-east-1',
        endpoint_url=mturk_environment['endpoint'],
    )
    return client

def urls2MT(client, conn, baseurl, gifs):
    for gif in gifs:
        url = baseurl + gif
        mtID = url2MT(client, url)
        db.updateMtIDbyID(conn, gif, mtID)

#Take events in DB and post them to MTurk
def db2MT(client, conn):
    c1=conn.cursor()
    c2=conn.cursor()
    for row in c1.execute('SELECT ID, url  FROM goals'):
        print(row)
        ID=row[0]
        mtID = url2MT(client, row[1])
        c2.execute('UPDATE goals SET mtID=?, status="mt" WHERE ID=?', (mtID,ID) )
        conn.commit()

#Given a hosted GIF url, post to MTurk
def url2MT(client, url):
    print(url)
    question_sample = open("my_question.xml", "r").read()
    qs=question_sample.replace("$link", url)
        # Create the HIT
    response = client.create_hit(
        MaxAssignments=1,
        LifetimeInSeconds=600,
        AssignmentDurationInSeconds=6000,
        Reward=mturk_environment['reward'],
        Title='Soccer goal or no goal?',
        Keywords='soccer, futbol, goal',
        Description='Determine if a goal was scored in the GIF',
        Question=qs,
    )

    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    return hit_id

#For events in DB, get MTurk answers, and save to DB
def updateMTanswers(client, conn):
    c1=conn.cursor()
    c2=conn.cursor()
    for row in c1.execute('SELECT ID, mtID  FROM goals WHERE status="mt"'):
        answer=getMTResults(client, row[1])
        ID=row[0]
        if answer:
            c2.execute('UPDATE goals SET isGoal=?, status="decided" WHERE ID=?', (answer,ID) )
            conn.commit()

#Get MTurk answers from Hit ID
def getMTResults(client, hit_id):
    hit = client.get_hit(HITId=hit_id)
    response = client.list_assignments_for_hit(
        HITId=hit_id,
        AssignmentStatuses=['Submitted', 'Approved'],
        MaxResults=10,
        )
    assignments = response['Assignments']
    for assignment in assignments:
        worker_id = assignment['WorkerId']
        assignment_id = assignment['AssignmentId']
        answer_xml = parseString(assignment['Answer'])
        answer = answer_xml.getElementsByTagName('FreeText')[0]
        only_answer = " ".join(t.nodeValue for t in answer.childNodes if t.nodeType == t.TEXT_NODE)
        # print(worker_id, assignment_id, only_answer)
        return only_answer

if __name__ == '__main__':
    main()
