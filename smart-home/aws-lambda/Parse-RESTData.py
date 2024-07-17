# =============================================================================
# This function will be called when REST messages are sent to the smartdev
# REST API. This function will take the data that is passed through the 
# message, parse it, and GET or POST the changes using DynamoDB.
# =============================================================================

# =============================================================================
# IMPORTS & GLOBAL VARS
# =============================================================================

import boto3
import json
import datetime     # used for timestamps

# boto3 clients
db = boto3.client('dynamodb')
cog = boto3.client('cognito-idp')

# Cognito Environment Variables
pool = 'us-east-2_f9zt9hlOE'            # user pool: a2b-smartdev

# =============================================================================
# FUNCTIONS - TIME
# -----------------------------------------------------------------------------
# INFO: Used to manage time operations.
# =============================================================================

# Build Current Time
def build_time():
    # get current time, calc sec, build & return string
    now = datetime.datetime.now()
    time = (now.hour*3600 + now.minute*60 + now.second)
    return f"{now.year}-{now.month}-{now.day}-{time}"

# Convert from 'y-m-d h:m:s' to 'y-m-d-s'
def format_time(time):
    # check if not in 'y-m-d-s' format
    if time.count(':') > 0:
        
        # reformat time string, assuming 'y-m-d h:m:s'
        temp = list(time.split(' '))
        sec = list(map(int,temp[1].split(':')))
        s = ((sec[0]*3600) + (sec[1]*60) + sec[2])
        time = temp[0] + '-' + str(s)

    return time

# Test If Time Is Older - A (older) < B (newer)
# Will compare year, month, and day, but skip seconds
def isOlder(a, b):
    # time format safety check
    a = format_time(a)
    b = format_time(b)
    
    # split time strings into list of parts as ints
    a1 = list(map(int,a.split("-")))
    b1 = list(map(int,b.split("-")))

    # if len of each is not equal, shrink longest
    if len(a1) > len(b1):
        del a1[-1]
    elif len(a1) < len(b1):
        del b1[-1]

    # loop through each element and compare for age
    for i in range(len(a1)):
        if i == 0:
            # if year a is older, return true
            if a1[i] < b1[i]:
                return True
        else:
            # if a is older and prev a is equal, return true, else false
            if (a1[i] < b1[i]) and (a1[i-1] == b1[i-1]):
                return True

    return False

# Find Difference In Days Between Times
# tnew & told are strings in 'yyyy-m-d-s' format
# expects tnew to be larger (newer) than told (older)
# only used for devRep calcs, so tdiff will never be > 1 year
def get_tdiff_days(tnew, told):
    # time format safety check
    tnew = format_time(tnew)
    told = format_time(told)

    # split time strings into list of parts as ints, remove sec
    nt = list(map(int,tnew.split("-")))[:3]
    ot = list(map(int,told.split("-")))[:3]

    # build list of days in each month (months are indices)
    # each element is day of year for the 1st of that month
    # m:d - 1:31, 2:28/29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31
    # if year % 4 = 0 and month is > 2, add 1
    months = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    leap_mon = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336]

    # find day of year for tnew
    if (nt[0] % 4) == 0:
        ntd = leap_mon[nt[1]-1] + nt[2]
    else:
        ntd = months[nt[1]-1] + nt[2]

    # find day of year & days in year for told
    if (ot[0] % 4) == 0:
        otd = leap_mon[ot[1]-1] + ot[2]
        oty = 366
    else:
        otd = months[ot[1]-1] + ot[2]
        oty = 365

    # find diff in days based on if years are equal or not
    if nt[0] == ot[0]:
        diff = ntd - otd
    else:
        diff = ntd + (oty - otd)

    return diff

# Find Difference In Seconds Between Times
# tnew & told are strings in 'yyyy-m-d-s' format
# expects tnew to be larger (newer) than told (older)
# only used for devRep calcs, so tdiff will never be > 1 year
def get_tdiff_sec(tnew, told):
    # time format safety check
    tnew = format_time(tnew)
    told = format_time(told)

    # split time strings into list of parts as ints
    nt = list(map(int,tnew.split("-")))
    ot = list(map(int,told.split("-")))

    # get diff in days
    daydiff = get_tdiff_days(tnew, told)

    # if sec in nt is lower than sec in ot, add 1 day of sec and decrement daydiff
    if nt[3] < ot[3]:
        nt[3] = nt[3] + 86400
        daydiff = daydiff - 1

    # find diff in sec
    diff = (daydiff * 86400) + (nt[3] - ot[3])

    return diff

# Find List of Dates Between Dates
# tnew & told are strings in 'yyyy-m-d-s' format
# expects tnew to be larger (newer) than told (older)
# only used for devRep calcs, so tdiff will never be > 1 year
def get_dates_list(tnew, told):
    # time format safety check
    tnew = format_time(tnew)
    told = format_time(told)
    
    # split time strings into list of parts as ints, remove sec
    nt = list(map(int,tnew.split("-")))[:3]
    ot = list(map(int,told.split("-")))[:3]

    # build list of days in each month (months are indices)
    # m:d - 1:31, 2:28/29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31
    # if year % 4 = 0, add 1 to 2nd index (feb)
    months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # get difference between dates in days & init dates list
    diff = get_tdiff_days(tnew, told)
    dates = []
    
    # if diff is less than 2 days, set diff to 0 to skip for loop
    if diff < 2:
        diff = 0        # no days between dates

    # loop through diff, modify ot, and append to dates
    for i in range(diff):
        # test if day is end of month, then if month is end of year
        if ot[2] == months[ot[1]]:
            if ot[1] == 12:             # end of year, reset day & month, add 1 year
                ot[0] = ot[0] + 1
                ot[1] = 1
                ot[2] = 1
            else:                       # end of month, reset day & add 1 month
                ot[1] = ot[1] + 1
                ot[2] = 1
        else:                           # add 1 day
            ot[2] = ot[2] + 1

        # build string & append to dates if not equal to nt
        if ot != nt:
            dates.append('-'.join(map(str,ot)))

    return dates

# =============================================================================
# FUNCTIONS - DYNAMODB ITEM / JSON OBJECT BLOCKS
# -----------------------------------------------------------------------------
# INFO: Used to format data. Leaves dict and lists within the data empty.
# =============================================================================

# Build DynamoDB Item from JSON - Base Block
def build_ddbItem_block(data):
    # determine data type of data
    if isinstance(data, dict):
        # determine list of keys in dict
        dScope = list(data.keys())
        newItm = {}

        # loop through each element and determine its data type
        # ordered by likelihood for efficiency (int > dict > str > list)
        for i in dScope:
            # if int, build number and copy data
            if isinstance(data[i], (int,float)):
                newItm.update({i: { 'N': str(data[i]) }})
            # if dict, build blank base map
            elif isinstance(data[i], dict):
                newItm.update({i: { 'M': {} }})
            # if string, build string and copy data
            elif isinstance(data[i], str):
                newItm.update({i: { 'S': data[i] }})
            # if list, build blank base list
            elif isinstance(data[i], list):
                newItm.update({i: { 'L': [] }})
    elif isinstance(data, list):
        # determine number of elements in item
        dScope = range(len(data))
        newItm = []

        # loop through each element and determine its data type
        # ordered by likelihood for efficiency (int > dict > str > list)
        for i in dScope:
            # if int, build number and copy data
            if isinstance(data[i], (int,float)):
                newItm.append({'N': str(data[i])})
            # if dict, build blank base map
            if isinstance(data[i], dict):
                newItm.append({'M': {}})
            # if string, build string and copy data
            elif isinstance(data[i], str):
                newItm.append({'S': data[i]})
            # if list, build blank base list
            elif isinstance(data[i], list):
                newItm.append({'L': []})

    # return new item
    return newItm

# -----------------------------------------------------------------------------

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

# =============================================================================
# FUNCTIONS - LAYERS
# -----------------------------------------------------------------------------
# INFO: Most configs contain lists of dicts. Some contain one layer of this 
#       while others contain two. These functions are used to build these 
#       configs with less code and minimal hit to performance.
# =============================================================================

# Build DynamoDB Item from JSON - Single Layer
def build_ddbItem_slayer(data):
    # setup primary keys - data will always be a dict
    newItm = build_ddbItem_block(data)

    # iterate through list and populate maps in key1
    tLen = len(data['data'])
    for i in range(tLen):
        newItm['data']['L'].append({ 'M': build_ddbItem_block(data['data'][i]) })

    return newItm

