import boto3
import json
from boto3.dynamodb.conditions import Key
import datetime
import urllib3
from datetime import datetime as dt
from datetime import timedelta


def update_cache(dynamodb,rec,slot):
    status='success'
    tname = 'vrp_cache' + '_' + slot
    try:
        table = dynamodb.Table(tname)
        response = table.update_item(
            Key={
                'location_hash':rec['hash']
            },
            UpdateExpression="set last_refresh=:lr,dist=:d, dur=:t",
            ExpressionAttributeValues={
                ':t': rec['time'],
                ':lr':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                ':d': rec['dist']
            },
            ReturnValues="UPDATED_NEW")
    except BaseException as e:
        raise Exception("unable to update data =>",str(e))
        status='failure'
    return status

def get_del_slot(trip_start):
    a1 = dt.strptime(trip_start, "%d/%m/%Y %H:%M:%S")

    s0 = '00:00:00'
    s1 = '06:00:00'
    s2 = '12:00:00'
    s3 = '18:00:00'
    s4 = '23:59:00'


    if ((a1.time() < dt.strptime(s1, '%H:%M:%S').time()) & (a1.time() > dt.strptime(s0, '%H:%M:%S').time())):
        slot = '1'
    elif (a1.time() < dt.strptime(s2, '%H:%M:%S').time()):
        slot = '2'
    elif (a1.time() < dt.strptime(s3, '%H:%M:%S').time()):
        slot = '3'
    else:
        slot = '4'

    return slot



def check_cache(dynamodb,hash_key,slot):
    cache={}
    cache_rec={}
    tname = 'vrp_cache'+'_'+slot
    table = dynamodb.Table(tname)
    cache = table.query(
        KeyConditionExpression=Key('location_hash')
            .eq(hash_key)
    )
    if cache['Count'] !=0:
        rec = cache.get('Items')[0]
        #put the last refresh logic here
        if (datetime.datetime.strptime(rec.get('last_refresh'),'%Y-%m-%d %H:%M:%S') < datetime.datetime.now()-timedelta(days=30)):
            print(hash_key, 'refreshed hashkey')
            result = {'distance': -1, 'time': -1}
        else:
            result={'distance':float(rec.get('dist')),'time':float(rec.get('dur'))}
    else:
        result = {'distance': -1,'time':-1}

    return result

def send_request(origin_addresses, dest_addresses, API_key, trip_start):
    """ Build and send request for the given origin and destination addresses."""
    def build_address_str(addresses):
        add_str=''
        add_str="|".join([a.replace("|",",") for a in addresses])
        return add_str

    """ this part needs some change """
    tp_time = dt.strptime(trip_start, "%d/%m/%Y %H:%M:%S")
    if tp_time > datetime.datetime.now():
        trip_start_time = tp_time

    else:
        trip_start_time = datetime.datetime.now()

    trip_start = str(int((trip_start_time - datetime.datetime(1970, 1, 1)).total_seconds()))

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&avoid=tolls' + '&departure_time=' + \
              trip_start
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)

    request = request + '&origins=' + origin_address_str + '&destinations=' + \
              dest_address_str + '&key=' + API_key

    print(request)

    http = urllib3.PoolManager()
    resp = http.request('GET', request)
    response = json.loads(resp.data)

    return response

