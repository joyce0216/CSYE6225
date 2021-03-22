import sys
import os
import json
import requests
import time

api_prefix = 'https://o3nlvj1uld.execute-api.us-east-2.amazonaws.com/prod/'

if len(sys.argv) == 3:
    response = requests.get(api_prefix + 'leader-elect').json()

    if not response['availableWorkers']:
        print("No workers available")
    else:
        available_workers = response['availableWorkers']
        leader = response['leader']

        print("1. Available Workers:\n  - " + "\n  - ".join(available_workers))
        print("2. Leader:\n  - " + leader)

        available_workers.remove(leader)

        print("\n3. Downloading book content from url...")
        try:
            bookText = requests.get(sys.argv[1]).content.decode('UTF-8')
        except:
            raise Exception("Download book timeout. Please try again or use a faster endpoint.")

        payload = {
            "workers": available_workers, 
            "bookText": bookText,
            "operation": "leaderProcess"
        }

        print("\n4. Starts processing on Cloud")
        start_time = time.time()

        response = requests.put(api_prefix + leader.lower(), data = json.dumps(payload)).json()

        word_frequency = response["word_frequency"]
        sorted_word_frequency = sorted(word_frequency.items(), key = lambda x: x[1], reverse = True)
        end_time = time.time()
        print(("\n5. Processed in {time} seconds").format(time=end_time-start_time))
        print("\n6. Top {top} words:".format(top = sys.argv[2]))
        print(sorted_word_frequency[:int(sys.argv[2])])

else:
    print("Arguments are invalid.")