# Build DynamoDB Item from JSON - Double Layer
def build_ddbItem_dlayer(data):
    # setup primary keys - data will always be a dict
    newItm = build_ddbItem_block(data)

    # iterate through list and populate maps in 'data'
    tLen = len(data['data'])
    for i in range(tLen):
        newItm['data']['L'].append({ 'M': build_ddbItem_block(data['data'][i]) })

        # iterate through list and populate maps in 'sdata'
        stLen = len(data['data'][i]['sdata'])
        for j in range(stLen):
            block = { 'M': build_ddbItem_block(data['data'][i]['sdata'][j]) }
            newItm['data']['L'][i]['M']['sdata']['L'].append(block)

    return newItm

# Build DynamoDB Item from JSON Object - acctUpdates
def build_ddbItem_acctUp(data):
    # build bulk of item
    newItm = build_ddbItem_dlayer(data)

    # manage the special case - iterate through both layers
    tLen = len(data['data'])
    for i in range(tLen):
        stLen = len(data['data'][i]['sdata'])
        for j in range(stLen):

            # populate 'updates'
            upList = {'L':build_ddbItem_block(data['data'][i]['sdata'][j]['updates'])}
            newItm['data']['L'][i]['M']['sdata']['L'][j]['M']['updates'].update(upList)

    return newItm

# -----------------------------------------------------------------------------

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

# Build JSON Object from DynamoDB Item - acctUpdates
def build_jsonObj_acctUp(data):
    # build bulk of object
    newObj = build_jsonObj_dlayer(data)

    # manage the special case - iterate through both layers
    tLen = len(data['data']['L'])
    for i in range(tLen):
        stLen = len(data['data']['L'][i]['M']['sdata']['L'])
        for j in range(stLen):

            # populate 'updates'
            upList = build_jsonObj_block(data['data']['L'][i]['M']['sdata']['L'][j]['M']['updates']['L'])
            newObj['data'][i]['sdata'][j].update({'updates':upList})

    return newObj

# =============================================================================
# FUNCTIONS - BUILD DYNAMODB ITEM / JSON OBJECT
# -----------------------------------------------------------------------------
# INFO: Uses the blocks & layers functions to build the relevant data.
# =============================================================================

# Build DynamoDB Item from JSON Object
def build_ddbItem(data, tblName):
    # initialize layer lists
    slayer = ['devState','devInfo','devTimer','devLogs','acctLogins']
    dlayer = ['devSched','acctRep','acctNet']

    # build item based on table
    if tblName in slayer:
        itm = build_ddbItem_slayer(data)
    elif tblName in dlayer:
        itm = build_ddbItem_dlayer(data)
    elif tblName == 'acctUpdates':
        itm = build_ddbItem_acctUp(data)
    else:
        itm = None

    return itm

# -----------------------------------------------------------------------------

# Build JSON Object from DynamoDB Item
def build_jsonObj(data, tblName):
    # initialize layer lists
    slayer = ['devState','devInfo','devTimer','devLogs','acctLogins']
    dlayer = ['devSched','acctRep','acctNet']

    # build object based on table
    if tblName in slayer:
        obj = build_jsonObj_slayer(data)
    elif tblName in dlayer:
        obj = build_jsonObj_dlayer(data)
    elif tblName == 'acctUpdates':
        obj = build_jsonObj_acctUp(data)
    else:
        obj = None

    return obj

# =============================================================================
# FUNCTIONS - DYNAMODB
# -----------------------------------------------------------------------------
# INFO: Use to manage data in DynamoDB.
# =============================================================================

# Build Key for DynamoDB Search
# acct = 'account', tbl = table as string, dev = 'dev_id'
def build_ddbKey(acct, tbl, dev=0):
    # build key & return it
    dkey = {'account': {'N': str(acct)}}
    if tbl not in ['acctRep','acctNet','acctUpdates','acctLogins']:
        dkey.update( {'dev_id':{'N': str(dev)}} )
    
    return dkey

# -----------------------------------------------------------------------------

# Get Item Data from DynamoDB
# acct = 'account', tbl = table as string, dev = 'dev_id'
def get_item(acct, tbl, dev=0):
    # build ddb key
    dkey = build_ddbKey(acct, tbl, dev)

    # get item based on table passed
    itm = db.get_item(Key=dkey,TableName=tbl)

    # if item retrieved, convert to json & return
    if len(itm) > 1:
        obj = build_jsonObj(itm['Item'], tbl)
        return obj
    else:       # else, return error message
        return 'ERROR: Data not found'

# Delete Item from DynamoDB
# acct = 'account', tbl = table as string, dev = 'dev_id'
def del_item(acct, tbl, dev=0):
    # build ddb key
    dkey = build_ddbKey(acct, tbl, dev)

    # delete item based on table passed
    db.delete_item(Key=dkey, TableName=tbl)

    return 'SUCCESS'

# Put Item in DynamoDB
def put_item(data, tbl):
    # determine if data has a 'dev_id'
    dKeys = list(data.keys())
    if 'dev_id' in dKeys:
        dev = data['dev_id']
    else:
        dev = 0
    
    # determine if 'last_update' has a failed message in it, change it
    # build current time, then remove up to 5 min to approximate time
    if data['last_update'].startswith('Failed'):
        temp = build_time()
        temp = list(map(int,temp.split("-")))
        if temp[2] != 1:
            temp[2] = temp[2] - 1
        else:
            temp[2] = 28
        data['last_update'] = str(temp[0]) + '-' + str(temp[1]) + '-' + str(temp[2]) + '-' + str(temp[3])

    # get item from table to compare
    dObj = get_item(data['account'], tbl, dev)

    # if item exists, return newer item if data is older
    if isinstance(dObj, dict):
        if isOlder(data['last_update'], dObj['last_update']):
            return dObj

    # will not run if item in table is newer or of equal age
    # should overwrite item in table if it exists
    newItm = build_ddbItem(data, tbl)
    db.put_item(TableName=tbl,Item=newItm)

    return 'SUCCESS'

# =============================================================================
# FUNCTIONS - MANAGE DATA - LOGS & REPORTS
# -----------------------------------------------------------------------------
# INFO: Use to manage devLogs & acctRep JSON objects and return them to be
#       added to DynamoDB.
# =============================================================================

# Format 'time' in devLogs to Match 'h-m-d-s' Format
# data = full devLogs data
def format_time_devLogs(data):
    # iterate through each log & format time
    for log in data['data']:
        log['time'] = format_time(log['time'])
    
    return data

# Append New devLogs JSON Data to devLogs
# data & altData should be JSON logs objects
def append_devLogs(altData):
    # get data from DDB
    data = get_item(altData['account'], 'devLogs', altData['dev_id'])
    
    # if data exists, append to logs
    if isinstance(data, dict):
        # get list of 'time' values in existing data
        oldList = []
        for log in data['data']:
            oldList.append(log['time'])
    
        # get list of 'time' values in new data without overlap
        newList = []
        for log in altData['data']:
            if log['time'] not in oldList:
                newList.append(log['time'])
    
        # append new log entries to existing log data
        for log in altData['data']:
            if log['time'] in newList:
                data['data'].append(log)

        # update 'last_update' if new data was added
        if len(newList) > 0:
            data.update( {'last_update':build_time()} )

        return data
    else:           # else, data does not exist
        return altData

# Remove JSON Data from devLogs
# data = JSON log object, altData = 'time' as a list of strings
def remove_devLogs(data, altData):
    # delete logs from data if 'time' is in altData
    for i in reversed( range( len(data['data']) ) ):
        if (data['data'][i]['time'] in altData):
            del data['data'][i]

    return data

# -----------------------------------------------------------------------------

# Add JSON Data to acctRep by Date
# data = JSON report object, altData = JSON 'data' list of dicts
def add_acctRep(data, altData):
    lup = 0         # 'last_update' flag

    # determine size of altData and append each element to newData
    aLen = len(altData)
    for i in range(aLen):
        lup = 1
        data['data'].append(altData[i])

        # while appending, add to 'ytd' sum
        data.update( {'ytd':(data['ytd'] + altData[i]['tot_usage'])} )

    # update 'days' & 'last_update' and build ddb item
    if lup == 1:
        data.update( {'last_update':build_time()} )
        data.update( {'days':len(data['data'])} )

    return data

