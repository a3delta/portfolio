import json
import boto3
import datetime     # used for timestamps

# ==============================================================================
# Global Variables
# ==============================================================================

# boto3 clients
db = boto3.client('dynamodb')
cog = boto3.client('cognito-idp')
lam = boto3.client('lambda')

# Parse-REST Data Lambda ARN
fname = 'arn:aws:lambda:us-east-2:894293519475:function:Parse-RESTData'

# =============================================================================
# FUNCTIONS - Build Current Time
# =============================================================================

# Build Current Time
def build_time():
    # get current time, calc sec, build & return string
    now = datetime.datetime.now()
    time = (now.hour*3600 + now.minute*60 + now.second)
    return f"{now.year}-{now.month}-{now.day}-{time}"

# =============================================================================
# FUNCTIONS - Get Cognito User Info from Token
# =============================================================================

# Get a User Info from Cognito by Auth Token
# token = auth token as string from connected service
def cog_get_user(token):
    # get the user by token
    user = cog.get_user(AccessToken=token)
    info = {'account':0, 'sub':''}

    # locate the account number tied to the user & return
    for attr in user['UserAttributes']:
        if attr['Name'] == 'custom:account':
            info['account'] = int(attr['Value'])
        elif attr['Name'] == 'sub':
            info['sub'] = attr['Value']

    return info

# =============================================================================
# FUNCTIONS - Convert DynamoDB Objects Into JSON Objects
# =============================================================================

# Build JSON Object from DynamoDB - Base Block
def build_jsonObj_block(data):
    # determine data type of data - assumes map or list
    if isinstance(data, dict):
        # determine list of keys in map/base DDB item
        dScope = list(data.keys())
        newObj = {}

        # loop through each element and determine its data type
        # ordered by likelihood for efficiency (N > M > S > L)
        for i in dScope:
            subKey = list(data[i].keys())[0]
            # if number, build int and copy data
            if subKey == 'N':
                newObj.update({i:int(float(data[i]['N']))})
            # if map, build blank base dict
            elif subKey == 'M':
                newObj.update({i:{}})
            # if string, build string and copy data
            elif subKey == 'S':
                newObj.update({i:data[i]['S']})
            # if list, build blank base list
            elif subKey == 'L':
                newObj.update({i:[]})
    elif isinstance(data, list):
        # determine number of elements in item
        dScope = range(len(data))
        newObj = []

        # loop through each element and determine its data type
        # ordered by likelihood for efficiency (N > M > S > L)
        for i in dScope:
            subKey = list(data[i].keys())[0]
            # if number, build int and copy data
            if subKey == 'N':
                newObj.append(int(float(data[i]['N'])))
            # if map, build blank base dict
            elif subKey == 'M':
                newObj.append({})
            # if string, build string and copy data
            elif subKey == 'S':
                newObj.append(data[i]['S'])
            # if list, build blank base list
            elif subKey == 'L':
                newObj.append([])

    # return new object
    return newObj

# Build JSON Object from DynamoDB - Single Layer
def build_jsonObj_slayer(data):
    # setup primary keys - data will always be a map
    newObj = build_jsonObj_block(data)

    # iterate through list and populate dicts in key1
    tLen = len(data['data']['L'])
    for i in range(tLen):
        newObj['data'].append(build_jsonObj_block(data['data']['L'][i]['M']))

    return newObj

# Build JSON Object from DynamoDB - Double Layer
def build_jsonObj_dlayer(data):
    # setup primary keys - data will always be a map
    newObj = build_jsonObj_block(data)

    # iterate through list and populate dicts in 'data'
    tLen = len(data['data']['L'])
    for i in range(tLen):
        newObj['data'].append(build_jsonObj_block(data['data']['L'][i]['M']))

        # iterate through list and populate maps in 'sdata'
        stLen = len(data['data']['L'][i]['M']['sdata']['L'])
        for j in range(stLen):
            block = build_jsonObj_block(data['data']['L'][i]['M']['sdata']['L'][j]['M'])
            newObj['data'][i]['sdata'].append(block)

    return newObj

# Build JSON Object from DynamoDB Item
def build_jsonObj(data, tblName):
    # initialize layer lists
    slayer = ['devState','devInfo','devTimer']

    # build object based on table
    if tblName in slayer:
        obj = build_jsonObj_slayer(data)
    elif tblName == 'devSched':
        obj = build_jsonObj_dlayer(data)
    else:
        obj = None

    return obj

# =============================================================================
# FUNCTIONS - Get Items from DynamoDB
# =============================================================================

# Get Item Data from DynamoDB
# acct = 'account', tbl = table as string, dev = 'dev_id'
def get_item(tbl, acct, dev):
    # build key
    dkey = {'account': {'N': str(acct)}}
    dkey.update( {'dev_id':{'N': str(dev)}} )
    
    # get item based on table passed
    itm = db.get_item(Key=dkey,TableName=tbl)

    # if item retrieved, convert to json & return
    if len(itm) > 1:
        obj = build_jsonObj(itm['Item'], tbl)
        return obj
    else:       # else, return error message
        return 'ERROR: Data not found'

