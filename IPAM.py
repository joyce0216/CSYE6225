import json
import boto3

# sqs reference: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
sqs = boto3.client('sqs')
ipam_queue_url = 'https://sqs.us-east-2.amazonaws.com/670096847783/IPAM.fifo'
fifo_message_group_id = 'static_fifo_message_group_id'

def lambda_handler(event, context):
    operation = event['operation']
    response_body = ''
    
    if operation == 'Set':
        ip_addresses = event['ip_addresses']
        send_sqs_messages(ip_addresses)
        response_body = "Set IP addresses: " + ', '.join(ip_addresses)
    elif operation == "Retrieve":
        try:
            next_available_ip_address = receive_and_delete_sqs_message()
            response_body = "Available IP address: " + next_available_ip_address
        except:
            response_body = "Queue exhausted. No IP address available."
    else:
        response_body = "Operation " + operation + " not supported!"
        
    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }
    
def send_sqs_messages(ip_addresses):
    entries = [{
        'Id':ip_address.replace('.', ''),
        'MessageBody':ip_address,
        'MessageDeduplicationId':ip_address,
        'MessageGroupId':fifo_message_group_id
    } for ip_address in ip_addresses]
    
    sqs.send_message_batch(QueueUrl=ipam_queue_url, Entries=entries)

def receive_and_delete_sqs_message():
    response = sqs.receive_message(QueueUrl=ipam_queue_url)
    message = response['Messages'][0]
    
    receipt_handle = message['ReceiptHandle']
    sqs.delete_message(QueueUrl=ipam_queue_url, ReceiptHandle=receipt_handle)
    
    return message['Body']
    