# Remove JSON Data from acctRep with Energy Usage Tracking
# data = JSON report object, altData = JSON 'data' list of dicts
def remove_acctRep(data, altData):
    lup = 0         # 'last_update' flag

    # loop through altData (forward) & data (reversed)
    for i in range( len(altData) ):
        for j in reversed( range( len(data['data']) ) ):

            # compare 'date', loop through 'sdata' in both
            if data['data'][j]['date'] == altData[i]['date']:
                for k in range( len(altData[i]['sdata']) ):
                    for l in reversed( range( len(data['data'][j]['sdata']) ) ):

                        # compare 'dev_id', update altData & delete data if match
                        if data['data'][j]['sdata'][l]['dev_id'] == altData[i]['sdata'][k]['dev_id']:
                            
                            # updates are being made, set flag to update 'last_update'
                            lup = 1

                            # set power, add it to altData & add 'time_on'
                            power = data['data'][j]['sdata'][l]['pow_used']
                            altData[i]['sdata'][k]['pow_used'] = altData[i]['sdata'][k]['pow_used'] + power
                            altData[i]['tot_usage'] = altData[i]['tot_usage'] + power
                            altData[i]['sdata'][k]['time_on'] = altData[i]['sdata'][k]['time_on'] + data['data'][j]['sdata'][l]['time_on']

                            # subtract power & delete 'dev_id' from data, break for loop
                            data['data'][j]['tot_usage'] = data['data'][j]['tot_usage'] - power
                            data['ytd'] = data['ytd'] - power
                            del data['data'][j]['sdata'][l]
                            break

                # remove 'date' from data if empty & break after check
                if data['data'][j]['tot_usage'] == 0:
                    del data['data'][j]
                break
    
    # update 'days' & 'last_update', and return
    if lup == 1:
        data.update( {'last_update':build_time()} )
        data.update( {'days':len(data['data'])} )

    # return updated data & altData
    return [data,altData]

# Remove JSON Data from acctRep by Specific Dates
# data = JSON report object, altData = 'date' as list of strings to remove
def remove_acctRep_dates(data, altData):
    lup = 0         # 'last_update' flag

    # loop through data and compare 'date'
    # iterate in reverse to avoid index issues when deleting
    for i in reversed( range( len(data['data']) ) ):

        # if match, update 'ytd' and delete
        if data['data'][i]['date'] in altData:
            lup = 1
            data.update( {'ytd':(data['ytd'] - data['data'][i]['tot_usage'])} )
            del data['data'][i]

    # update 'days' & 'last_update', and return
    if lup == 1:
        data.update( {'last_update':build_time()} )
        data.update( {'days':len(data['data'])} )

    return data

# Remove JSON Data from acctRep by Specific Device
# data = JSON report object, altData = 'dev_id' as int to remove
def remove_acctRep_dev(data, dev):
    lup = 0         # 'last_update' flag

    # loop through data 'data' & 'sdata' and compare 'dev_id'
    # iterate in reverse to avoid index issues when deleting
    for i in reversed( range( len(data['data']) ) ):
        for j in reversed( range( len(data['data'][i]['sdata']) ) ):
            
            # if match, update 'tot_usage' & 'ytd', then del & break
            if data['data'][i]['sdata'][j]['dev_id'] == dev:
                lup = 1
                power = data['data'][i]['sdata'][j]['pow_used']
                data['data'][i].update( {'tot_usage':(data['data'][i]['tot_usage'] - power)} )
                data.update( {'ytd':(data['ytd'] - power)} )
                del data['data'][i]['sdata'][j]
                break

        # check for 'data' entries in data with 'tot_usage' == 0 and del
        if data['data'][i]['tot_usage'] == 0:
            del data['data'][i]

    # update 'days' & 'last_update', then build ddb item and return
    if lup == 1:
        data.update( {'last_update':build_time()} )
        data.update( {'days':len(data['data'])} )

    return data

# Update JSON Data in acctRep by Date
# data = JSON report object, altData = JSON 'data' list of dicts
def update_acctRep(data, altData):
    # remove all matching data from data & then add all altData
    output = remove_acctRep(data, altData)
    data = add_acctRep(output[0], output[1])
    
    # sort data by 'date' & 'dev_id'
    repSort = sorted(data['data'], key=lambda d: d['date'])
    data.update({'data':repSort})
    for i in range( len(data['data']) ):
        devSort = sorted(data['data'][i]['sdata'], key=lambda d: d['dev_id'])
        data['data'][i].update({'sdata':devSort})

    return data

# =============================================================================
# FUNCTIONS - MANAGE DATA - NET & UPDATES
# -----------------------------------------------------------------------------
# INFO: Use to manage acctNet & acctUpdates JSON objects and return them to be
#       added to DynamoDB.
# =============================================================================

# Remove Device from acctNet by 'dev_id'
# data = JSON acctNet object, dev = device 'dev_id'
def remove_acctNet_dev(data, dev):
    # get 'net_ssid' for 'dev_id'
    ssid = get_net_ssid(data['account'], dev)
    
    # return if no ssid found
    if not isinstance(ssid, str):
        return data
    
    # initialize deletion index / length of 'data'
    dLen = len(data['data'])
    n = dLen
    
    # find 'net_ssid' in data
    for i in range(dLen):
        if data['data'][i]['net_ssid'] == ssid:
            
            # find 'dev_id' in data
            for j in range(len(data['data'][i]['sdata'])):
                if data['data'][i]['sdata'][j]['dev_id'] == dev:
                    
                    # remove device from data, update 'last_update', then break
                    n = j
                    data.update( {'last_update':build_time()} )
                    break
            
            # delete 'dev_id' if found
            if n != dLen:
                del data['data'][i]['sdata'][n]
                
            # break loop
            break
    
    return data

# Update JSON Data in acctNet
# data & altData = JSON acctNet objects
def update_acctNet(data, altData):
    # 'last_update' update flag
    lup = 0
    
    # get list of 'net_ssid' in data
    nets = []
    for n in data['data']:
        nets.append(n['net_ssid'])
    
    # loop through altData and add any missing net, then clear net
    i_to_del = []
    for n in range(len(altData['data'])):
        if altData['data'][n]['net_ssid'] not in nets:
            data['data'].append(altData['data'][n])
            i_to_del.append(n)
    
    # remove matched nets from altData, reinit i_to_del
    for i in i_to_del:
        del altData['data'][i]
    i_to_del = []
    
    # if any altData['data'] remains, match 'net_ssid'
    for net1 in altData['data']:
        for net2 in data['data']:
            if net1['net_ssid'] == net2['net_ssid']:

                # for each dev in net1 & net2, match 'dev_id'
                for d in range(len(net1['sdata'])):
                    for dev in net2['sdata']:
                        if net1['sdata'][d]['dev_id'] == dev['dev_id']:

                            # on 'dev_id' match, overwrite data with altData
                            dev = net1['sdata'][d]
                            i_to_del.append(d)
                            lup = 1
                            break

                # remove matched 'dev_id' from net1
                for i in i_to_del:
                    del net1['sdata'][i]
                i_to_del = []

                # add whatever is left to net2
                for dev in net1['sdata']:
                    net2['sdata'].append(dev)
                    lup = 1
                
                # break net2 loop
                break

    # if lup was set, update 'last_update'
    if lup == 1:
        data['last_update'] = build_time()
    
    # sort data by 'net_ssid' & 'dev_id'
    netSort = sorted(data['data'], key=lambda n: n['net_ssid'])
    data.update({'data':netSort})
    for i in range( len(data['data']) ):
        devSort = sorted(data['data'][i]['sdata'], key=lambda d: d['dev_id'])
        data['data'][i].update({'sdata':devSort})

    return data

# -----------------------------------------------------------------------------

# Get Net SSID for 'dev_id' in 'account' from DynamoDB
# acct = 'account', dev = 'dev_id'
def get_net_ssid(acct, dev):
    # get acctNet for account
    net = get_item(acct, 'acctNet')
    
    # run if not a str
    if isinstance(net, dict):
        # find 'dev_id' in acctNet
        for i in range(len(net['data'])):
            for j in range(len(net['data'][i]['sdata'])):

                # compare 'dev_id'
                if net['data'][i]['sdata'][j]['dev_id'] == dev:
                    return net['data'][i]['net_ssid']

    # return none if not found
    return None

# Get List of Devices for a Specific 'net_ssid' in 'account'
# 
def get_devList_net(acct, net):
    # get acctNet & initialize devList
    data = get_item(acct, 'acctNet')
    devList = []

    # build list of 'dev_id' tied to 'net_ssid' if data exists
    if not isinstance(data, str):
        for i in range( len(data['data']) ):
            if data['data'][i]['net_ssid'] == net:
                for j in range( len(data['data'][i]['sdata']) ):

                    # if 'dev_id' is not in devList, add it
                    if data['data'][i]['sdata'][j]['dev_id'] not in devList:
                        devList.append(data['data'][i]['sdata'][j]['dev_id'])
                break

    return devList

# -----------------------------------------------------------------------------

