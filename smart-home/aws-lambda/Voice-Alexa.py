import json
import boto3
import datetime     # used for timestamps

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response


# ==============================================================================
# Global Variables
# ==============================================================================

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# boto3 clients
db = boto3.client('dynamodb')
cog = boto3.client('cognito-idp')
lam = boto3.client('lambda')

# Parse-RESTData Lambda ARN
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

# Get a User Account from Cognito by Auth Token
# token = auth token as string from connected service
def cog_get_account(token):
    # get the user by token
    user = cog.get_user(AccessToken=token)
    acct = 0
    
    # locate the account number tied to the user & return
    for attr in user['UserAttributes']:
        if attr['Name'] == 'custom:account':
            acct = int(attr['Value'])
            break

    return acct

# Get User Account
# handler_input = Alexa skill request handler input
def get_account(handler_input):
    # get the account token
    token = ask_utils.request_util.get_account_linking_access_token(handler_input)
    
    # get the account number
    account = cog_get_account(token)
    
    return account

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

# Get Device from Handler Data
def get_dev(acct, loc, dev):
    # get a list of devices tied to the account
    dev_info = get_dev_info(acct)
    
    # find the device in the list of devices
    # assuming simple device matching for now
    dev_name = loc + ' ' + dev
    device = 'NOT FOUND'
    
    # loop through each device in the list & match dev_name
    for d in dev_info['data']:
        if d['dev_name'] == dev_name:
            device = d
            break
    
    # return the found device dictionary
    return device

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
# Intent Processing
# ==============================================================================

