import googlemaps
from datetime import datetime
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import mpu
import csv
import os

def smooth(speed, box_pts):
    box = np.ones(box_pts)/box_pts
    speed_smooth = np.convolve(speed, box, mode='same')
    return speed_smooth

def calculate_speed_google(lat, long, time):
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    speed = []
    speed.append(0)
    for i in range(len(lat)-1):
        t = time[i+1] - time[i]
        start_point = [lat[i],long[i]]
        end_point = [lat[i+1],long[i+1]]
        direction_result = gmap.directions(start_point, end_point, mode = "driving")
        string = direction_result[0]['legs'][0]['distance']['text']
        sp = float(string.split()[0])*0.3048/t
        speed.append(sp)
    speed[0] = speed[1]
    return speed


def RMSE(speed_cal, speed):
    total = 0
    error_total = []
    for i in range(len(speed_cal)):
        total += abs(speed[i] - speed_cal[i])
        error_total.append(speed[i] - speed_cal[i])
        error = total / len(speed_cal)

    return error


def calculate_speed_cal(lat, long, time):
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

def google_speed(lat1,lon1,lat2,lon2,time):
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    start_point = [lat1,lon1]
    end_point = [lat2,lon2]
    direction_result = gmap.directions(start_point, end_point, mode = "driving")
    string = direction_result[0]['legs'][0]['distance']['text']
    sp = float(string.split()[0])*0.3048/time
    return sp

def cal_speed(lat1,lon1,lat2,lon2,time):
    dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2))*1000
    res = dist/time
    return res


def fill_speed(speed, time, lat, long):
    speed_revise_number = 0
    no_smooth = 0
    for i in range(len(speed) - 1):
        if speed[i] == None:
            speed_revise_number += 1
            t = time[i + 1] - time[i]
            if t == 0: t = 1
            res = cal_speed(lat[i], long[i], lat[i + 1], long[i + 1], t)
            if res < 0.1: res = 0
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
    headnone = False
    if heading[0] == None:
        headnone= True
    for i in range(len(heading)-1):
        if headnone == True:
            if heading[i] != None:
                heading[0:i] = [heading[i]]*i
                headnone = False
        else:
            if heading[i] == None:
                if heading[i+1] == None :
                    heading[i] = heading[i-1]
                else:
                    heading[i] = (heading[i-1]+heading[i+1])/2
    if heading[-1] == None:
        heading[-1] = heading[-2]
    return heading


def organize_data(data):
    delkey = []
    for key, value in data.items():
        if len(value[0]) < 20:
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
    breakpoint = []
    start = 0
    number = 0
    for i in range(len(heading)-2):
        diff = abs(heading[i+1]-heading[i])
        if diff > 19 and diff < 70 and start == 0:
            if i-2<0 :
                breakpoint.append(0)
            else:
                breakpoint.append(i - 2)
            start = 1
        if diff < 5 and start == 1:

            angle_diff = abs(heading[i+1] - heading[breakpoint[-1]])

            if (angle_diff < 30 or angle_diff >150) :
                del breakpoint[-1]
                start = 0
                continue
            else:
                breakpoint.append(i+2)
                start = 0
                number+=1
    if len(breakpoint) %2 != 0:
        del breakpoint[-1]
    return breakpoint, number

def find_dic_turning(data):
    dict_turning={}
    total_number = 0
    for key,value in data.items():
        breakpoint, number = find_turning(value[3])
        total_number += number
        if len(breakpoint) != 0:
            dict_turning[key] = [breakpoint,number]
    return dict_turning,total_number

def calculate_average_speed(data, key, turning_list,number_turning):
    total_speed = 0
    for i in range(0, len(turning_list), 2):
        total_speed += np.mean(data[key][2][turning_list[i]:turning_list[i+1]])
    average_speed = total_speed/number_turning
    return average_speed


def store_speed(dict_turning, data):
    if not os.path.isfile('total_speed.csv'):
        acs = []
        df = pd.DataFrame({
            'Turning speed': acs
        })
        df.to_csv("total_speed.csv", index=False)

    speed_data = pd.read_csv('total_speed.csv')
    aver_speed = speed_data["Turning speed"].tolist()

    #ticket = []

    for key, value in dict_turning.items():
        a_speed = calculate_average_speed(data, key, dict_turning[key][0], dict_turning[key][1])
        if a_speed < 100:
            #ticket.append(key)
            aver_speed.append(a_speed)

    df = pd.DataFrame({  # 'ticket_id': ticket,
        'Turning speed': aver_speed
    })

    df.to_csv("total_speed.csv", index=False)

