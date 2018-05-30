import boto3
import db

def main():
    s3 = boto3.client('s3')
    # makeBucket(s3, 'autogoaltracker')
    s3.upload_file('cv/gifs/m3.gif', 'autogoaltracker', 'm3.gif')
    getBuckets(s3)

def uploadGifs(client, gifs, bucket):
    for gif in gifs:
        client.upload_file(gif, bucket, gif, ExtraArgs={'ACL':'public-read'})

def uploadFile(client, bucket_name, filename):
    print (client.upload_file(filename, bucket_name, filename))

def getBuckets(client):
    response = client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    print("Bucket List: %s" % buckets)

def makeBucket(client, name):
    client = boto3.client('s3')
    print(client.create_bucket(Bucket=name) )

if __name__ == '__main__':
    main()
