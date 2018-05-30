import db, findGoals, host, goal2MT, movEdit
import boto3
dbase ='goals.db'
folder = 'gifs0526'
bucket='autogoaltracker'
hostURL='https://s3.amazonaws.com/autogoaltracker/'
from os import listdir
from os.path import isfile, join


isLive = True #True is paid, False is sandbox
mFolder ='/Volumes/Woolf-Backup/_Soccer/052418/'
def main():

    movs = [join(mFolder, f) for f in listdir(mFolder) if isfile(join(mFolder,  f)) and 'MP4' in f]
    # movs =[mFolder + 'GP038537.MP4']
    conn = db.getConn(dbase)
    #TODO get list of movies
    # movs = ['/Users/swoolf/GitHub/SoccerHighlights/cv/Videos/180517_v1.MP4','/Users/swoolf/GitHub/SoccerHighlights/cv/Videos/180517_v2.MP4']
    #setUp MT/S3 Clients
    session = boto3.Session()
    client = goal2MT.getClient(session, isLive)
    s3 = boto3.client('s3')

    #Find potential goals and host on S3
    # findGoals.mov2gifs(movs, conn, folder)
    # gifs = db.list_gifs_by_status(conn, 'gif')
    # host.uploadGifs(s3, gifs, bucket)
    #
    # #
    # # #publish to MT
    # goal2MT.urls2MT(client, conn, hostURL, gifs)
    # db.printDB(conn)

    # check MT
    # goal2MT.updateMTanswers(client, conn)
    # db.printDB(conn)

    # compileVideo and post to youTube
    clipsInfo = db.getClips(conn)
    print(clipsInfo)
    movEdit.compileMov('soccerVideo.MP4', clipsInfo)

    #TODO Post to youTube

if __name__ == '__main__':
    main()
