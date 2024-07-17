# Lambda function that is run once to initialize DynamoDB
# tables for each of the configurations associated with
# the A2B Smart Device project.

import json
import boto3

# establish client connections
db = boto3.client('dynamodb')

# function to create the necessary tables
def create_ddb_tbl(name):
    # begin defs and schema
    attrDef = [{'AttributeName': 'account','AttributeType': 'N'}]
    kSchema = [{'AttributeName': 'account','KeyType': 'HASH'}]
    
    # expand defs and schema
    if name not in ['acctRep', 'acctNet', 'acctUpdates', 'acctLogins']:
        attrDef.append({'AttributeName': 'dev_id','AttributeType': 'N'})
        kSchema.append({'AttributeName': 'dev_id','KeyType': 'RANGE'})

    # build and create table here
    db.create_table(AttributeDefinitions=attrDef,TableName=name,
        KeySchema=kSchema,BillingMode='PAY_PER_REQUEST')


# primary function
def lambda_handler(event, context):
    
    # Create list of expected tables
    devTbls = ['devState','devInfo','devTimer','devSched','devLogs','acctRep','acctNet','acctUpdates', 'acctLogins']

    # List existing tables
    tables = db.list_tables()['TableNames']

    # If table exists, remove it from list of expected tables
    for x in tables:
        if x in devTbls:
            devTbls.remove(x)

    # Create missing tables and verify table status is 'active'
    # Takes about 8s each; lambda default timeout is 3s
    # Should wait until tables are active before using them
    for y in devTbls:
        create_ddb_tbl(y)
        #db.get_waiter('table_exists').wait(TableName=y,WaiterConfig={'Delay': 2,'MaxAttempts': 5})

    return {
        'statusCode': 200,
        'body': json.dumps('Smart device tables have been initialized in DynamoDB.')
    }
