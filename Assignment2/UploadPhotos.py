import json
import boto3
import base64

bucket = '6225-photo-manager'

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    response_body = ''
    try:
        data = json.loads(event['body'])
        filename = data['name']
        image = base64.b64decode(data['file'])

        s3_response = s3_client.put_object(Bucket=bucket, Key=filename, Body=image)
        response_body = filename + " uploaded"
    except Exception as e:
        response_body = str(e)
    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }
