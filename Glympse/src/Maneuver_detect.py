import googlemaps
import json
import numpy as np
import pandas as pd
import mpu

import speedlimit


def smooth(speed, box_pts):
    """Smooth the speed data

    :param speed: a list of data that you want to smooth
    :type speed: list
    :param box_pts: the number of box points
    :type box_pts: int
    :return: a list of data after smooth
    """
    box = np.ones(box_pts) / box_pts
    speed_smooth = np.convolve(speed, box, mode='same')
    return speed_smooth


def calculate_speed_google(lat, long, time):
    """Calculate a list of speed between two points by using Google API

    :param lat: a list of latitude
    :type lat: list
    :param long: a list of longitude
    :type long: list
    :param time: a list of timestamp
    :return: a list of speed that the length is equal to input
    """
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    speed = []
    speed.append(0)
    for i in range(len(lat) - 1):
        t = time[i + 1] - time[i]                                              # time interval
        start_point = [lat[i], long[i]]
        end_point = [lat[i + 1], long[i + 1]]
        direction_result = gmap.directions(start_point, end_point, mode="driving")
        string = direction_result[0]['legs'][0]['distance']['text']
        sp = float(string.split()[0]) * 0.3048 / t                             # Covert unit from ft to m
        speed.append(sp)
    speed[0] = speed[1]                                                        # Cause the first point didn't have
    return speed                                                               # forward point to look at so
                                                                               # set it equal to the second point


def RMSE(speed_cal, speed):
    """Calculate the root mean square error between the true speed and calculated speed

    :param speed_cal: a list of speed after calculated
    :param speed: a list of truth speed
    :return: the error number, Int
    """
    total = 0
    error_total = []
    for i in range(len(speed_cal)):
        total += abs(speed[i] - speed_cal[i])
        error_total.append(speed[i] - speed_cal[i])
        error = total / len(speed_cal)

    return error


def calculate_speed_cal(lat, long, time):
    """Calculate a list of speed between two points by using mpu (the linear distance between two points)

    :param lat: a list of latitude
    :type lat: list
    :param long: a list of longitude
    :type long: list
    :param time: a list of timestamp
    :return: a list of speed that the length is equal to input
    """
    speed = []
    speed.append(0)
    for i in range(len(lat) - 1):
        t = time[i + 1] - time[i]
        lat1 = lat[i]
        lon1 = long[i]
        lat2 = lat[i + 1]
        lon2 = long[i + 1]
        dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2)) * 1000
        speed.append(dist / t)
    speed[0] = speed[1]

    return speed


def google_speed(lat1, lon1, lat2, lon2, time):
    """Calculate the single speed between two points by using Google API

    :param lat1: start point latitude
    :param lon1: start point longitude
    :param lat2: end point latitude
    :param lon2: end point longitude
    :param time: time interval (second)
    :return: speed , float
    """
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    start_point = [lat1, lon1]
    end_point = [lat2, lon2]
    direction_result = gmap.directions(start_point, end_point, mode="driving")
    string = direction_result[0]['legs'][0]['distance']['text']
    sp = float(string.split()[0]) * 0.3048 / time
    return sp


def cal_speed(lat1, lon1, lat2, lon2, time):
    """Calculate the single speed between two points by using mpu

        :param lat1: start point latitude
        :param lon1: start point longitude
        :param lat2: end point latitude
        :param lon2: end point longitude
        :param time: time interval (second)
        :return: speed , float
    """
    dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2)) * 1000
    res = dist / time
    return res


def fill_speed(speed, time, lat, long):
    """Filling out the missing speed point, this function will check every point in given list
       if the speed = None or 0, I will recalculate the speed

    :param speed: a list of speed
    :param time: a list of timestamp
    :param lat: a list of latitude
    :param long: a list of longitude
    :return: a list of speed after filling out
    """
    speed_revise_number = 0
    no_smooth = 0
    for i in range(len(speed) - 1):
        if speed[i] == None:
            speed_revise_number += 1        # count the number of speed point calculate
            t = time[i + 1] - time[i]
            if t == 0: t = 1                # if time interval less than 1 second set it to one
            res = cal_speed(lat[i], long[i], lat[i + 1], long[i + 1], t)
            if res < 0.1: res = 0           # if calculated speed less tham 0.1m/s set it to zero
            speed[i] = res
            no_smooth = 1
        else:
            if speed[i] <= 0:
                speed_revise_number += 1
                t = time[i + 1] - time[i]
                if t == 0: t = 1
                res = cal_speed(lat[i], long[i], lat[i + 1], long[i + 1], t)
                if res < 0.1: res = 0
                speed[i] = res

    if speed[-1] == None:
        speed[-1] = speed[-2]
    if speed[-1] <= 0:
        speed[-1] = speed[-2]

    if no_smooth == 0:
        speed = smooth(speed, 3)

    return speed


def fill_heading(heading):
    """Filling out the missing heading point, this function will check out every point in the given list
       if the heading = None, I will fill out the missing heading

    :param heading: a list of heading angle
    :return: a list of heading after filling out
    """
    headnone = False
    if heading[0] == None:
        headnone = True
    for i in range(len(heading) - 1):
        if headnone == True:
            if heading[i] != None:
                heading[0:i] = [heading[i]] * i
                headnone = False
        else:
            if heading[i] == None:
                if heading[i + 1] == None:
                    heading[i] = heading[i - 1]
                else:
                    heading[i] = (heading[i - 1] + heading[i + 1]) / 2
    if heading[-1] == None:
        heading[-1] = heading[-2]
    return heading


def organize_data(data):
    """Organize the data, including filling out missing points & delete too short location points list
       & delete unuseful data

    :param data: a dict of data
    :return: a dict of data after processing
    """
    delkey = []
    for key, value in data.items():
        if len(value[0]) < 30:
            delkey.append(key)
            continue
        value[2] = fill_speed(value[2], value[4], value[0], value[1])
        value[3] = fill_heading(value[3])

        if value[3][0] == None:
            delkey.append(key)
        else:
            if np.mean(value[3]) == 0:
                delkey.append(key)

    for i in range(len(delkey)):
        del data[delkey[i]]
    return data


def find_turning(heading):
    """Use heading angle to find the turning maneuver

    :param heading:a list of heading angle
    :return breakpoint:a list of start point & end point of the turning [start,end,start,end,start,end]
    :return number : the count of the turning
    """
    breakpoint = []
    start = 0
    number = 0
    for i in range(len(heading) - 2):
        diff = abs(heading[i + 1] - heading[i])
        if diff > 19 and diff < 70 and start == 0:                              # if the angle change large than 19 less
                                                                                # than 70 assume the turning began
            if i - 2 < 0:
                breakpoint.append(0)
            else:
                breakpoint.append(i - 2)
            start = 1
        if diff < 5 and start == 1:                                             # if the angle change less than 5 assume turning end

            angle_diff = abs(heading[i + 1] - heading[breakpoint[-1]])          # if the angle change between start & end assume not turning

            if (angle_diff < 30 or angle_diff > 150):
                del breakpoint[-1]
                start = 0
                continue
            else:
                breakpoint.append(i + 2)
                start = 0
                number += 1
    if len(breakpoint) % 2 != 0:
        del breakpoint[-1]
    return breakpoint, number


def find_dic_turning(data):
    """ Find the turning in every task and store to a new dict that including a list of turning start & end point
        and the count of turning

    :param data: a dict of data
    :return dict_turning: a dict of turning list & the count of turning
            key : task id
            value : an array including a list of turning start & end point and the count of turning
            [breakpoint, number]
    :return total_number: a count of turning in the data, int
    """
    dict_turning = {}
    total_number = 0
    for key, value in data.items():
        breakpoint, number = find_turning(value[3])
        total_number += number
        if len(breakpoint) != 0:
            dict_turning[key] = [breakpoint, number]
    return dict_turning, total_number


def calculate_average_speed(data, key, turning_list, number_turning):
    """ Calculate the average turning speed

    :param data: the dict of the data
    :param key: task id
    :param turning_list: a list of turning start & end points
    :param number_turning: the count of turning
    :return: average turning speed, float
    """
    total_speed = 0
    for i in range(0, len(turning_list), 2):
        total_speed += np.mean(data[key][2][turning_list[i]:turning_list[i + 1]])
    average_speed = total_speed / number_turning
    return average_speed