# Get a List of devInfo Data for Finding a Referenced Device
# account = account number as an int
def get_dev_info(account):
    # declare query variables
    tbl = 'devInfo'
    vals = {':v1':{'N':str(account)}}
    cond = 'account = :v1'

    # query the devInfo table in DynamoDB
    query = db.query(TableName=tbl, ExpressionAttributeValues=vals, KeyConditionExpression=cond)

    # trim the output for account, dev_id, dev_subid, and dev_name
    dev_info = {'account':account, 'data':[]}
    for itm in query['Items']:
        for d in itm['data']['L']:
            dev = {'dev_id':int(itm['dev_id']['N'])}
            dev.update({'dev_subid':int(d['M']['dev_subid']['N'])})
            dev.update({'dev_type':d['M']['dev_type']['S']})
            dev.update({'dev_name':d['M']['dev_name']['S']})
            dev_info['data'].append(dev)

    return dev_info

# ==============================================================================
# REST PUT Data to Parse-RESTData Function
# ==============================================================================

# PUT Data to Parse-RESTData Function
# tbl = table the data goes to, data = data formatted for the table
def put_to_rest(tbl, data):
    # convert data to a byte string
    data_str = json.dumps(data)
    
    # build the event to send
    event = {'httpMethod':'PUT','body':data_str,'path':'/app'}
    event.update({'queryStringParameters':{'table':tbl}})

    # set up lambda invocation parameters
    pload = json.dumps(event)
    
    # send data to Parse-RESTData function
    lam.invoke(FunctionName=fname, Payload=pload)

# ==============================================================================
# Intent Translation
# ==============================================================================

# Convert Google Device ID & Get dev_type
# acct = account number tied to devices, devices = list of device objects from intent payload
def convert_id(acct, devices):
    # initialize device lists
    pay_devs = []

    # pull the list of dev_id and dev_subid from the payload
    for dev in devices:
        id_split = dev['id'].split('-')
        temp = {'id':dev['id'],'dev_id':int(id_split[0]),'dev_subid':int(id_split[1])}
        
        # get the devInfo for each dev and add dev_type to the data
        devInfo = get_item('devInfo', acct, temp['dev_id'])
        if isinstance(devInfo, str):
            temp.update({'dev_type':devInfo})
        else:
            for sub in devInfo['data']:
                if sub['dev_subid'] == temp['dev_subid']:
                    temp.update({'dev_type':sub['dev_type']})
                    break
        
        # append the converted data to the main list
        pay_devs.append(temp)
    
    return pay_devs

# ==============================================================================
# Main Intent Functions
# ==============================================================================

# SYNC Intent
# req_id = request ID from POST, acct = account number, sub = Cognito sub for user
def intent_sync(req_id, acct, sub):
    # initialize the sync response
    resp = { 'requestId':req_id,'payload':{ 'agentUserId':sub,'devices':[] } }

    # get devices
    dev_info = get_dev_info(acct)

    # for each device, translate to sync response
    for dev in dev_info['data']:
        
        # build id
        sync_id = str(dev['dev_id']) + '-' + str(dev['dev_subid'])
        sync_dev = {'id':sync_id}
        
        # initialize remaining device information
        sync_type = ''
        sync_traits = ['action.devices.traits.OnOff','action.devices.traits.LockUnlock']
        sync_info = {'manufacturer':'team-a2b','model':'','hwVersion':'1.0','swVersion':'1.0'}
        
        # determine the device type and build the rest
        if dev['dev_type'] == 'switch':
            sync_type = 'action.devices.types.SWITCH'
            sync_info['model'] = 'smart_switch_1'
        elif dev['dev_type'] == 'dimmer':
            sync_type = 'action.devices.types.SWITCH'
            sync_traits.append('action.devices.traits.Brightness')
            sync_info['model'] = 'smart_dimmer_1'
        elif dev['dev_type'] == 'outlet':
            sync_type = 'action.devices.types.OUTLET'
            sync_info['model'] = 'smart_outlet_1'
        
        # add values to sync_dev dictionary
        sync_dev.update({'type':sync_type})
        sync_dev.update({'traits':sync_traits})
        sync_dev.update({'name':{'name':dev['dev_name']}})
        sync_dev.update({'willReportState':False})      # set to false, devs will not auto-report back
        sync_dev.update({'deviceInfo':sync_info})
        
        # append the device to the response
        resp['payload']['devices'].append(sync_dev)

    return resp