# Append acctUpdates in DynamoDB
# tab = table or 'devRename', acct = 'account', dev = 'dev_id'
def append_acctUpdates(tab, acct, dev):
    lup = 0         # 'last_update' flag

    # load acctUpdates from DDB & determine 'net_ssid' for dev
    up = get_item(acct, 'acctUpdates')
    net = get_net_ssid(acct, dev)

    # if 'net_ssid' exists, then there is an internet-connect dev to update
    # if it does not exist, then this dev will not be pulling updates
    if not isinstance(net, str):
        return

    # manage the list of updates to append to acctUpdates
    if tab != 'devRename':
        upList = [tab]
    else:       # 'devRename' case, add all dev-relevant configs
        upList = ['devState','devInfo','devTimer','devSched','acctNet']

    # if 'net_ssid' exists, but acctUpdates does not, create it
    if not isinstance(up, dict):
        lup = 1
        up = {'account':acct, 'last_update':'', 'data':[]}
        up['data'].append({'net_ssid':net, 'sdata':[{'dev_id':dev, 'updates':upList}]})

    else:       # update existing acctUpdates
        # find 'net_ssid'
        for n in up['data']:
            if n['net_ssid'] == net:

                # find 'dev_id' and append to updates on match
                for d in n['sdata']:
                    if d['dev_id'] == dev:
                        for u in upList:

                            # manage devDelete case, otherwise, append
                            if u == 'devDelete':
                                lup = 1
                                d['updates'] = [u]
                            elif u not in d['updates']:
                                lup = 1
                                d['updates'].append(u)

                        # empty upList & break for loop on 'dev_id' match
                        upList = []
                        break

                # manage case where 'net_ssid' is found, but 'dev_id' isn't
                if len(upList) > 0:
                    lup = 1
                    n['sdata'].append({'dev_id':dev, 'updates':upList})
                    upList = []
                break       # break for loop on 'net_ssid' match

        # manage the case where no 'net_ssid' match is made
        if len(upList) > 0:
            lup = 1
            up['data'].append({'net_ssid':net, 'sdata':[{'dev_id':dev, 'updates':upList}]})

    # update 'last_update' & put updated acctUpdates back in DDB
    if lup == 1:
        up['last_update'] = build_time()

        # sort data by 'net_ssid' & 'dev_id'
        netSort = sorted(up['data'], key=lambda n: n['net_ssid'])
        up.update({'data':netSort})
        for i in range( len(up['data']) ):
            devSort = sorted(up['data'][i]['sdata'], key=lambda d: d['dev_id'])
            up['data'][i].update({'sdata':devSort})

        # put item back in ddb
        put_item(up, 'acctUpdates')

# Remove from acctUpdates by Table
# tab = table, acct = 'account', dev = 'dev_id'
def remove_acctUpdates_tab(tab, acct, dev):
    lup = 0         # 'last_update' flag

    # if 'net_ssid' exists, then there is an internet-connect dev to update
    # if it does not exist, then this dev will not be pulling updates
    net = get_net_ssid(acct, dev)
    if isinstance(net, str):
        
        # if acctUpdates exists, update acctUpdates
        up = get_item(acct, 'acctUpdates')
        if isinstance(up, dict):

            # find 'net_ssid'
            for n in up['data']:
                if n['net_ssid'] == net:

                    # find 'dev_id' and remove from updates on match
                    for d in n['sdata']:
                        if d['dev_id'] == dev:

                            # remove the update & break the loop
                            if tab in d['updates']:
                                lup = 1
                                d['updates'].remove(tab)
                            break   # break for loop on 'dev_id' match
                    break           # break for loop on 'net_ssid' match

        # update 'last_update' & put updated acctUpdates back in DDB
        if lup == 1:
            up['last_update'] = build_time()
            put_item(up, 'acctUpdates')

# Update acctUpdates from DynamoDB for 'acctNet' Updates
# acct = account as int, dev = dev_id as int
def update_acctUpdates_net(acct, dev):
    # get net_ssid for dev_id added to acctNet - assumes it always exists
    net = get_net_ssid(acct, dev)

    # get list of devices for net_ssid
    devList = get_devList_net(acct, net)

    # append acctNet to updates list for each device
    for dev in devList:
        append_acctUpdates('acctNet', acct, dev)

# Get devRename Update if Exists
def get_rename_update(acct, dev):
    # get acctUpdates & verify existence
    up = get_item(acct, 'acctUpdates')
    if isinstance(up, dict):
        
        # loop through each net & dev to find 'dev_id'
        for net in up['data']:
            for d in net['sdata']:
                if d['dev_id'] == dev:
                    
                    # check updates for devRename case
                    for u in d['updates']:
                        if u.startswith('new_id-'):
                            return int(u.split('-')[1])

    return None

# Get acctUpdates from DynamoDB by 'dev_id'
# acct = 'account', dev = 'dev_id'
def get_acctUpdates_dev(acct, dev):
    lup = 0         # 'last_update' flag
    upObj = {}

    # test if acctUpdates exists, find 'dev_id' in acctUpdates if it exists
    up = get_item(acct, 'acctUpdates')
    if isinstance(up, dict):
        for net in up['data']:
            for d in net['sdata']:

                # if match, copy 'sdata' and clear 'updates' list
                if d['dev_id'] == dev:
                    lup = 1
                    upObj.update( {'dev_id':dev} )
                    upObj.update( {'updates':d['updates']} )
                    d['updates'] = []
                    break

            # if ubObj is not empty, break outer for loop
            if len(upObj) > 0:
                break

        # update 'last_update' & put updated acctUpdates back in DDB
        if lup == 1:
            up['last_update'] = build_time()
        put_item(up, 'acctUpdates')

        # return updates object
        return upObj

    # default return if no updates are found
    return 'NO UPDATES'

# Get acctUpdates from DynamoDB by 'dev_id'
# acct = 'account', dev = 'dev_id'
def get_acctUpdates_dev(acct, dev):
    lup = 0         # 'last_update' flag
    upObj = {}

    # test if acctUpdates exists, find 'dev_id' in acctUpdates if it exists
    up = get_item(acct, 'acctUpdates')
    if isinstance(up, dict):
        for net in up['data']:
            for d in net['sdata']:

                # if match, copy 'sdata' and clear 'updates' list
                if d['dev_id'] == dev:
                    lup = 1
                    upObj.update( {'dev_id':dev} )
                    upObj.update( {'updates':d['updates']} )
                    d['updates'] = []
                    break

            # if ubObj is not empty, break outer for loop
            if len(upObj) > 0:
                break

        # update 'last_update' & put updated acctUpdates back in DDB
        if lup == 1:
            up['last_update'] = build_time()
        put_item(up, 'acctUpdates')

        # return updates object
        return upObj

    # default return if no updates are found
    return 'NO UPDATES'

# Get acctUpdates from DynamoDB by 'net_ssid'
# acct = 'account', net = 'net_ssid'
def get_acctUpdates_net(acct, net):
    lup = 0         # 'last_update' flag

    # load acctUpdates from DDB
    up = get_item(acct, 'acctUpdates')

    # test if acctUpdates exists, find 'net_ssid' in acctUpdates if it exists
    if isinstance(up, dict):
        for i in range(len(up['data'])):

            # if match, copy 'data'
            if up['data'][i]['net_ssid'] == net:
                lup = 1
                upObj = up['data'][i]

                # clear 'updates' list for each 'sdata'
                for j in reversed( range( len(up['data'][i]['sdata']) ) ):
                    for k in range(len(upObj['sdata'])):

                        # if dev_id match, manage update purge
                        if up['data'][i]['sdata'][j]['dev_id'] == upObj['sdata'][k]['dev_id']:

                            # if updates are devDelete or start with new_id-, delete dev_id and break
                            if 'devDelete' in upObj['sdata'][k]['updates']:
                                del up['data'][i]['sdata'][j]
                            elif upObj['sdata'][k]['updates'][0].startswith('new_id-'):
                                del up['data'][i]['sdata'][j]
                            else:
                                up['data'][i]['sdata'][j]['updates'] = []
                            break

                # updates found, so break for
                break

        # update 'last_update' & put updated acctUpdates back in DDB
        if lup == 1:
            up['last_update'] = build_time()
        put_item(up, 'acctUpdates')

        # return updates object
        return upObj

    # default return if no updates are found
    return 'NO UPDATES'

# Get acctUpdates from DynamoDB
# acct = 'account', dev = 'dev_id'
def get_acctUpdates(acct, dev):
    # if dev is 0, get updates for net
    if dev > 0:
        return get_acctUpdates_dev(acct, dev)
    else:   # else, get updates for dev
        net = get_net_ssid(acct, dev)
        if isinstance(net, str):
            return get_acctUpdates_net(acct, net)
        else:
            return 'NO UPDATES'

# =============================================================================
# FUNCTIONS - ENERGY REPORT
# -----------------------------------------------------------------------------
# INFO: Used to manage and update 365 day energy report data and generation.
# =============================================================================