def hash_mapping(origins, destinations, distances, API_key, trip_start):

    origins_list = list(origins)
    destinations_list = list(destinations)

    or_len = len(origins)
    des_len = len(destinations)

    max_elements = 100
    max_cols = 25

    num_addresses = max(or_len, des_len)

    if num_addresses <= 25:
        max_rows = max_elements // num_addresses
    else:
        max_rows = max_elements // max_cols

    qr, rr = divmod(or_len, max_rows)
    # (2,3) ==> (15,6)
    qc, rc = divmod(des_len, max_cols)
    # (0,15) ==> (15,25)

    # below we are adhering to less than 100 elements and less than 25 columns per google maps request

    if num_addresses <= 25:
        dest_addresses = destinations_list

        for i in range(qr):
            origin_addresses = origins_list[i * max_rows: (i + 1) * max_rows]
            response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
            distances = pop_distances(origin_addresses, dest_addresses, response, distances)

        # Get the remaining remaining r rows, if necessary.
        if rr > 0:
            origin_addresses = origins_list[qr * max_rows: qr * max_rows + rr]
            response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
            distances = pop_distances(origin_addresses, dest_addresses, response, distances)

        # for k,v in distances_rr.items():
        #     distances[k] = distances_rr[k]

        print("dest_addresses ", dest_addresses)
        print("origin_addresses ", origin_addresses)

        return distances

    else:
        for i in range(qr):
            origin_addresses = origins_list[i * max_rows: (i + 1) * max_rows]

            for j in range(qc):
                dest_addresses = destinations_list[j * max_cols: (j + 1) * max_cols]
                response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
                distances = pop_distances(origin_addresses, dest_addresses, response, distances)

            if rc > 0:
                dest_addresses = destinations_list[qc * max_cols: qc * max_cols + rc]
                response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
                distances = pop_distances(origin_addresses, dest_addresses, response, distances)
        if rr > 0:
            origin_addresses = origins_list[qr * max_rows: qr * max_rows + rr]
            for j in range(qc):
                dest_addresses = destinations_list[j * max_cols: (j + 1) * max_cols]
                response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
                distances = pop_distances(origin_addresses, dest_addresses, response, distances)

            if rc > 0:
                dest_addresses = destinations_list[qc * max_cols: qc * max_cols + rc]
                response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
                distances = pop_distances(origin_addresses, dest_addresses, response, distances)

        return distances

def split_requests(add_info, API_key, trip_start):

    def build_address_str(addresses):
        add_str=''
        add_str="|".join([ a.replace("|",",") for a in addresses])
        return add_str

    destinations = add_info.get('origins')
    origins = add_info.get('destinations')
    distances = {}
    distances = hash_mapping(origins, destinations, distances, API_key, trip_start)
    distances = hash_mapping(destinations, origins, distances, API_key, trip_start)

#     origins_list = list(origins)
#     destinations_list = list(destinations)
#
#     or_len = len(origins)
#     des_len = len(destinations)
#
#     max_elements = 100
#     max_cols = 25
#
#     num_addresses = max(or_len,des_len)
#
#     if num_addresses <= 25:
#         max_rows = max_elements // num_addresses
#     else:
#         max_rows = max_elements // max_cols
#
#     qr, rr = divmod(or_len, max_rows)
#     #(2,3) ==> (15,6)
#     qc, rc = divmod(des_len, max_cols)
#     #(0,15) ==> (15,25)
#
# # below we are adhering to less than 100 elements and less than 25 columns per google maps request
#     distances = {}
#     if num_addresses <= 25:
#         dest_addresses = destinations_list
#
#         for i in range(qr):
#             origin_addresses = origins_list[i * max_rows: (i + 1) * max_rows]
#             response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
#             distances = pop_distances(origin_addresses, dest_addresses, response, distances)
#
#
#         # Get the remaining remaining r rows, if necessary.
#         if rr > 0:
#             origin_addresses = origins_list[qr * max_rows: qr * max_rows + rr]
#             response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
#             distances = pop_distances(origin_addresses, dest_addresses, response, distances)
#
#         # for k,v in distances_rr.items():
#         #     distances[k] = distances_rr[k]
#
#
#         print("dest_addresses ",dest_addresses)
#         print("origin_addresses ", origin_addresses)
#
#         return distances
#
#     else:
#         for i in range(qr):
#             origin_addresses = origins_list[i * max_rows: (i + 1) * max_rows]
#
#             for j in range(qc):
#                 dest_addresses = destinations_list[j * max_cols: (j + 1) * max_cols]
#                 response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
#                 distances = pop_distances(origin_addresses, dest_addresses, response, distances)
#
#             if rc > 0:
#                 dest_addresses = destinations_list[qc * max_cols: qc * max_cols + rc]
#                 response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
#                 distances = pop_distances(origin_addresses, dest_addresses, response, distances)
#         if rr > 0:
#             origin_addresses = origins_list[qr * max_rows: qr * max_rows + rr]
#             for j in range(qc):
#                 dest_addresses = destinations_list[j * max_cols: (j + 1) * max_cols]
#                 response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
#                 distances = pop_distances(origin_addresses, dest_addresses, response, distances)
#
#             if rc > 0:
#                 dest_addresses = destinations_list[qc * max_cols: qc * max_cols + rc]
#                 response = send_request(origin_addresses, dest_addresses, API_key, trip_start)
#                 distances = pop_distances(origin_addresses, dest_addresses, response, distances)

    return distances