def count_fast_turn(data, key, turning_list):
    """Count the number of fast turn number

    :param data: a dict of data
    :param key: task id
    :param turning_list: a list of turning start & end points
    :return: the count of fast turn, int
    """
    fast_turn = 0
    for i in range(0, len(turning_list), 2):
        turn_speed = np.mean(data[key][2][turning_list[i]:turning_list[i + 1]])
        if turn_speed > 6.7:
            fast_turn += 1

    return fast_turn


def store_speed(dict_turning, data):

    aver_speed = []
    for key, value in dict_turning.items():
        a_speed = calculate_average_speed(data, key, dict_turning[key][0], dict_turning[key][1])
        if a_speed < 100:
            # ticket.append(key)
            aver_speed.append(a_speed)

    df = pd.DataFrame({  # 'ticket_id': ticket,
        'Turning speed': aver_speed
    })

    df.to_csv("Maneuver detect/Population data/total_turning.csv", mode='a', index=False, header=False)


def store_hb(hb_number, time):
    df = pd.DataFrame([{  # 'ticket_id': ticket,
        'HB_number/time': hb_number/time,
    }])

    df.to_csv("Maneuver detect/Population data/total_HB.csv", mode='a', index=False)#, header=False)


def store_ACC(ACC_number, time):
    df = pd.DataFrame([{  # 'ticket_id': ticket,
        'ACC_number/time': ACC_number/time,
    }])

    df.to_csv("Maneuver detect/Population data/total_ACC.csv", mode='a', index=False)#, header=False)


def store_ov(total_ov, ov_duration, time):
    if len(total_ov) == 0:
        ov_mean = 0
    else:
        ov_mean = np.mean(total_ov)

    df = pd.DataFrame([{  # 'ticket_id': ticket,
        'ov_duration': ov_duration,
        'Average over speed': total_ov,
        'time': time,
        #'distance': distance,
    }])

    df.to_csv("Maneuver detect/Population data/total_speeding.csv", mode='a', index=False)#, header=False)


def find_ACC(speed, time):
    """Use speed to find the acceleration maneuver, Acceleration exceeds 3m per second for more than two seconds

    :param speed: a list of speed
    :return breakpoint:a list of start point & end point of the acceleration [start,end,start,end,start,end]
    :return number : the count of the acceleration
    """
    breakpoint = []
    start = 0
    number = 0
    for i in range(len(speed) - 1):
        diff = speed[i + 1] - speed[i]
        if diff > 3 and start == 0 and diff < 9:         # acceleration exceeds 3m per second
            breakpoint.append(i)
            start = 1
        if diff < 2 and start == 1:

            time_diff = time[i] - time[breakpoint[-1]]   # acceleration time interval

            if time_diff > 2:
                breakpoint.append(i)
                start = 0
                number += 1
            else:
                del breakpoint[-1]
                start = 0
                continue
    if len(breakpoint) % 2 != 0 or len(breakpoint) == 1:
        del breakpoint[-1]
    return breakpoint, number


def find_dic_ACC(data):
    """ Find the acceleration in every task and store to a new dict that including a list of acceleration
        start & end point and the count of acceleration

    :param data: a dict of data
    :return dict_acc: a dict of acceleration list & the count of acceleration
            key : task id
            value : an array including a list of acceleration start & end point and the count of acceleration
            [breakpoint, number]
    :return total_number: a count of acceleration in the data, int
    """
    dict_acc = {}
    total_number = 0
    for key, value in data.items():
        bp, number = find_ACC(value[2], value[4])
        total_number += number
        dict_acc[key] = [bp, number]
    return dict_acc, total_number


def find_hardbrake(speed, time):
    """Use speed to find the hard brake maneuver, the speed decrease exceeds 5m/s

    :param speed: a list of speed
    :param time: a list of timestamp
    :return breakpoint:a list of the hardbrake
    :return number : the count of the hardbrake
    """
    breakpoint = []
    number = 0
    td = 0
    for i in range(len(speed) - 1):
        t = time[i + 1] - time[i]
        if t == 0: t = 1
        diff = (speed[i] - speed[i + 1]) / t

        if diff > 5 and diff < 8:
            breakpoint.append(i)
            number += 1
    return breakpoint, number