# Get List of Account Devices
# Currently built for new version of devNet
def get_dev_list(acct):
    # build the query variables
    tbl = 'devInfo'
    vals = {':v1':{'N':str(acct)}}
    cond = 'account = :v1'
    proj = 'account,dev_id'
    
    # query DDB for all 'dev_id' tied to 'account'
    resp = db.query(TableName=tbl, ExpressionAttributeValues=vals,
        KeyConditionExpression=cond, ProjectionExpression=proj)
    
    # clean up the output
    devList = []
    for itm in resp['Items']:
        devList.append(int(itm['dev_id']['N']))

    return devList

# Purge Device Logs and Reports Older Than Date
# data = JSON object (logs/reports), tbl = 'devLogs'/'acctRep'
def purge_devData(data, tbl, date=''):
    # initialize dates & time
    dates = []
    if date == '':
        temp = (build_time().split('-'))[:3]
        temp[0] = str( int(temp[0]) - 1 )
        time = '-'.join(temp)
    else:
        time = '-'.join((date.split('-'))[:3])

    # set up key based on tbl
    if tbl == 'devLogs':
        key = 'time'
    elif tbl == 'acctRep':
        key = 'date'

    # iterate list in 'data', compare key with time, append dates if older
    for i in reversed( range( len(data['data']) ) ):
        if isOlder(data['data'][i][key], time):
            dates.append(data['data'][i][key])

    # purge & build newData based on key1, then store in DDB
    if key == 'date':
        newData = remove_acctRep_dates(data, dates)
        if date == '':
            put_item(newData, 'acctRep')
    else:
        newData = remove_devLogs(data, dates)
        if date == '':
            put_item(newData, 'devLogs')

    return newData

# Split Logs Based on Sub-Devices
# data = JSON logs list of dicts
def split_logs_subid(data):
    # initialize split_logs list & data length
    split_logs = []
    dLen = len(data)

    # loop through each log, if subid not in split logs, add new dict
    for i in range(dLen):

        # check if subid is in split_logs list and set index, else build new dict
        slLen = len(split_logs)
        n = slLen
        for j in range(slLen):
            if split_logs[j]['dev_subid'] == data[i]['dev_subid']:
                n = j

        # if n was not set, 'dev_subid' does not exist in split_logs, add it
        if n == slLen:
            slog = {'dev_subid':data[i]['dev_subid']}
            slog.update({'data':[]})
            split_logs.append(slog)

        # build simplified log dict and append to split_logs[n]['data']
        log = data[i]
        del log['trigger']
        del log['message']
        split_logs[n]['data'].append(log)

    return split_logs

# Calculate Energy Usage - Power Used
# returns wattseconds of usage; divide by 60 to get watthours
def calc_energy(time_on, v_percent, log):
    # set amps based on log, assumes 15 if no amps set
    if log['amp'] == 0:
        amp = 15

    # initialize: power (watts) = voltage (volts) * current (amps)
    volts = (log['pow'] / log['amp']) * (v_percent / 100)
    power = volts * log['amp']

    # calculate wattseconds: power * seconds
    wattsec = power * time_on

    # wattsec is type float, return as int
    return int(wattsec)

# Calculate Energy Usage - Usage Report
# Builds & returns 'sdata' dict for 'sdata' list
# u_rep = 'sdata' dict, log = single log entry dict
# date = date to calc time_on until, sec = string to append to date for special cases
def calc_usage(u_rep, log, date, sec=''):
    # if sec does not equal '', append to date
    # 0 = start of day, 86400 = EOD, expects date to not include sec
    if sec != '':
        date = date + '-' + sec

    # determine older date & use it to calc 'time_on' * 'pow_used' with correct 'v_percent'
    if isOlder(log['time'], date):
        t_on = get_tdiff_sec(date, log['time'])
        p_used = u_rep['pow_used'] + calc_energy(t_on, log['chg_to'], log)
    else:
        t_on = get_tdiff_sec(log['time'], date)
        p_used = u_rep['pow_used'] + calc_energy(t_on, log['chg_from'], log)
    u_rep.update({ 'time_on':(u_rep['time_on'] + t_on) })
    u_rep.update({ 'pow_used':p_used })

    return u_rep

# Generate Energy Report - Single Device
# acct = dev account, dev = dev_id, last = last_update
def gen_enRep_single(acct, dev, last):
    # get devLogs data for dev & purge if they exist
    data = get_item(acct, 'devLogs', int(dev))
    if isinstance(data, dict):
        # purge logs for last year
        data = purge_devData(data, 'devLogs')
        # get logs purged prior to last
        logs = purge_devData(data, 'devLogs', last)
    else:       # if no log data, cannot build report for device
        return []

    # split logs by 'dev_subid'
    slogs = split_logs_subid(logs['data'])

    # initialize - reports list & length of logs
    reps = []
    slLen = len(slogs)

    # build report - loop through each sub log
    for i in range(slLen):
        # loop through each log in split_logs and calculate
        lLen = len(slogs[i]['data'])
        for j in range(lLen):

            # get 'time' of log & trim seconds off
            time = '-'.join((slogs[i]['data'][j]['time'].split('-'))[:3])

            # check if time exists, then set index at that time
            rLen = len(reps)
            n = rLen
            for k in range(rLen):
                if time == reps[k]['date']:
                    n = k

            # if no index was set, then create new rep in reps
            if n == rLen:
                rep = {'date':time}
                rep.update({'tot_usage':0})
                rep.update({'sdata':[]})
                reps.append(rep)

            # determine if 'sdata' for current rep contains entry for current 'dev_subid', set index
            uLen = len(reps[n]['sdata'])
            m = uLen
            for k in range(uLen):
                if reps[n]['sdata'][k]['dev_subid'] == slogs[i]['dev_subid']:
                    m = k

            # if no index was set, then create new entry in 'sdata'
            if m == uLen:
                usa = {'dev_id':dev}
                usa.update({'dev_subid':slogs[i]['dev_subid']})
                usa.update({'time_on':0, 'pow_used':0})
                reps[n]['sdata'].append(usa)

            # calculate usage when not on the first log
            if j > 0:
                # calculate usage for current log for different date scenarios
                prev = slogs[i]['data'][j-1]['time']
                p_trim = '-'.join((prev.split('-'))[:3])

                # calc usage - current & previous date are equal
                if time == p_trim:
                    reps[n]['sdata'][m] = calc_usage(reps[n]['sdata'][m], slogs[i]['data'][j], prev)
                else:           # current & previous date are different
                    # update current log, then proceed to the previous
                    # if changing from v_percent > 0, calc usage since beginning of day, else, skip
                    if slogs[i]['data'][j]['chg_from'] > 0:
                        reps[n]['sdata'][m] = calc_usage(reps[n]['sdata'][m], slogs[i]['data'][j], time, sec='0')

                    # finalize prev usage: if last set v_percent is > 0, calc til EOD
                    if slogs[i]['data'][j-1]['chg_to'] > 0:

                        # find the report that the previous log is part of & update it
                        for k in range(rLen):
                            if reps[k]['date'] == p_trim:
                                l = k
                        uLen = len(reps[l]['sdata'])
                        for k in range(uLen):
                            if reps[l]['sdata'][k]['dev_subid'] == slogs[i]['dev_subid']:
                                reps[l]['sdata'][k] = calc_usage(reps[l]['sdata'][k], slogs[i]['data'][j-1], p_trim, sec='86400')

                        # find any missing dates between the current and last log
                        missing = get_dates_list(time, prev)

                        # for each date, add 'sdata' data - if dates is empty, doesn't run
                        mLen = len(missing)
                        for k in range(mLen):
                            # build a new rep for each date
                            rep = {'date':missing[k]}
                            rep.update({'tot_usage':0})
                            rep.update({'sdata':[]})

                            # build new usage for each date
                            usa = {'dev_id':dev}
                            usa.update({'dev_subid':slogs[i]['dev_subid']})
                            usa.update({'time_on':0, 'pow_used':0})

                            # clone previous log and update 'time' to match missing date
                            clone = slogs[i]['logs'][j-1]
                            clone.update({'time':(missing[k]+'-0')})

                            # calculate usage for cloned timestamp to EOD, append to rep, append rep to reps
                            usa = calc_usage(usa, clone, missing[k], sec='86400')
                            rep['sdata'].append(usa)
                            reps.append(rep)

            # update for last log as well, calc until current time
            if (j+1) == lLen:
                if slogs[i]['data'][j]['chg_to'] > 0:
                    s = (build_time().split('-'))[3]
                    reps[n]['sdata'][m] = calc_usage(reps[n]['sdata'][m], slogs[i]['data'][j], time, sec=s)

    # update 'tot_usage' based on 'pow_used' for each report entry
    rLen = len(reps)
    for i in range(rLen):
        tot_u = 0
        uLen = len(reps[i]['sdata'])
        for j in range(uLen):
            tot_u = tot_u + reps[i]['sdata'][j]['pow_used']
        reps[i].update({'tot_usage':tot_u})

    # return list of dicts for 'data'
    return reps