def pop_distances(origins, destinations,resp_data,distances):


    for idx,val in enumerate(origins):
        for idx2,val2 in enumerate(destinations):
            temp = {'dist': 0, 'time': 0}
            hash = val + "-" + val2
            dist = resp_data.get('rows')[idx].get('elements')[idx2].get('distance').get('value')
            time = resp_data.get('rows')[idx].get('elements')[idx2].get('duration').get('value')
            temp['dist'] = dist
            temp['time'] = time
            temp['hash'] = hash
            distances[hash] = {'dist':dist,'hash':hash,'time':time}
            # add the reverse hash also
            # rev_hash=val2 + "-" + val
            # distances[rev_hash]= {'dist':dist,'hash':rev_hash,'time':time}

    return distances

def build_unique_address_list(unknown_addresses):
    unique_pairs = []
    for key in unknown_addresses.keys():
        # rev_key = key.split("-")[1] + "-" + key.split("-")[0]  # check if the reverse key is already available.
        # if not (key in unique_pairs) and not (rev_key in unique_pairs):  # not already added
        if not (key in unique_pairs):
            unique_pairs.append(key)
    origin_addresses = set([key.split("-")[0] for key in unique_pairs])
    dest_addresses = set([key.split("-")[1] for key in unique_pairs])

    return {'origins':origin_addresses,'destinations':dest_addresses}

def build_matrices(input_addresses,matrix):
    dist_matrix = []
    time_matrix = []

    for idx, val in enumerate(input_addresses):
        dm_mat1 = []
        tm_mat1 = []
        for idx2, val2 in enumerate(input_addresses):
            hash = val + "-" + val2
            # cache_rec = check_cache(dynamodb, hash, slot)
            # dist = cache_rec.get('distance')
            # time = cache_rec.get('time')
            if matrix.get(hash):
                dm_mat1.append(matrix.get(hash).get('dist'))
                tm_mat1.append(matrix.get(hash).get('time'))
            else:
                print("cannot find hash: ", hash)

        dist_matrix.append(dm_mat1)
        time_matrix.append(tm_mat1)

    return dist_matrix, time_matrix

def main(input_addresses, trip_start, API_key):

    add_info = {}
    dm = {}
    dynamodb = boto3.resource('dynamodb', endpoint_url="https://dynamodb.us-east-1.amazonaws.com",
                              region_name='us-east-1')

    print_cond = 0
    matrix = {}
    unknown_addresses={}
    slot = get_del_slot(trip_start)
    print('slot is: ',slot)

# First Round
    for idx, val in enumerate(input_addresses):
        for idx2, val2 in enumerate(input_addresses):
            temp = {'dist': 0, 'time': 0}
            hash = val + "-" + val2
            cache_rec=check_cache(dynamodb,hash,slot)
            dist=cache_rec.get('distance')
            time=cache_rec.get('time')
            temp['dist'] = dist
            temp['time'] = time
            temp['hash'] = hash
            if dist == -1 :
                unknown_addresses[hash]=temp
            matrix[hash] = temp
    # TODO Update back the "matrix" to have data for all pairs

    if unknown_addresses:
        add_info=build_unique_address_list(unknown_addresses)
        dm = split_requests(add_info, API_key, trip_start)
        print(dm)

        for idx, dm_rec in enumerate(dm.values()):
            stat = update_cache(dynamodb, dm_rec, slot)
            if stat != 'success':
                raise Exception("Unable to save data to cache. rec is =>", dm_rec)
    else:
        print("No new addresses to be used. All addresses satisfied from cache")


    for key,val in dm.items():
        matrix[key]=dm[key]

    print(matrix)

    distance_matrix, time_matrix = build_matrices(input_addresses,matrix)
    # distance_matrix,time_matrix = build_matrices(input_addresses,slot, dynamodb)

    print(distance_matrix)
    print(time_matrix)
    print()


    print("Address pairs count :", len(matrix.keys()))
    print( "Unknown address pairs :",len(unknown_addresses.keys()))
    print( "Unknown Origins :{} , \nUnknown Destinations : {}".format(add_info.get('origins'),add_info.get('destinations')))
    print("Distance matrix for unknowns = ", dm, "\ncount is ",len(dm.keys()))
    print("Summary:\nTotal Pairs={}\nKnown Pairs={}\nUnknown Pairs={}\nGoogle Returned={}"\
        .format(
            len(matrix.keys()),
            len(matrix.keys()) -len(unknown_addresses.keys()),
            len(unknown_addresses.keys()),
            len(dm.keys())
                )
            )

    return distance_matrix,time_matrix