def find_dic_HB(data):
    """ Find the hardbrake in every task and store to a new dict that including a list of hardbrake points
        and the count of hardbrake

    :param data: a dict of data
    :return dict_hb: a dict of hardbrake list & the count of hardbrake
            key : task id
            value : an array including a list of hardbrake and the count of hardbrake
            [breakpoint, number]
    :return total_number: a count of hardbrake in the data, int
    """
    dict_hb = {}
    total_number = 0
    for key, value in data.items():
        breakpoint, number = find_hardbrake(value[2], value[4])
        if len(breakpoint) > 0:
            if breakpoint[0] == 0:
                del breakpoint[0]
                number -= 1
        total_number += number

        dict_hb[key] = [breakpoint, number]
    return dict_hb, total_number


def total_time(data):
    """Calculate the total task time in data

    :param data: the dict of data
    :return: the total task duration, unit second
    """
    t_time = 0
    for key, value in data.items():
        if len(value[4]) > 1:
            t_time += value[4][-1] - value[4][0]
    return t_time


def total_distance(data):
    """Calculate the total distance in data

    :param data: the dict of data
    :return: the total distance
    """
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    t_distance = 0
    for key, value in data.items():
        start_point = [value[0][0], value[1][0]]
        end_point = [value[0][-1], value[1][-1]]
        direction_result = gmap.directions(start_point, end_point, mode="driving")
        if direction_result != []:
            string = direction_result[0]['legs'][0]['distance']['text']
            sp = float(string.split()[0])
            t_distance += sp
    return t_distance


def over_speed_limit(lat, long, speed, time):
    """Calculate the speeding duration & Speeding ration

    :param lat: a list of latitude
    :param long: a list of longitude
    :param speed: a list of speed
    :param time: a list of time
    :return over_time: the count of location point speeding
    :return overspeed: the sum of speeding ration, float
    :return duration: Speeding duration (second)
    """
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    over_time = 0
    overspeed = 0
    temp = 0
    duration = 0
    ovsp_start = False
    sL = float('Inf')
    j = 0

    speedlimit_list, call_api = speedlimit.path_speed_limit(lat, long, speed)
    if len(speedlimit_list) > 0:
        for i in range(len(speed)-1):
            if i > call_api[j]:
                if j<len(call_api)-1:
                    j += 1
                else:
                    j = len(call_api)-1

            if j > len(speedlimit_list)-1:
                j = len(speedlimit_list)-1

            sL = speedlimit_list[j]

            if sL < speed[i] and speed[i + 1] > sL and ovsp_start == False:
                start_time = time[i]
                over_time += 1
                overspeed +=  (speed[i] - sL) /sL
                ovsp_start = True
            elif sL > speed[i] and ovsp_start == True:
                end_time = time[i]
                duration += end_time - start_time
                ovsp_start = False

    return over_time, overspeed, duration


def find_dic_over(data):
    """Find the speeding duration & ratio & the count of speeding location points

    :param data:the dict of data
    :return dict_ov: a dict of [overspeed, over_time, duration]
                key: task is
                value : an array including [overspeed, over_time, duration]
    :return total_duration: the total time speeding
    :return total_overspeed: the total of speeding ratio
    :return total_times: the total count of the speeding location points
    """
    dict_ov = {}
    total_duration = 0
    total_overspeed = 0
    total_times = 0
    for key, value in data.items():
        over_time, overspeed, duration = over_speed_limit(value[0], value[1], value[2], value[4])
        total_duration += duration
        total_overspeed += overspeed
        total_times += over_time
        dict_ov[key] = [overspeed, over_time, duration]
    return dict_ov, total_duration, total_overspeed, total_times


def open_file(filename):
    """Read the json file to the dict data

    :param filename: the filename you want to read
    :return: the dict of data
    """
    with open(filename + '.json') as json_file:
        data = json.load(json_file)

    return data


def get_info(data):
    """Calculate the Speeding & turning & Hard brake & Acceleration

    :param data: the dict of data
    :return:
    """
    dict_turning, turning_number = find_dic_turning(data)
    print("Turing detect finished---------------------------------------------")
    dict_hb, hb_number = find_dic_HB(data)
    print("Hard brake detect finished-----------------------------------------")
    dict_acc, acc_number = find_dic_ACC(data)
    print("Acceleration detect finished---------------------------------------")
    dict_ov, ov_duration, total_ov, total_times = find_dic_over(data)
    print("Speeding detect finished-------------------------------------------")
    return dict_turning, turning_number, dict_hb, hb_number, dict_acc, acc_number, ov_duration, total_ov, total_times