# Generate Energy Report - Multiple Devices
# acct = account
def gen_enRep_multi(acct):
    # purge report data for account older than 1 year if it exists
    data = get_item(acct, 'acctRep')
    if not isinstance(data, str):
        devRep = purge_devData(data, 'acctRep')
        if devRep['ytd'] == 0:
            last = ''
        else:
            last = data['last_update']
    else:
        devRep = {}
        last = ''

    # build blank devRep data if it does not exist
    if len(devRep) == 0:
        devRep.update({'account':acct})
        devRep.update({'last_update':''})
        devRep.update({'days':0, 'ytd':0, 'data':[]})

    # get list of devices tied to account
    devList = get_dev_list(acct)
    
    # build report data for each device & merge report data together
    for dev in devList:
        rep = gen_enRep_single(acct, dev, last)
        devRep = update_acctRep(devRep, rep)

    # sort devRep 'data' by 'date'
    repSort = sorted(devRep['data'], key=lambda r: r['date'])
    devRep.update({'data':repSort})

    # update 'last_update' & put new report back in DDB if data exists
    devRep['last_update'] = build_time()
    if devRep['ytd'] != 0:
        put_item(devRep, 'acctRep')

    return devRep

# =============================================================================
# FUNCTIONS - DEVICE MANAGEMENT
# -----------------------------------------------------------------------------
# INFO: Used to delete & rename devices in DynamoDB.
# =============================================================================

# Delete 'dev_id' from DynamoDB
# acct = 'account', dev = 'dev_id'
# repData = 1 if scrubbing 'dev_id' from logs & reports
def del_devid(acct, dev, repData=0):
    # build list of general tables & devs length
    genTabs = ['devState', 'devInfo', 'devTimer', 'devSched']

    # for all but devRep, devLogs, devNet, & devUpdates, delete item
    for tab in genTabs:
        del_item(acct, tab, dev)

    # if repData == 1, delete item from devLogs
    if repData == 1:
        del_item(acct, 'devLogs', dev)

    # for acctUpdates, replace updates with devDelete
    append_acctUpdates('devDelete', acct, dev)

    # for acctNet, get json obj, rebuild data if exists, put new data in table
    nObj = get_item(acct, 'acctNet')
    if isinstance(nObj, dict):
        put_item( remove_acctNet_dev(nObj, dev), 'acctNet')
        
        # update acctUpdates for acctNet
        update_acctUpdates_net(acct, dev)

    # for repData == 1, delete item from acctRep for dev if it exists
    if repData == 1:
        rObj = get_item(acct, 'acctRep')
        if isinstance(rObj, dict):
            put_item( remove_acctRep_dev(rObj, dev), 'acctRep')

    return 'SUCCESS'

# Rename 'dev_id' in DynamoDB
# acct = 'account', dev_old = old 'dev_id', dev_new = new 'dev_id'
def rename_devid(acct, dev_old, dev_new):
    # list of general tables
    genTab = ['devState','devInfo','devTimer','devSched','devLogs']

    # for each general table
    for tab in genTab:
        # get data, update 'dev_id' if existing, & put in ddb
        data = get_item(acct, tab, dev_old)
        if not isinstance(data, str):
            data.update({'dev_id':dev_new})
            put_item(data, tab)

            # del old data from ddb when done
            del_item(acct, tab, dev_old)

    # for acctNet, acctUpdates, & acctRep, rename 'dev_id' if it exists
    for tab in ['acctNet','acctUpdates', 'acctRep']:
        data = get_item(acct, tab)
        if not isinstance(data, str):

            for i in range( len(data['data']) ):
                for j in range( len(data['data'][i]['sdata']) ):
                    if data['data'][i]['sdata'][j]['dev_id'] == dev_old:

                        # if 'acctUpdates', add 'new_id-###' update
                        # updates for new_id are added after rename_devid in rest_put
                        if tab == 'acctUpdates':
                            new_update = 'new_id-' + str(dev_new)
                            data['data'][i]['sdata'][j]['updates'] = [new_update]
                        else:       # acctNet or acctRep
                            data['data'][i]['sdata'][j].update({'dev_id':dev_new})

            # put back in table (will overwrite previous data)
            put_item(data, tab)

    return 'SUCCESS'

# =============================================================================
# FUNCTIONS - COGNITO MANAGEMENT
# -----------------------------------------------------------------------------
# INFO: Used to delete, rename, link, and manage accounts in Cognito.
# =============================================================================

# List Users in Cognito User Pool
# attr = list of strings of attributes to get, all attributes retrieved if empty
def cog_list_users(attr):
    # initialize userList
    userList = []

    # get list of users in the user pool if list passed into func
    if isinstance(attr, list):
        if len(attr) == 0:
            userList = (cog.list_users(UserPoolId=pool))['Users']
        else:
            userList = (cog.list_users(UserPoolId=pool, AttributesToGet=attr))['Users']

    return userList

# List Usernames in Cognito User Pool
def cog_list_usernames():
    # declare empty list
    unList = []
    
    # get list of users as dicts
    uList = cog_list_users([])
    uLen = len(uList)
    
    # build list of strings of just the usernames
    for i in range(uLen):
        unList.append(uList[i]['Username'])
    
    # sort the list & return
    unList.sort()
    return unList

# Get a User from Cognito by Username
# user = user 'username' as string
def cog_get_user_username(username):
    # get user from user pool
    user = cog.admin_get_user(UserPoolId=pool, Username=username)
    
    # remove HTTP response and datetime keys
    del user['ResponseMetadata']
    del user['UserCreateDate']
    del user['UserLastModifiedDate']

    return user

# Get a User from Cognito by Auth Token
# token = auth token as string from connected service
def cog_get_user_token(token):
    # get the user by token
    user = cog.get_user(AccessToken=token)
    
    # remove HTTP response key
    keys = list(user.keys())
    if 'ResponseMetadata' in keys:
        del user['ResponseMetadata']

    return user

# Get Account Tied to User
def get_user_acct(username):
    user = cog_get_user_username(username)
    
    # check for account
    account = 0
    for attr in user['UserAttributes']:
        if attr['Name'] == 'custom:account':
            account = int(attr['Value'])
    
    return account

# List Groups in Cognito User Pool
def list_groups():
    # get the list of groups
    gList = response = cog.list_groups(UserPoolId=pool)
    
    # trim the results
    groups = gList['Groups']
    for i in range(len(groups)):
        del groups[i]['LastModifiedDate']
        del groups[i]['CreationDate']
    
    return groups

# List Users in Account Group in Cognito User Pool
# acct = account number
def list_group_members(acct):
    # declare vars - name = 'acct-####'
    gname = 'acct-' + str(acct)
    members = []
    
    # only get list of users in group if acct group exists
    g = list_groups()
    if gname in g:
        group = cog.list_users_in_group(UserPoolId=pool, GroupName=gname)
    
        # trim the list
        for mem in group['Users']:
            members.append(mem['Username'])

    return members

# Create Account Group in Cognito User Pool
# acct = account number to create the group for
def create_acct_group(acct):
    # declare vars - name = 'acct-####', desc = '####'
    gname = 'acct-' + str(acct)
    gdesc = str(acct)
    
    # create acct group
    resp = cog.create_group(GroupName=gname, UserPoolId=pool, Description=gdesc)

    return resp

# Delete Account Group in Cognito User Pool
# acct = account number in name of group to delete
def delete_acct_group(acct):
    # declare vars - name = 'acct-####'
    gname = 'acct-' + str(acct)
    
    # delete acct group
    cog.delete_group(GroupName=gname, UserPoolId=pool)

# Add User to Account Group in Cognito User Pool
# user = username to add to group, acct = account number of group
def add_user_acct(user, acct):
    # declare vars - name = 'acct-####'
    gname = 'acct-' + str(acct)
    
    # add user to acct
    cog.admin_add_user_to_group(UserPoolId=pool, Username=user, GroupName=gname)

# Remove User from Account Group in Cognito User Pool
# user = username to add to group, acct = account number of group
def remove_user_acct(user, acct):
    # declare vars - name = 'acct-####'
    gname = 'acct-' + str(acct)
    
    # remove user from acct
    cog.admin_remove_user_from_group(UserPoolId=pool, Username=user, GroupName=gname)
    
    # list users left in acct group
    group = cog.list_users_in_group(UserPoolId=pool, GroupName=gname)
    
    # if no users were found, delete the group
    if len(group['Users']) == 0:
        delete_acct_group(acct)