def find_ACC(speed, time):
    breakpoint = []
    start = 0
    number = 0
    for i in range(len(speed)-1):
        diff = speed[i+1]-speed[i]
        if diff > 3 and start == 0 and diff<9:

            breakpoint.append(i)
            start = 1
        if diff < 2 and start == 1:

            time_diff = time[i] - time[breakpoint[-1]]

            if time_diff>2:
                breakpoint.append(i)
                start = 0
                number+=1
            else:
                del breakpoint[-1]
                start = 0
                continue
    if len(breakpoint) %2 != 0 or len(breakpoint)== 1:
        del breakpoint[-1]
    return breakpoint, number

def find_dic_ACC(data):
    dict_turning={}
    total_number = 0
    for key,value in data.items():
        breakpoint, number = find_ACC(value[2], value[4])
        total_number += number
        dict_turning[key] = [breakpoint,number]
    return dict_turning,total_number


def find_hardbrake(speed, time):
    breakpoint = []
    number = 0
    td = 0
    for i in range(len(speed) - 1):
        t = time[i + 1] - time[i]
        if t == 0: t = 1
        diff = (speed[i] - speed[i + 1]) / t

        if diff > 5 and diff < 8:
            breakpoint.append(i)
            #td += diff
            number += 1
    return breakpoint, number#, td

def find_dic_HB(data):
    dict_hb={}
    total_number = 0
    tdd = 0
    for key,value in data.items():
        breakpoint, number = find_hardbrake(value[2], value[4])
        if len(breakpoint)>0:
            if breakpoint[0] == 0:
                del breakpoint[0]
                number-=1
        total_number += number
        #tdd += td
        dict_hb[key] = [breakpoint,number]
    return dict_hb, total_number#, tdd/total_number

def total_time(data):
    t_time = 0
    for key,value in data.items():
        if len(value[4])>1:
            t_time += value[4][-1] - value[4][0]
    return t_time

def total_distance(data):
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    t_distance = 0
    for key,value in data.items():
        start_point = [value[0][0],value[1][0]]
        end_point = [value[0][-1],value[1][-1]]
        direction_result = gmap.directions(start_point, end_point, mode = "driving")
        string = direction_result[0]['legs'][0]['distance']['text']
        sp = float(string.split()[0])
        t_distance += sp
    return t_distance


def over_speed_limit(lat, long, speed):
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    over_time = 0
    overspeed = []
    temp = 0

    for i in range(len(speed)):
        if (abs(speed[i] - temp) > 15) and speed[i] < 130 and speed[i] > 25:
            temp = speed[i]
            results = gmap.snapped_speed_limits((lat[i], long[i]))
            if results != {}:
                speed_limit = gmap.speed_limits(results["snappedPoints"][0]["placeId"])

                sL = speed_limit[0]['speedLimit']
                if sL < speed[i] and speed[i + 1] > sL:
                    over_time += 1
                    overspeed.append(speed[i] - sL)

    return over_time, overspeed


def find_dic_over(data):
    dict_ov = {}
    total_number = 0
    for key, value in data.items():
        over_time, overspeed = over_speed_limit(value[0], value[1], value[2])
        total_number += over_time
        dict_ov[key] = [overspeed, over_time]

    return dict_ov, total_number

def open_file(filename):
    with open(filename + '.json') as json_file:
        data = json.load(json_file)

    return data

def get_info(data):
    dict_turning, turning_number = find_dic_turning(data)
    dict_hb, hb_number = find_dic_HB(data)
    dict_acc, acc_number = find_dic_ACC(data)

    return dict_turning, turning_number, dict_hb, hb_number, dict_acc, acc_number

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
    print("min = ", min,  "max =", max)
    print("25% = ", twfive, "50% = ", half, "75% = ", sevfive )

    filename = input('Do you want to save the describe if yes input the filename: ')

    if (str(filename) != "n"):
        df.describe().to_csv(filename + ".csv", index=True)

    return mean, std, count, min, max, twfive, half, sevfive

def main():
    filename = input('Input filename: ')
    data = open_file(str(filename))
    print("Load data finished-------------------------------------------------")
    data_ogn = organize_data(data)
    print("Ticket number:", len(data_ogn))
    print("Organize data finished---------------------------------------------")
    dict_turning, turning_number, dict_hb, hb_number, dict_acc, acc_number = get_info(data_ogn)
    #time = total_time(data)
    #distance = total_distance(data)
    print("HB:", hb_number)
    print("ACC:", acc_number)
    print("Turning:", turning_number)
    #print("Time:", time)
    #print("Distance", distance)

    store_sp = input('Do you want to store the turning speed data?(y/n)')
    if (str(store_sp) == 'y'):
        store_speed(dict_turning, data)

    print("Describe turning speed:")
    mean, std, count, min, max, twfive, half, sevfive = describe(dict_turning, data)

if __name__ == "__main__":
    gmap = googlemaps.Client(key='AIzaSyC2vamy14qg0cvysoTg0w7A8Pj4Lzxn_aw')
    main()