def store_database(turning_speed, hb_number, acc_number, ov_duration, total_ov, time, agent_id, fast_turn, total_times):
    df = pd.DataFrame([{
        '2fast turn number' : fast_turn,
        '3turning_speed' : turning_speed,
        '9time': time,
        '4hb_number': hb_number,
        '5acc_number':acc_number,
        '7ov_duration': ov_duration,
        '8speeding times': total_times,
        '6Average over speed': total_ov,
        '1Agent_id': agent_id,
    }])

    df.to_csv("Maneuver detect/Population data/population_new.csv", mode='a', index = False, header=False)

def generate_population(data, agent_id):
    """Generate the population data and store into population database
        data must be the single agent data

    :param data: the dict of data
    :param agent_id: agent id number
    """
    if data != {}:
        fast_turn = 0
        aver_speed = 0
        speed_number = 0

        dict_turning, turning_number, dict_hb, hb_number, dict_acc, acc_number, ov_duration, total_ov, total_times = get_info(
            data)
        time = total_time(data)


        for key, value in dict_turning.items():
            a_speed = calculate_average_speed(data, key, dict_turning[key][0], dict_turning[key][1])
            fast_turn = count_fast_turn(data, key, dict_turning[key][0])
            if a_speed < 100:
                aver_speed += a_speed
                speed_number += 1
        if speed_number == 0:
            turning_speed = 0
        else:
            turning_speed = aver_speed / speed_number
        store_database(turning_speed, hb_number, acc_number, ov_duration, total_ov, time, agent_id, fast_turn, total_times)

def describe(dict_turning, data):
    aver_speed = []
    for key, value in dict_turning.items():
        a_speed = calculate_average_speed(data, key, dict_turning[key][0], dict_turning[key][1])
        if a_speed < 100:
            aver_speed.append(a_speed)

    df = pd.DataFrame({
        'Turning speed': aver_speed
    })

    mean = float(df.mean()[0])
    std = float(df.std()[0])
    count = int(df.count()[0])
    min, max = float(df.min()[0]), float(df.max()[0])
    twfive, sevfive, half = float(df.quantile(0.25)[0]), float(df.quantile(0.75)[0]), float(df.quantile(0.5)[0])

    print("mean = ", mean)
    print("std = ", std)
    print("count = ", count)
    print("min = ", min, "max =", max)
    print("25% = ", twfive, "50% = ", half, "75% = ", sevfive)

    return mean, std, count, min, max, twfive, half, sevfive


def main():
    filename = input('Input filename: ')
    data = open_file(str(filename))
    print("Load data finished-------------------------------------------------")
    data_ogn = organize_data(data)
    print("Ticket number:", len(data_ogn))
    print("Organize data finished---------------------------------------------")
    dict_turning, turning_number, dict_hb, hb_number, dict_acc, acc_number, ov_duration, total_ov, total_times = get_info(data_ogn)
    time = total_time(data_ogn)
    #distance = total_distance(data_ogn)
    print("HB:", hb_number)
    print("ACC:", acc_number)
    print("Turning:", turning_number)
    print("Speeding:", ov_duration)
    print("Time:", time)
    print('total_times', total_times)
    print('ratio', total_ov/total_times)
    #print("Distance", distance)

    store_sp = input('Do you want to store the data to population database?(y/n)')
    if (str(store_sp) == 'y'):
        #store_speed(dict_turning, data_ogn)
        store_hb(hb_number, time)
        store_ACC(acc_number, time)
        store_ov(total_ov, ov_duration, time)

    print("Describe turning speed:")
    mean, std, count, min, max, twfive, half, sevfive = describe(dict_turning, data_ogn)

    agent_filename = input('Do you want to save the single agent describe if yes input the filename: ')

    '''if (str(filename) != "n"):

        agent_info = {'Number': [len(data_ogn), time, distance, hb_number, acc_number, ov_duration, total_ov,
                                 turning_number, mean, std]}

        df = pd.DataFrame(agent_info, index=["Ticket", 'Driving Time', 'Driving Distance', 'Hard brake', 'ACC',
                                             'Speeding time', 'Speeding value', 'Turning number', 'Turning speed mean',
                                             'Turning speed std'])
        agent_filename = 'Maneuver detect/Single agent data/' + agent_filename
        df.to_csv(agent_filename + ".csv", index=True)'''


if __name__ == "__main__":
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    main()