# Get General State of Device
def get_state(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # within the devState, find the v_percent & locked values for the device
    state = {'on_state':'off','lock_state':'unlocked','percentage':0}
    for subdev in devState['data']:
        if subdev['dev_subid'] == device['dev_subid']:
            
            # set values based on state data
            if subdev['v_percent'] > 0:
                state['on_state'] = 'on'
            
            if subdev['locked'] > 0:
                state['lock_state'] = 'locked'
            
            state['percentage'] = subdev['v_percent']
            state.update({'dev_type':device['dev_type']})
            break

    return state

# Turn On the Device
def turn_on(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'

    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # modify the state
    for subdev in devState['data']:
        if subdev['dev_subid'] == device['dev_subid']:
            subdev['v_percent'] = 100
            break
    
    # update 'last_update'
    devState['last_update'] = build_time()
    
    # send the new state to main parsing function
    put_to_rest('devState', devState)

# Turn Off the Device
def turn_off(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # modify the state
    for subdev in devState['data']:
        if subdev['dev_subid'] == device['dev_subid']:
            subdev['v_percent'] = 0
            break
    
    # update 'last_update'
    devState['last_update'] = build_time()
    
    # send the new state to main parsing function
    put_to_rest('devState', devState)

# Increase Power Percentage of Device
def power_up(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # modify the state
    if device['dev_type'] == 'dimmer':
        new_v = 0
        for subdev in devState['data']:
            if subdev['dev_subid'] == device['dev_subid']:
                new_v = subdev['v_percent'] + 10
                if new_v > 100:
                    subdev['v_percent'] = 100
                else:
                    subdev['v_percent'] = new_v
                break
    
        # update 'last_update'
        devState['last_update'] = build_time()
    
        # send the new state to main parsing function
        put_to_rest('devState', devState)
        
        # return the new v_percent
        return new_v
    else:   # not a dimmable device
        return 'NOT VARIABLE'

# Decrease Power Percentage of Device
def power_down(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # modify the state
    if device['dev_type'] == 'dimmer':
        new_v = 0
        for subdev in devState['data']:
            if subdev['dev_subid'] == device['dev_subid']:
                new_v = subdev['v_percent'] - 10
                if new_v < 0:
                    subdev['v_percent'] = 0
                else:
                    subdev['v_percent'] = new_v
                break

        # update 'last_update'
        devState['last_update'] = build_time()

        # send the new state to main parsing function
        put_to_rest('devState', devState)

        # return the new v_percent
        return new_v
    else:   # not a dimmable device
        return 'NOT VARIABLE'

# Set Power Percentage of Device
def power_set(acct, loc, dev, perc):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # make sure perc is between 0 and 100
    perc = int(perc)
    if perc > 100:
        perc = 100
    elif perc < 0:
        perc = 0
    
    # modify the state
    if device['dev_type'] == 'dimmer':
        for subdev in devState['data']:
            if subdev['dev_subid'] == device['dev_subid']:
                subdev['v_percent'] = perc
                break
    
        # update 'last_update'
        devState['last_update'] = build_time()
    
        # send the new state to main parsing function
        put_to_rest('devState', devState)
        
        # return the new v_percent
        return 'SUCCESS'
    else:   # not a dimmable device
        return 'NOT VARIABLE'

# Set Device as Locked
def set_lock(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)

    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # modify the state
    for subdev in devState['data']:
        if subdev['dev_subid'] == device['dev_subid']:
            subdev['locked'] = 1
            break
    
    # update 'last_update'
    devState['last_update'] = build_time()
    
    # send the new state to main parsing function
    put_to_rest('devState', devState)

# Set Device as Unlocked
def set_unlock(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devState for the device
    devState = get_item('devState', acct, device['dev_id'])
    
    # modify the state
    for subdev in devState['data']:
        if subdev['dev_subid'] == device['dev_subid']:
            subdev['locked'] = 0
            break
    
    # update 'last_update'
    devState['last_update'] = build_time()
    
    # send the new state to main parsing function
    put_to_rest('devState', devState)

# Get Sub-Device Count
def get_sub_count(acct, dev):
    # get devInfo for device
    devInfo = get_item('devInfo', acct, dev)
    
    # verify devInfo exists
    if isinstance(devInfo, str):
        return 0
    else:
        return len(devInfo['data'])

# Build devTimer for Device
def build_timer(acct, dev):
    # get the dev_subid count for the device
    count = get_sub_count(acct, dev)
    
    # build devTimer
    devTimer = {'account':acct, 'dev_id':dev}
    devTimer.update({'last_update':'', 'data':[]})
    for i in range(count):
        devTimer['data'].append({'dev_subid':(i+1)})
        devTimer['data'][i].update({'on_limit':0,'off_limit':0})
    
    return devTimer

# Set Timer for Device
def set_timer(acct, loc, dev, onoff, time, tunit):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # build delay
    delay = 0
    if tunit.startswith('sec'):
        delay = int(time)
    elif tunit.startswith('min'):
        delay = int(time) * 60
    elif tunit.startswith('hour'):
        delay = int(time) * 3600
    
    # get devTimer for the device
    devTimer = get_item('devTimer', acct, device['dev_id'])
    
    # test if devTimer exists, if not, build it
    if isinstance(devTimer, str):
        devTimer = build_timer(acct, device['dev_id'])
    
    # take the existing devTimer & edit it
    for sub in devTimer['data']:
        if sub['dev_subid'] == device['dev_subid']:
            if onoff == 'on':
                sub['on_limit'] = delay
            else:
                sub['off_limit'] = delay
            break
    
    # update 'last_update'
    devTimer['last_update'] = build_time()
    
    # send the new state to main parsing function
    put_to_rest('devTimer', devTimer)

# Get Timer for Device
def get_timer(acct, loc, dev):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'

    # get devTimer for the device
    devTimer = get_item('devTimer', acct, device['dev_id'])
    
    # test if devTimer exists
    resp = {'on_limit':0,'off_limit':0}
    if isinstance(devTimer, str):
        return 'DOES NOT EXIST'
    else:
        # take the existing devTimer & edit it
        for sub in devTimer['data']:
            if sub['dev_subid'] == device['dev_subid']:
                resp['on_limit'] = sub['on_limit']
                resp['off_limit'] = sub['off_limit']
                break
    
    return resp

# Convert Week Day to Integer
def weekday_to_int(wday):
    wday = wday.casefold()
    day = 0
    if wday.startswith('sun'):
        day = 0
    elif wday.startswith('mon'):
        day = 1
    elif wday.startswith('tue'):
        day = 2
    elif wday.startswith('wed'):
        day = 3
    elif wday.startswith('thu'):
        day = 4
    elif wday.startswith('fri'):
        day = 5
    elif wday.startswith('sat'):
        day = 6

    return day

# Build devSched for Device
def build_sched(acct, dev):
    # get the dev_subid count for the device
    count = get_sub_count(acct, dev)
    
    # build devSched
    devSched = {'account':acct, 'dev_id':dev}
    devSched.update({'last_update':'', 'data':[]})
    for i in range(count):
        devSched['data'].append({'dev_subid':(i+1), 'sdata':[]})

    return devSched


# Get Day Schedule for Device
def get_day_sched(acct, loc, dev, day):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'

    # get devTimer for the device
    devSched = get_item('devSched', acct, device['dev_id'])
    
    # test if devSched exists
    resp = []
    if isinstance(devSched, str):
        return 'DOES NOT EXIST'
    else:
        # take the existing devTimer & edit it
        for dev in devSched['data']:
            if dev['dev_subid'] == device['dev_subid']:
                
                # get the schedule, then break
                for sub in dev['sdata']:
                    if sub['day'] == day:
                        resp.append(sub)
    
    # sort the response by time before returning
    # sort data by 'date' & 'dev_id'
    schedSort = sorted(resp, key=lambda d: d['time'])
    resp = schedSort

    return resp

# Set Day Schedule for Device - FIX ME
def set_day_sched(acct, loc, dev, day, chg, time):
    # get the device
    device = get_dev(acct, loc, dev)
    
    # if device does not exist, return
    if isinstance(device, str):
        return 'DEVICE NOT FOUND'
    
    # get devSched for the device
    devSched = get_item('devSched', acct, device['dev_id'])
    
    # test if devSched exists, if not, build it
    if isinstance(devSched, str):
        devSched = build_sched(acct, device['dev_id'])
    
    # convert chg if on/off, else leave it alone
    if chg == 'on':
        chg = 100
    elif chg == 'off':
        chg = 0
    if device['dev_type'] != 'dimmer':
        if chg > 0:
            chg = 100
        else:
            chg = 0
    
    # test if time in expected format
    test = time.find(':')
    if test < 0:
        return 'WRONG TIME FORMAT'
    
    # convert time to seconds
    temp = time.split(':')
    hr = int(temp[0])
    mn = int(temp[1])
    time = (hr * 3600) + (mn * 60)
    
    # take the existing devSched & edit it
    for sub in devSched['data']:
        if sub['dev_subid'] == device['dev_subid']:
            
            # overwrite time entry if it exists
            for entry in sub['sdata']:
                if entry['day'] == day:
                    if entry['time'] == time:
                        entry['v_percent'] = chg
                    break

            # else, append new entry and sort
            sub['sdata'].append({'day':day, 'time':time, 'v_percent': chg})
            break

    # update 'last_update'
    devSched['last_update'] = build_time()
    
    # send the new state to main parsing function
    put_to_rest('devSched', devSched)

# ==============================================================================
# Main Launch Request
# ==============================================================================

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # set up initial greeting
        speak_output = 'Welcome to your Virtual Switch Board! What would you like to do with your smart devices?'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# ==============================================================================
# Custom Intent Requests
# ==============================================================================

class GetStateIntentHandler(AbstractRequestHandler):
    """Handler for Get State Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetStateIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # get the general device state
        state = get_state(account, loc, dev)
        
        # check for 'DEVICE NOT FOUND' error
        if state != 'DEVICE NOT FOUND':
            on = state['on_state']
            perc = state['percentage']
            lock = state['lock_state']
        
            # build the spoken output
            if state['dev_type'] == 'dimmer':
                speak_output = f'{loc} {dev} is {on} at {perc} percent and {lock}.'
            else:
                speak_output = f'{loc} {dev} is {on} and {lock}.'
        else:
            speak_output = f'I am sorry, {loc} {dev} was not found.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class GetOnIntentHandler(AbstractRequestHandler):
    """Handler for Get On Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetOnIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # get the general device state
        state = get_state(account, loc, dev)
        
        # check for 'DEVICE NOT FOUND' error
        if state != 'DEVICE NOT FOUND':
            on = state['on_state']

            # build the spoken output
            speak_output = f'{loc} {dev} is currently {on}.'
        else:
            speak_output = f'I am sorry, {loc} {dev} was not found.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class GetLockIntentHandler(AbstractRequestHandler):
    """Handler for Get Lock Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetLockIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # get the general device state
        state = get_state(account, loc, dev)
        
        # check for 'DEVICE NOT FOUND' error
        if state != 'DEVICE NOT FOUND':
            lock = state['lock_state']
        
            # build the spoken output
            speak_output = f'{loc} {dev} is currently {lock}.'
        else:
            speak_output = f'I am sorry, {loc} {dev} was not found.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class GetPowerIntentHandler(AbstractRequestHandler):
    """Handler for Get Power Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetPowerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # get the general device state
        state = get_state(account, loc, dev)
        
        # check for 'DEVICE NOT FOUND' error
        if state != 'DEVICE NOT FOUND':
            perc = state['percentage']

            # build the spoken output
            speak_output = f'{loc} {dev} is set to {perc} percent.'
        else:
            speak_output = f'I am sorry, {loc} {dev} was not found.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class TurnOnIntentHandler(AbstractRequestHandler):
    """Handler for Turn On Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TurnOnIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # turn on the device
        turn_on(account, loc, dev)
        
        # build the spoken output
        speak_output = f'Turning on {loc} {dev}.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class TurnOffIntentHandler(AbstractRequestHandler):
    """Handler for Turn Off Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TurnOffIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # turn off the device
        turn_off(account, loc, dev)
        
        # build the spoken output
        speak_output = f'Turning off {loc} {dev}.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class PowerUpIntentHandler(AbstractRequestHandler):
    """Handler for Power Up Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PowerUpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # increase the power for the device
        perc = power_up(account, loc, dev)
        
        # build the spoken output
        if isinstance(perc, int):
            speak_output = f'Increasing the power percentage of {loc} {dev} to {perc} percent.'
        else:
            speak_output = f'I am sorry, {loc} {dev} is not a dimmable smart device.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class PowerDownIntentHandler(AbstractRequestHandler):
    """Handler for Power Down Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PowerDownIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # decrease the power for the device
        perc = power_down(account, loc, dev)
        
        # build the spoken output
        if isinstance(perc, int):
            speak_output = f'Decreasing the power percentage of {loc} {dev} to {perc} percent.'
        else:
            speak_output = f'I am sorry, {loc} {dev} is not a dimmable smart device.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class PowerSetIntentHandler(AbstractRequestHandler):
    """Handler for Power Set Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PowerSetIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        perc = ask_utils.request_util.get_slot(handler_input, "percentage").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # set the power for the device
        response = power_set(account, loc, dev, perc)
        
        # build the spoken output
        if response == 'SUCCESS':
            speak_output = f'Setting the power percentage of {loc} {dev} to {perc} percent.'
        elif response == 'NOT VARIABLE':
            speak_output = f'I am sorry, {loc} {dev} is not a dimmable smart device.'
        else:
            speak_output = f'I am sorry, I was not able to find {loc} {dev}.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class LockIntentHandler(AbstractRequestHandler):
    """Handler for Lock Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LockIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # lock the device
        set_lock(account, loc, dev)
        
        # build the spoken output
        speak_output = f'Locking {loc} {dev}.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class UnlockIntentHandler(AbstractRequestHandler):
    """Handler for Unlock Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("UnlockIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # unlock the device
        set_unlock(account, loc, dev)
        
        # build the spoken output
        speak_output = f'Unlocking {loc} {dev}.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class SetOnTimerIntentHandler(AbstractRequestHandler):
    """Handler for Set On Timer Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SetOnTimerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        time = ask_utils.request_util.get_slot(handler_input, "limit").value
        tunit = ask_utils.request_util.get_slot(handler_input, "unit").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # set the device timer
        set_timer(account, loc, dev, 'on', time, tunit)
        
        # build the spoken output
        speak_output = f'Setting the on timer for {loc} {dev} to {time} {tunit}.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class SetOffTimerIntentHandler(AbstractRequestHandler):
    """Handler for Set Off Timer Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SetOffTimerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        time = ask_utils.request_util.get_slot(handler_input, "limit").value
        tunit = ask_utils.request_util.get_slot(handler_input, "unit").value
        
        # get account number tied to the user
        account = get_account(handler_input)
        
        # set the device timer
        set_timer(account, loc, dev, 'off', time, tunit)
        
        # build the spoken output
        speak_output = f'Setting the off timer for {loc} {dev} to {time} {tunit}.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class GetTimerIntentHandler(AbstractRequestHandler):
    """Handler for Get Timer Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetTimerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value

        # get account number tied to the user
        account = get_account(handler_input)
        
        # get timer for device
        resp = get_timer(account, loc, dev)
        
        # build the spoken output
        if isinstance(resp, str):
            speak_output = f'No timers were found for the {loc} {dev}.'
        else:
            on = resp['on_limit']
            off = resp['off_limit']
            speak_output = f'The {loc} {dev} is set to turn off after {on} seconds and turn on after {off} seconds.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class GetDaySchedIntentHandler(AbstractRequestHandler):
    """Handler for Get Day Schedule Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetDaySchedIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        wday = ask_utils.request_util.get_slot(handler_input, "weekday").value
        
        # convert weekday to an int
        day = weekday_to_int(wday)

        # get account number tied to the user
        account = get_account(handler_input)
        
        # get schedule for a day for the device
        resp = get_day_sched(account, loc, dev, day)
        
        # build the spoken output
        if isinstance(resp, str):
            speak_output = f'No schedules were found for the {loc} {dev} for {wday}.'
        else:
            # build the speak_output for each scheduled entry, adjust time too
            speak_output = f'On {wday}, the {loc} {dev} is set to change to '
            for s in resp:
                
                # determine time of day in hr, min, sec
                sec = s['time'] % 60
                mn = (s['time'] - sec) % 3600
                hr = ((s['time'] - sec) - (mn * 60)) / 3600
                
                # determine AM or PM
                half = 'A.M.'
                if hr > 12:
                    half = 'P.M.'
                    hr = hr - 12
                
                # build time phrase
                time = ''
                sphrase = 'seconds'
                if sec == 1:
                    sphrase = 'second'
                if sec > 0:
                    time = f'{hr}:{mn} {half} and {sec} {sphrase}'
                else:
                    time = f'{hr}:{mn} {half}'
                
                # determine language for v_percent
                vphrase = 'off'
                if s['v_percent'] == 100:
                    vphrase = 'on'
                elif s['v_percent'] != 0:
                    vphrase = f'{s['v_percent']} percent'
                
                # add built language to speak_output
                speak_output = speak_output + vphrase + ' at ' + time + ', '
            
            # finish the output
            speak_output = speak_output[:-2] + '.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class DaySchedOnIntentHandler(AbstractRequestHandler):
    """Handler for Day Schedule On Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DaySchedOnIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        wday = ask_utils.request_util.get_slot(handler_input, "weekday").value
        time = ask_utils.request_util.get_slot(handler_input, "time").value
        
        # convert weekday to an int
        day = weekday_to_int(wday)

        # get account number tied to the user
        account = get_account(handler_input)
        
        # get schedule for a day for the device
        set_day_sched(account, loc, dev, day, 'on', time)

        # build the spoken output
        speak_output = f'Setting schedule for {wday} at {time} to turn on the {loc} {dev}.'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class DaySchedOffIntentHandler(AbstractRequestHandler):
    """Handler for Day Schedule Off Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DaySchedOffIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        wday = ask_utils.request_util.get_slot(handler_input, "weekday").value
        time = ask_utils.request_util.get_slot(handler_input, "time").value
        
        # convert weekday to an int
        day = weekday_to_int(wday)

        # get account number tied to the user
        account = get_account(handler_input)
        
        # get schedule for a day for the device
        set_day_sched(account, loc, dev, day, 'off', time)

        # build the spoken output
        speak_output = f'Setting schedule for {wday} at {time} to turn off the {loc} {dev}.'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class DaySchedPowerIntentHandler(AbstractRequestHandler):
    """Handler for Day Schedule Power Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DaySchedPowerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # get the device name from {location} and {device}
        loc = ask_utils.request_util.get_slot(handler_input, "location").value
        dev = ask_utils.request_util.get_slot(handler_input, "device").value
        wday = ask_utils.request_util.get_slot(handler_input, "weekday").value
        time = ask_utils.request_util.get_slot(handler_input, "time").value
        power = ask_utils.request_util.get_slot(handler_input, "percentage").value
        
        # convert weekday to an int
        day = weekday_to_int(wday)

        # get account number tied to the user
        account = get_account(handler_input)
        
        # get schedule for a day for the device
        set_day_sched(account, loc, dev, day, power, time)

        # build the spoken output
        speak_output = f'Setting schedule for {wday} at {time} to turn change the {loc} {dev} to {power} percent.'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

# ==============================================================================
# Default Skill Handlers
# ==============================================================================

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "How may I help you?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "I'm sorry, I did not catch that. What would you like to do with your smart devices?"
        reprompt = "I'm afraid I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

# ==============================================================================
# Intent Testing Handler
# ==============================================================================

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

# ==============================================================================
# Error Catching Handler
# ==============================================================================

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

# ==============================================================================
# Main Function
# ==============================================================================

sb = SkillBuilder()

# Main Launch Request
sb.add_request_handler(LaunchRequestHandler())

# Custom Intent Requests
sb.add_request_handler(GetStateIntentHandler())
sb.add_request_handler(GetOnIntentHandler())
sb.add_request_handler(GetLockIntentHandler())
sb.add_request_handler(GetPowerIntentHandler())
sb.add_request_handler(TurnOnIntentHandler())
sb.add_request_handler(TurnOffIntentHandler())
sb.add_request_handler(PowerUpIntentHandler())
sb.add_request_handler(PowerDownIntentHandler())
sb.add_request_handler(PowerSetIntentHandler())
sb.add_request_handler(LockIntentHandler())
sb.add_request_handler(UnlockIntentHandler())
sb.add_request_handler(SetOnTimerIntentHandler())
sb.add_request_handler(SetOffTimerIntentHandler())
sb.add_request_handler(GetTimerIntentHandler())
sb.add_request_handler(GetDaySchedIntentHandler())
sb.add_request_handler(DaySchedOnIntentHandler())
sb.add_request_handler(DaySchedOffIntentHandler())
sb.add_request_handler(DaySchedPowerIntentHandler())

# Default Skill Handlers
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Intent Testing Handler
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

# Error Catching Handler
sb.add_exception_handler(CatchAllExceptionHandler())

# Main Function
lambda_handler = sb.lambda_handler()
