import sys
import os
import json
import base64
from multiprocessing import Pool
import requests



def upload_photo(filepath):
    with open(filepath, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read())

    payload = {
        'name': os.path.basename(filepath),
        'file': encoded_string.decode('utf-8')
    }

    url = 'https://yjyc4stoh8.execute-api.us-east-2.amazonaws.com/prod/upload-photos'
    response = requests.post(url, data = json.dumps(payload))

    print(response.text)


def download_photos():
    url = 'https://yjyc4stoh8.execute-api.us-east-2.amazonaws.com/prod/download-photos'
    print(json.dumps(requests.get(url).json(), indent = 4, sort_keys = True))

def print_usage():
    print("Usage: list")
    print("List all images")
    print("")
    print("Usage: upload IMAGE [...]")
    print("Upload images")

if __name__ == "__main__":

    if len(sys.argv) == 2:
        args = sys.argv[1].split()
        if args[0] == 'list':
            download_photos()
        elif args[0] == 'upload' and len(args) > 1:
            for arg in args[1:]:
                upload_photo(arg)
        else:
            print_usage()
    else:
        print_usage()