# Get List of Account Numbers
# Assumes that 'account' group names 'acct-####'
# Assumes that 'account' group descriptions are '####'
def list_acct_no():
    # declare vars
    accts = []
    
    # get a list of groups
    groups = list_groups()
    
    # trim the list to only include groups named 'acct-####'
    gLen = len(groups)
    for i in range(gLen):
        if groups[i]['GroupName'].startswith('acct-'):
            accts.append(int(groups[i]['Description']))
    
    # sort & return
    accts.sort()
    
    return accts

# Get Next Available Account Number
def get_next_acct():
    # get sorted list of account numbers as ints
    accts = list_acct_no()
    
    # find the last element and add 1
    if len(accts) > 0:
        last_index = (len(accts) - 1)
        next_avail = (accts[last_index] + 1)
    else:
        next_avail = 1
    
    return next_avail

# Set Password for User in Cognito
# user = username as a string, pwd = password to set as a string
def cog_set_pass(user, pwd):
    # initialize variables for checks
    symbols = ['^','$','*','.','[',']','{','}','(',')','?','-','%','!','@','#']
    symbols = symbols + ['\"','\\','\'','&','/',',','>','<',':',';','|','_','~','`','+','=']
    reqs_not_met = ['LENGTH','UPPER','LOWER','NUMBER','SYMBOL']
    
    # test password for meeting complexity requirements
    # start with length
    if len(pwd) > 7:
        reqs_not_met.remove('LENGTH')

    # check for upper, lower, number, and symbol
    temp = list(pwd)
    for c in temp:
        if c.isupper():
            reqs_not_met.remove('UPPER')
            break
    for c in temp:
        if c.islower():
            reqs_not_met.remove('LOWER')
            break
    for c in temp:
        if c.isnumeric():
            reqs_not_met.remove('NUMBER')
            break
    for c in temp:
        if c in symbols:
            reqs_not_met.remove('SYMBOL')
            break
    
    # if any requirements were not met, return error
    if len(reqs_not_met) > 0:
        msg = 'PASSWORD REQUIREMENTS NOT MET: '
        for i in range(len(reqs_not_met)):
            if i > 0:
                msg = msg + ', '
            msg = msg + reqs_not_met[i]
        return msg
    else:
        # set password as permanent to prevent forced reset at next login
        cog.admin_set_user_password(UserPoolId=pool, Username=user, Password=pwd, Permanent=True)
        return 0

# Add a User to Cognito User Pool
# user = acctLogins data['data'], acct = 'account', local = 'local_account'
def cog_add_user(user, acct, local):
    # verify that username does not already exist
    userList = cog_list_usernames()
    if user['username'] in userList:
        # add username exists error in 'cognito_sub' & set 'cognito_prev_pwd'
        user.update({'cognito_sub':'UNABLE TO ADD: Username already exists in pool.'})
        user.update({'cognito_prev_pwd':user['password']})
    else:
        # build attributes
        user_attr = []
        user_attr.append({'Name':'email','Value':user['email']})
        user_attr.append({'Name':'email_verified','Value':'True'})
        user_attr.append({'Name':'custom:account','Value':str(acct)})
        user_attr.append({'Name':'custom:local_account','Value':str(local)})
        user_attr.append({'Name':'custom:role','Value':user['role']})
    
        # create the Cognito user account
        # ForceAliasCreation=True needed when 'email_verified' is set to 'True'
        # Means: if alias exists, this will move the alias from the existing to the new account
        # MessageAction='SUPPRESS' used to suppress invitation email, change to 'RESEND' to send
        newUser = cog.admin_create_user(UserPoolId=pool, Username=user['username'],
            UserAttributes=user_attr, ForceAliasCreation=True, MessageAction='SUPPRESS')
    
        # update user with the Cognito user ID (sub)
        for attr in newUser['User']['Attributes']:
            if attr['Name'] == 'sub':
                user.update({'cognito_sub':attr['Value']})
                break

        # set the password for the new user
        # this step is required because account creation can only set temp passwords
        # account creation requires the Cognito user ID (sub) now for Username
        resp = cog_set_pass(user['username'], user['password'])
        if resp == 0:
            user.update({'cognito_prev_pwd':user['password']})
        else:
            user.update({'cognito_prev_pwd':''})
            user.update({'password':resp})

        # add new user to respective acct group
        add_user_acct(user['username'], acct)

    # return any error messages
    if isinstance(resp, str):
        return resp
    else:
        return user

# Add Missing Users to Cognito User Pool
# data = acctLogins data
def add_missing_users(data):
    # check if acct group exists, if not, create it
    accts = list_acct_no()
    if data['account'] not in accts:
        create_acct_group(data['account'])
        
        # if cognito keys exist in data, remove them
        for user in data['data']:
            cog_keys = list(user.keys())
            if 'cognito_sub' in cog_keys:
                del user['cognito_sub']
            if 'cognito_prev_pwd' in cog_keys:
                del user['cognito_prev_pwd']

    # iterate through each user in data['data']
    for user in data['data']:

        # test keys, if 'cognito_sub' does not exist, add user
        kList = list(user.keys())
        if 'cognito_sub' not in kList:
            user = cog_add_user(user, data['account'], data['local_account'])
    
    return data

# Delete a User from Cognito User Pool
# user = username
def cog_del_user(user):
    # get user's account number &
    # remove user from acct group & delete group if empty
    u = cog_get_user_username(user)
    for attr in u['UserAttributes']:
        if attr['Name'] == 'custom:account':
            remove_user_acct(user, int(attr['Value']))

    # disable user to revoke all auth tokens, then delete
    cog.admin_disable_user(UserPoolId=pool, Username=user)
    cog.admin_delete_user(UserPoolId=pool, Username=user)

# Delete Removed Users from Cognito User Pool
# data = acctLogins data
def del_removed_users(data):
    # declare vars
    gname = 'acct-' + str(data['account'])
    cog_list = []

    # verify acct group exists & get list of users from group
    groups = list_groups()
    if gname in groups:
        cog_list = list_group_members(data['account'])

    # create list of users in data
    data_list = []
    for user in data['data']:
        data_list.append(user['username'])
    
    # loop through cognito list & delete user if not in data_list
    for m in cog_list:
        if m not in data_list:
            cog_del_user(m)

# Delete Account Sync from Cognito User Pool
def cog_del_acct(acct):
    # get list of users in acct group
    cog_list = list_group_members(acct)
    
    # delete each account & the group
    for user in cog_list:
        cog_del_user(user)

# Modify User in Cognito
# user = username to mod, attr = attribute, val = attribute value
def cog_mod_user(user, attr, val):
    # setup user attributes
    userattr = [{'Name':attr, 'Value':val}]

    # modify/update user attributes
    cog.admin_update_user_attributes(UserPoolId=pool, Username=user, UserAttributes=userattr)

# Sync acctLogins with Cognito User Pool
# data = acctLogins data
def sync_acctLogins(data):
    # convert account to int if string
    if isinstance(data['account'], str):
        data['account'] = int(data['account'])
        
    # update account numbers if needed
    if data['local_account'] == 0:
        data['local_account'] = data['account']
        
        # check if 'account' exists & update accordingly
        accounts = list_acct_no()
        if data['account'] in accounts:
            data['account'] = get_next_acct()

    # add any accounts missing in Cognito
    data = add_missing_users(data)
    
    # delete any accounts missing in acctLogins
    del_removed_users(data)
    
    # iterate through each user
    for user in data['data']:
        
        # update any changed passwords
        if user['password'] != user['cognito_prev_pwd']:
            resp = cog_set_pass(user['username'], user['password'])
            if resp == 0:
                user['cognito_prev_pwd'] = user['password']

        # get user from Cognito to check for attribute changes
        cog_user = cog_get_user_username(user['username'])
        
        # check each attribute in cog_user for updates
        for attr in cog_user['UserAttributes']:
            
            # update any changed emails
            if attr['Name'] == 'email':
                if attr['Value'] != user['email']:
                    cog_mod_user(user['username'], 'email', user['email'])
            # update any changed roles
            elif attr['Name'] == 'custom:role':
                if attr['Value'] != user['role']:
                    cog_mod_user(user['username'], 'custom:role', user['role'])

    return data

# Authenticate User
def auth_user(username, password):
    # get list of usernames
    user_list = cog_list_usernames()
    
    # convert everything to lower case for case-insensitive matching
    username = username.casefold()
    for u in user_list:
        u = u.casefold()
    
    # test if username is in the list
    if username not in user_list:
        return f'NOT FOUND: {username}'
    
    # if still running, get the user account number
    acct = get_user_acct(username)
    
    # get the account acctLogins data
    logins = get_item(acct, 'acctLogins')
    
    # test logins data
    if not isinstance(logins, dict):
        return 'NO ACCTLOGINS DATA'
    
    # locate the user in the data & compare the passwords
    for u in logins['data']:
        if u['username'] == username:
            if u['password'] == password:
                return logins
    
    return 'INVALID PASSWORD'

