import json
import sys
import os

from pdpyras import APISession, PDClientError

from model.oauth_client_delete import *
from config import *

def lambda_handler(event, context):
    print('Event Received: {}'.format(json.dumps(event)))

    # unmarshal the event
    awsEvent = Marshaller.unmarshall(event, 'AWSEvent')

    #only process OAuthClient events
    if 'OAuthClient' not in awsEvent.detail.topicName:
        return generate_return_body(200, 'Not an OAuth Client event')

    oauthClientEvent = awsEvent.detail.eventBody

    # only respond to deleted clients
    if oauthClientEvent.action != 'Delete':
        return generate_return_body(200, 'OAuth Client not deleted')

    deleteTime = ''
    for propertyChange in oauthClientEvent.propertyChanges:
        if propertyChange.property == 'deleted_on':
            deleteTime = propertyChange.newValues[0]

    print('{} has been deleted at {}'.format(oauthClientEvent.entity.name, deleteTime))

    try:
        # create a pager duty incident with the client id and deletion time
        incident = notify_pager_duty(oauthClientEvent.entity.id, deleteTime)
        print('PagerDuty incident with ID {} has been created'.format(incident.id))
    except PDClientError as e:
        if e.response:
            return generate_return_body(e.response.status_code, e.response.msg)
        else:
            return generate_return_body(500, str(e))

    return generate_return_body(200, 'PagerDuty incident created')

def notify_pager_duty(oauth_client_id, deleted_on):
    session = APISession(pager_duty_token)

    details = 'OAuth Client with ID {} has been deleted at {}'.format(oauth_client_id, deleted_on)

    payload = {
        'type': 'incident',
        'title': 'OAuth Client Deleted',
        'service': {
            'id': oauth_client_id,
            'type': 'service_reference'
        },
        'body': {
            'type': 'incident_body',
            'details': details
        },
    }

    return session.rpost('/incidents', json=payload)

def generate_return_body(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps({
            'message': message
        })
    }

# For running locally. Pass in the path to a valid event in a JSON file to test
if __name__ == '__main__':
    file_path = sys.argv[1]
    if file_path != None and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            print(lambda_handler(json.load(f), 'context'))