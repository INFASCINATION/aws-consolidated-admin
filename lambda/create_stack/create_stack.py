import base64
import boto3
import os

kms = boto3.client('kms')

KMS_KEY_ID = os.environ['KMS_KEY_ID']

def decrypt(ciphertext):
    return kms.decrypt(
        CiphertextBlob=base64.b64decode(ciphertext))['Plaintext']

def format_parameters(params):
    return [{
        'ParameterKey': k,
        'ParameterValue': v
    } for k,v in params.iteritems()]

def lambda_handler(event, context):
    sess = boto3.session.Session(
        aws_access_key_id=event['Credentials']['AccessKeyId'],
        aws_secret_access_key=decrypt(
            event['Credentials']['SecretAccessKeyCiphertext']),
        aws_session_token=event['Credentials']['SessionToken'],
        region_name=event['Region'])

    cfn = sess.client('cloudformation')

    return cfn.create_stack(
        TemplateURL=event['TemplateURL'],
        StackName=event['Stack']['StackName'],
        Capabilities=event.get('Capabilities', []),
        Parameters=format_parameters(event['Parameters']),
        OnFailure='DO_NOTHING')