# =============================================================================
# FUNCTIONS - ACCOUNT MANAGEMENT
# -----------------------------------------------------------------------------
# INFO: Used to delete, rename, link, and manage accounts in DynamoDB.
# =============================================================================

# Delete 'account' from DynamoDB
# acct = 'account'
def del_acct(acct):
    # get list of 'dev_id' tied to account
    devs = get_dev_list(acct)

    # init list of tables
    devTabs = ['devState','devInfo','devTimer','devSched','devLogs']
    acctTabs = ['acctRep','acctNet','acctUpdates','acctLogins']

    # delete all items in all dev tables for acct
    for tab in devTabs:
        for i in range(len(devs)):
            del_item(acct, tab, devs[i])

    # delete all items in all acct tables for acct
    for tab in acctTabs:
        del_item(acct, tab)
    
    # delete all Cognito users tied to account    
    cog_del_acct(acct)

    return 'SUCCESS'

# =============================================================================
# FUNCTIONS - REST API
# -----------------------------------------------------------------------------
# INFO: Used to get, put, delete, & update items in DynamoDB.
# =============================================================================

# HTTP REST Response
def respond(err, res=None):
    if isinstance(res, dict):
        res = json.dumps(res)
    elif not isinstance(res, str):
        res = str(res)
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

# -----------------------------------------------------------------------------

# REST PUT - (dev & app) put devConfig data in DDB table
    # param1: table= devConfig or 'devRename'
    # param2: data= JSON data or {'account':acct,'dev_id':dev,'new_id':ndev}
    # special case (app only) - rename 'dev_id'
# tab = table to put data in, data = data to put, src = dev or app
def rest_put(tab, data, src):
    # init net_dev
    net_dev = 0

    # test the data type, if str, convert to JSON
    if isinstance(data, str):
        data = json.loads(data)

    # copy 'dev_id' for acctNet PUT
    if tab == 'acctNet':
        net_dev = data['data'][0]['sdata'][0]['dev_id']
    
    # if src is /dev, check for devRename update if devState, devLogs, or acctNet
    if src == '/dev':
        if tab in ['devState','devLogs']:
            new_id = get_rename_update(data['account'], data['dev_id'])
        elif tab == 'acctNet':
            new_id = get_rename_update(data['account'], net_dev)
        else:       # catch case
            new_id = ''
        
        # check new_id & assign to 'dev_id' if an int
        if isinstance(new_id, int):
            if tab == 'acctNet':
                net_dev = new_id
            else:
                data['dev_id'] = new_id

    # try putting data in table if it is not 'devRename' or 'devLogs'
    if tab == 'devLogs':        # handle the devLogs case, append new logs
        data = format_time_devLogs(data)        # format 'time' in devLogs
        data = append_devLogs(data)             # append logs
        resp = put_item(data, tab)              # get response
    elif tab == 'devRename':    # handle rename case, update 'dev_id' to 'new_id'
        resp = rename_devid(data['account'], data['dev_id'], data['new_id'])
        data['dev_id'] = data['new_id']
        append_acctUpdates(tab, data['account'], data['new_id'])
    elif tab == 'acctNet':      # handle acctNet case, if one device, update
        if (len(data['data']) == 1) and (len(data['data'][0]['sdata']) == 1):
            netObj = get_item(data['account'], 'acctNet')
            if isinstance(netObj, dict):        # netObj exists
                resp = put_item(update_acctNet(netObj, data), tab)
            else:                               # no acctNet in ddb
                resp = put_item(data, tab)
            update_acctUpdates_net(data['account'], net_dev)
        else:                   # not a new device, overwrite acctNet
            resp = put_item(data, tab)
    elif tab == 'acctLogins':   # handle acctLogins 'last_update' & sync
        data['last_update'] = build_time()
        data = sync_acctLogins(data)
        resp = put_item(data, tab)
    else:                       # handle the rest
        resp = put_item(data, tab)

    # handle updates from app for acctUpdates if data successfully put in table
    if src == '/app':
        if resp == 'SUCCESS':
            if tab != 'acctLogins':
                append_acctUpdates(tab, data['account'], data['dev_id'])
    else:       # remove tab from acctUpdates if src is '/dev'
        # rest_put will always return newer data, so no need stay in acctUpdates
        if tab != 'acctNet':
            remove_acctUpdates_tab(tab, data['account'], data['dev_id'])
        else:
            remove_acctUpdates_tab(tab, data['account'], net_dev)

    return resp

# REST GET - (dev & app) get devConfig data from DDB table
    # param1: table= devConfig
    # param2: id= {'account':acct,'dev_id':dev}
        # dev = 0 for acctRep & acctNet, also acctUpdates if polling by net_ssid
# tab = table to get data from, data = id of data to get
def rest_get(tab, data):
    # test the data type, if str, convert to JSON
    if isinstance(data, str):
        data = json.loads(data)

    # get requested data based on table name
    if tab == 'acctUpdates':
        resp = get_acctUpdates(int(data['account']), int(data['dev_id']))
    elif tab == 'acctRep':
        resp = gen_enRep_multi(int(data['account']))
    elif tab == 'acct_list':
        resp = list_acct_no()
    elif tab == 'acct_next':
        resp = get_next_acct()
    elif tab == 'user_list':
        resp = cog_list_usernames()
    elif tab == 'auth_user':
        resp = auth_user(data['account'], data['dev_id'])
    elif tab == 'dev_list':
        resp = get_dev_list(int(data['account']))
    else:
        resp = get_item(int(data['account']), tab, int(data['dev_id']))
        remove_acctUpdates_tab(tab, int(data['account']), int(data['dev_id']))

    return resp

# REST DELETE - (app only) delete 'dev_id' from all DDB tables
    # param1: id= {'account':acct,'dev_id':dev} (set dev=0 if deleting entire acct)
    # param2: flag= 0 or 1 (0 = keep logs/rep data, 1 = remove logs/rep data)
# data = id of data to get, flag = flag to keep/remove logs/rep data
def rest_del(data, flag):
    # test the data type, if str, convert to JSON
    if isinstance(data, str):
        data = json.loads(data)

    # if 'dev_id' is not 0, delete 'dev_id' from account
    if data['dev_id'] > 0:
        resp = del_devid(data['account'], data['dev_id'], flag)
    else:       # else, delete account
        resp = del_acct(data['account'])

    return resp

# =============================================================================
# MAIN
# -----------------------------------------------------------------------------
# INFO: Primary function to handle REST API calls from the API Gateway.
# =============================================================================

def test_s3output(event):
    s3 = boto3.client('s3')
    
    # setup s3 info
    bucket = 'a2bsmartdev'
    key = 'test/app_event-' + event['queryStringParameters']['table'] + '-' + build_time() + '.json'

    # store body
    body = json.dumps(event)
    #body = event
    #body = {'body':json.dumps(event)}
    #body.update({'inner_body':json.loads(event['body'])})

    # take the event and print it to a file in s3
    s3.put_object(Bucket=bucket, Key=key, Body=body)


# Run core functionality in the Lambda handler function
def lambda_handler(event, context):

    # API Gateway REST event structure (METHOD /path?parameterName=data)
        # event['httpMethod'] = "METHOD"
        # event['path'] = "/path"
        # event['queryStringParameters']['parameterName'] = data
        # event['body'] = "Whatever is passed as data for PUT request."
    
    #if event['path'] == '/app':
    #    test_s3output(event)
    #test_s3output(event)
    
    #if event['path'] == '/dev':
    #    if event['httpMethod'] == 'PUT':
    #        if isinstance(event['body'], str):
    #            data = json.loads(event['body'])
                
    #        temp = list(map(int,data['last_update'].split("-")))
    #        if temp[2] != 1:
    #            temp[2] = temp[2] - 1
    #        else:
    #            temp[2] = 28
    #        data['last_update'] = str(temp[0]) + '-' + str(temp[1]) + '-' + str(temp[2]) + '-' + str(temp[3])
            
    #        event['body'] = json.dumps(data)

    if event['httpMethod'] == 'PUT':
        return respond(None, rest_put(event['queryStringParameters']['table'], event['body'], event['path']))
    elif event['httpMethod'] == 'GET':
        query = {'account':event['queryStringParameters']['acct'],'dev_id':event['queryStringParameters']['dev']}
        return respond(None, rest_get(event['queryStringParameters']['table'], query))
    elif event['httpMethod'] == 'DELETE':
        del_id = {'account':int(event['queryStringParameters']['acct']),'dev_id':int(event['queryStringParameters']['dev'])}
        return respond(None, rest_del(del_id, int(event['queryStringParameters']['flag'])))
    elif event['httpMethod'] == 'POST':
        test_s3output(event)
        return respond(None, 'Alexa request received.')
    else:
        return respond(None,'Unsupported method.')
