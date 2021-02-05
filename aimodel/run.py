from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import json

PROJECT = "comprehension-247816"
MODEL_NAME = "grammartest"
VERSION_NAME = "v1"

techcrunch=[
 'Uber shuts down self-driving trucks unit',
 'Grover raises €37M Series A to offer latest tech products as a subscription',
 'Tech companies can now bid on the Pentagon’s $10B cloud contract'
]
nytimes=[
 '‘Lopping,’ ‘Tips’ and the ‘Z-List’: Bias Lawsuit Explores Harvard’s Admissions',
 'A $3B Plan to Turn Hoover Dam into a Giant Battery',
 'A MeToo Reckoning in China’s Workplace Amid Wave of Accusations'
]
github=[
 'Show HN: Moon – 3kb JavaScript UI compiler',
 'Show HN: Hello, a CLI tool for managing social media',
 'Firefox Nightly added support for time-travel debugging'
]
requests = (techcrunch+nytimes+github)

# JSON format the requests
request_data = {'instances': requests}

# Authenticate and call CMLE prediction API
credentials = GoogleCredentials.get_application_default()
api = discovery.build('ml', 'v1', credentials=credentials,
     discoveryServiceUrl='https://storage.googleapis.com/cloud-ml/discovery/ml_v1_discovery.json')

parent = 'projects/%s/models/%s/versions/%s' % (PROJECT, MODEL_NAME, VERSION_NAME)
response = api.projects().predict(body=request_data, name=parent).execute()

print(response['predictions'])