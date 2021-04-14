import os
import json
import uuid
import boto3
from multiprocessing import Process, Pipe
import requests
from exif import Image


bucket = '6225-photo-manager'

google_maps_api_key = 'AIzaSyA1E0Q07cNt3jorqCmtiWGNZ_sVpDR2ZNs'

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    response_body = 'a'
    try:
        filenames = [key['Key'] for key in s3_client.list_objects(Bucket=bucket)['Contents']]

        # create a list to keep all processes
        processes = []
        # create a list to keep connections
        parent_connections = []

        # create a process per instance
        for filename in filenames:
            # create a pipe for communication
            parent_connection, child_connection = Pipe()
            parent_connections.append(parent_connection)

            # create the process, pass instance and connection
            process = Process(target=get_info, args=(filename, child_connection))
            processes.append(process)

        # start all processes
        for process in processes:
            process.start()

        # make sure that all processes have finished
        for process in processes:
            process.join()

        response_body = [parent_connection.recv()[0] for parent_connection in parent_connections]
    except Exception as e:
        response_body = str(e)

    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }


def get_info(filename, connection):
    url = 'https://{bucket}.s3.us-east-2.amazonaws.com/{filename}'.format(bucket = bucket, filename = filename)

    # Download file to tmp
    filepath = '/tmp/{uuid}-{filename}'.format(uuid = uuid.uuid4(), filename = filename)
    s3_client.download_file(bucket, filename, filepath)

    # Get metadata
    info = get_metadata(filepath)
    info['url'] = url
    info['User File'] = filename
    connection.send([info])
    connection.close()


def get_location(latitude, longitude):
    base = 'https://maps.googleapis.com/maps/api/geocode/json'
    key = 'key={google_maps_api_key}'.format(google_maps_api_key = google_maps_api_key)
    parameters = 'latlng={latitude},{longitude}&sensor={sensor}'.format(
        latitude = latitude,
        longitude = longitude,
        # Fake sensor
        sensor = 'true'
    )
    url = '{base}?{key}&{parameters}'.format(base = base, key = key, parameters = parameters)
    # First result should be precise enough
    return json.loads(requests.get(url).text)['results'][0]['formatted_address']


def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return degrees + minutes + seconds


def get_metadata(filepath):
    metadata = {}
    # read the image data using exif
    with open(filepath, "rb") as image_file:
        image = Image(image_file)

    metadata = {
        'Date Taken': image.get('datetime_digitized'),
        'Device Used': image.get('model'),
        'Location': get_location(
            get_decimal_from_dms(image.get('gps_latitude'), image.get('gps_latitude_ref')),
            get_decimal_from_dms(image.get('gps_longitude'), image.get('gps_longitude_ref')),
        )
    }

    return metadata