# QUERY Intent
# req_id = request ID from POST, acct = account number, payload = intent payload
def intent_query(req_id, acct, payload):
    # initialize the query response
    resp = { 'requestId':req_id,'payload':{ 'devices':{} } }
    
    # convert the payload devices & get dev_type
    pay_devs = convert_id(acct, payload['devices'])
    
    # get devState for each device and update response
    for dev in pay_devs:
        devState = get_item('devState', acct, dev['dev_id'])
        
        # match the dev_subid to the correct index
        index = 0
        for i in range(len(devState['data'])):
            if devState['data'][i]['dev_subid'] == dev['dev_subid']:
                index = i
                break
        
        # build device dict for query
        temp = {'status':'SUCCESS','online':True}
        
        # add correct on state & brightness if applicable
        v_percent = devState['data'][index]['v_percent']
        if v_percent > 0:
            temp.update({'on':True})
        else:
            temp.update({'on':False})
        
        # add correct lock state
        if devState['data'][index]['locked'] > 0:
            temp.update({'isLocked':True})
        else:
            temp.update({'isLocked':False})
        
        # add remaining lock query variable
        temp.update({'isJammed': False})
        
        # add brightness if dev_type is a dimmer
        if dev['dev_type'] == 'dimmer':
            temp.update({'brightness':v_percent})
        
        # add device data to payload
        resp['payload']['devices'].update({dev['id']:temp})

    return resp

# EXECUTE Intent
# req_id = request ID from POST, acct = account number, payload = intent payload
def intent_execute(req_id, acct, payload):
    # initialize the query response
    resp = { 'requestId':req_id,'payload':{ 'commands':[] } }
    
    # initialize devState list to queue updates and minimize REST calls
    states_list = {}
    
    # for each command in the payload
    for cmd in payload['commands']:
    
        # initialize commands response
        cmd_resp = {'ids':[],'status':'SUCCESS','states':{'online':True}}
        
        # convert the payload devices & get dev_type
        pay_devs = convert_id(acct, cmd['devices'])
        
        # for each device from payload, append to ids list
        for d in pay_devs:
            cmd_resp['ids'].append(d['id'])
            
            # get devState data while working
            key_list = list(states_list.keys())
            if d['id'] not in key_list:
                states_list.update({ d['id']:get_item('devState', acct, d['dev_id']) })

        # for each execution in the payload command
        for exe in cmd['execution']:
            
            # test command and work accordingly
            if exe['command'].endswith('.OnOff'):
                
                # do OnOff command, set change variable
                chg = exe['params']['on']
                
                # initialize commands response states
                cmd_resp['states'].update({'on':chg})
                
                # find devState for the device & update
                for d in pay_devs:
                    for s in states_list[d['id']]['data']:
                        if s['dev_subid'] == d['dev_subid']:
                            if chg:
                                s['v_percent'] = 100
                            else:
                                s['v_percent'] = 0
                
            elif exe['command'].endswith('.LockUnlock'):
                
                # do LockUnlock command, set change variable
                chg = exe['params']['lock']
                
                # initialize commands response states
                cmd_resp['states'].update({'isLocked':chg,'isJammed':False})
                
                # find devState for the device & update
                for d in pay_devs:
                    for s in states_list[d['id']]['data']:
                        if s['dev_subid'] == d['dev_subid']:
                            if chg:
                                s['locked'] = 1
                            else:
                                s['locked'] = 0
                
            elif exe['command'].endswith('.BrightnessAbsolute'):
                
                # do BrightnessAbsolute command, set change variable
                chg = exe['params']['brightness']
                
                # initialize commands response states
                cmd_resp['states'].update({'brightness':chg})
                
                # find devState for the device & update
                for d in pay_devs:
                    for s in states_list[d['id']]['data']:
                        if s['dev_subid'] == d['dev_subid']:
                            s['v_percent'] = chg
                
            #else:
                # error handling for unsupported commands
                
        # append command response to response
        resp['payload']['commands'].append(cmd_resp)
    
    # put each devState back to DDB through the Parse-RESTData Lambda function
    key_list = list(states_list.keys())
    for k in key_list:
        states_list[k]['last_update'] = build_time()
        put_to_rest('devState', states_list[k])
    
    return resp

# ==============================================================================
# Main Function
# ==============================================================================

def lambda_handler(event, context):

    # get the access token for the POST
    token = event['headers']['Authorization'].replace('Bearer ','')
    info = cog_get_user(token)
    # continue under the assumption that the token is valid
    
    # get the POST body
    post_body = json.loads(event['body'])
    
    # get the request ID and loop through the inputs
    req_id = post_body['requestId']
    for entry in post_body['inputs']:
        intent = entry['intent']
    
        # start processing intents
        if intent == 'action.devices.SYNC':
            # get a list of devices & features, build out response
            response = intent_sync(req_id, info['account'], info['sub'])
        elif intent == 'action.devices.QUERY':
            response = intent_query(req_id, info['account'], entry['payload'])
        elif intent == 'action.devices.EXECUTE':
            response = intent_execute(req_id, info['account'], entry['payload'])
        elif intent == 'action.devices.DISCONNECT':
            # do nothing and return an empty dict
            response = {}

    return {
        'statusCode': 200,
        'body': json.dumps(response),
        'headers': {'Content-Type': 'application/json'}
    }
