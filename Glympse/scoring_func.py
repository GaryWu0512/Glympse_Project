# latest version of scoring
# Rev 5 6/7/19

import numpy as np
import pandas as pd
import csv
import datetime

import matplotlib.pyplot as plt

# minimum drive time for a score is set to 10 hrs
MIN_TIME = 36000

# Returns the safety score for the given stats
#
# value: count of the maneuver to be scored
# mu: the mean of the maneuver in the sample population
# std: the standard deviation of the maneuver in the sample population
def score_one(value, mu, std):
    z = (float(value) - mu)/std
    if z >= 2:
        score = 1
    elif z < 2 and z >= 1:
        score = 2
    elif z < 1 and z >= 0:
        score = 3
    elif z < 0 and z >= -1:
        score = 4
    else:
        score = 5
    return score

def score_all(counts):
    mu = np.mean(counts)
    std = np.std(counts)
    score_array = np.array([])

    for value in counts:
        z = (float(value) - mu)/std
        if z >= 2:
            score = 1
        elif z < 2 and z >= 1:
            score = 2
        elif z < 1 and z >= 0:
            score = 3
        elif z < 0 and z >= -1:
            score = 4
        else:
            score = 5
        score_array = np.append(score_array, score)
    return score_array

# Returns to total weighted safety score for an agent
#
# hard_brake: total hard brake count/total drive time
# acceleration: total acceleration count/ total drive time
# turning: total fast turn count/total drive time
# speeding: % over speed limit*time over speed limit/total drive time
def weight_score(hard_brake, acceleration, turning, speeding):
    tot_score = .15*acceleration + .30*hard_brake + .15*turning + .40*speeding
    return tot_score

# Returns the mean and standard deviation for each maneuver from the samples population
#
# sample_pop_file: filename of the sample population
# example sample_pop_file: population_new.csv
def get_stats(sample_pop_file):
    agents = []
    hb = []
    acc = []
    speeding_avg = []
    speeding_count = []
    speeding_duration = []
    fast_turn = []
    mu = []
    std = []
    times = []
    with open(sample_pop_file) as pop_data:
        reader = csv.DictReader(pop_data, delimiter=',')
        for row in reader:
            agents.append(row['1Agent_id'])
            fast_turn.append(row['2fast turn number'])
            hb.append(row['4hb_number'])
            acc.append(row['5acc_number'])
            speeding_avg.append(row['6Average over speed'])
            speeding_count.append(row['8speeding times'])
            speeding_duration.append(row['7ov_duration'])
            times.append(row['9time'])

    hb = average_counts(hb,times)
    mu.append(np.mean(hb))
    std.append(np.std(hb))

    acc = average_counts(acc,times)
    mu.append(np.mean(acc))
    std.append(np.std(acc))

    turning = average_counts(fast_turn, times)
    mu.append(np.mean(turning))
    std.append(np.std(turning))

    speeding_avg = np.array(speeding_avg,dtype=np.float32)
    speeding_duration = np.array(speeding_duration,dtype=np.float32)
    speeding = average_counts(speeding_avg*speeding_duration,times)
    mu.append(np.mean(speeding))
    std.append(np.std(speeding))

    return mu, std


def average_counts(maneuver, time):
    maneuver = np.array(maneuver,dtype=np.float32)
    time = np.array(time,dtype=np.float32)
    avg = np.divide(maneuver,time)
    return avg

# Returns:
# scores: an array of scores for each maneuver and the weighted score
# scores = [hard brake, acceleration, turning, average % over speed, speeding time, weighted score]
# stats: the stats for each maneuver and total drive time
# stats = [hb count, acc count, turning count, speeding count, time]
# Raises an exception if agent to be scored total drive time is less than the
# set minimum requirement MIN_TIME
#
# maneuver_filename: filename and/or path from Maneuver detecting
# sample_pop_file: filename of the sample population
# example filename: 'Maneuver detect/Single agent data/test.csv'
# example sample_pop_file: population_new.csv
def get_scores(maneuver_filename, sample_pop_file):
    scores = []
    stats = []
    mu, std = get_stats(sample_pop_file)
    with open(sample_pop_file) as pop_data:
        reader = csv.DictReader(pop_data, delimiter=',')
        for row in reader:
            stats.append(float(row['2fast turn number']))
            stats.append(float(row['4hb_number']))
            stats.append(float(row['5acc_number']))
            stats.append(float(row['6Average over speed']))
            stats.append(float(row['8speeding times']))
            stats.append(float(row['7ov_duration']))
            time = float(row['9time'])
            stats.append(time)

    if float(time) < MIN_TIME:
        raise Exception('total drive time should not be less than MIN_TIME. Total drive time was: {}'.format(time))

    hb = float(hb)/float(time)
    scores.append(score_one(hb,mu[0],std[0]))
    acc = float(acc)/float(time)
    scores.append(score_one(acc,mu[1],std[1]))
    turning = float(turning)/float(time)
    scores.append(score_one(turning,mu[2],std[2]))
    speeding = (float(speeding)*float(speeding_time))/float(time)
    scores.append(score_one(speeding,mu[3],std[3]))

    total_score = weight_score(scores[0], scores[1], scores[2], scores[3])
    scores.append(total_score)

    return scores, stats

# Same as get_scores(manever_filename) except it takes an agent from the sample population
# Used to get an accurate sample score
# Returns:
# scores: an array of scores for each maneuver and the weighted score
# scores = [hard brake, acceleration, turning, average % over speed, speeding time, weighted score]
# stats: the stats for each maneuver and total drive time
# stats = [hb count, acc count, turning count, speeding count, time]
# Raises an exception if agent to be scored total drive time is less than the
# set minimum requirement MIN_TIME
#
# agent_id: agent_id from sample pop to be scored
# sample_pop_file: filename of the sample population
# example agent_id: 523922 example sample_pop_file: population_new.csv
def get_scores_example(agent_id, sample_pop_file):
    agents = []
    hb = []
    acc = []
    speeding_avg = []
    speeding_count = []
    speeding_duration = []
    fast_turn = []
    mu = []
    std = []
    times = []
    with open(sample_pop_file) as pop_data:
        reader = csv.DictReader(pop_data, delimiter=',')
        for row in reader:
            agents.append(row['1Agent_id'])
            fast_turn.append(row['2fast turn number'])
            hb.append(row['4hb_number'])
            acc.append(row['5acc_number'])
            speeding_avg.append(row['6Average over speed'])
            speeding_count.append(row['8speeding times'])
            speeding_duration.append(row['7ov_duration'])
            times.append(row['9time'])

    index = agents.index(agent_id)
    scores = []
    stats = []
    mu, std = get_stats(sample_pop_file)

    stats.append(float(hb[index]))
    stats.append(float(acc[index]))
    stats.append(float(fast_turn[index]))
    stats.append(float(speeding_avg[index]))
    stats.append(float(speeding_duration[index]))
    time = float(times[index])
    stats.append(time)

    if float(time) < MIN_TIME:
        raise Exception('total drive time should not be less than MIN_TIME. Total drive time was: {}'.format(time))

    hb = stats[0]/time
    scores.append(score_one(hb,mu[0],std[0]))
    acc = stats[1]/time
    scores.append(score_one(acc,mu[1],std[1]))
    turning = stats[2]/time
    scores.append(score_one(turning,mu[2],std[2]))
    speeding = (stats[3]*stats[4]/time)
    scores.append(score_one(speeding,mu[3],std[3]))

    total_score = weight_score(scores[0], scores[1], scores[2], scores[3])
    scores.append(total_score)
    return scores, stats

def get_scores_all(sample_pop_file):
    agents = []
    hb = []
    acc = []
    speeding_avg = []
    speeding_count = []
    speeding_duration = []
    fast_turn = []
    times = []
    with open(sample_pop_file) as pop_data:
        reader = csv.DictReader(pop_data, delimiter=',')
        for row in reader:
            agents.append(row['1Agent_id'])
            fast_turn.append(row['2fast turn number'])
            hb.append(row['4hb_number'])
            acc.append(row['5acc_number'])
            speeding_avg.append(row['6Average over speed'])
            speeding_count.append(row['8speeding times'])
            speeding_duration.append(row['7ov_duration'])
            times.append(row['9time'])

    hb = average_counts(hb,times)
    hb_scores = score_all(hb)
    acc = average_counts(acc,times)
    acc_scores = score_all(acc)
    fast_turn = average_counts(fast_turn,times)
    fast_turn_scores= score_all(fast_turn)
    speeding_avg = np.array(speeding_avg,dtype=np.float32)
    speeding_duration = np.array(speeding_duration,dtype=np.float32)
    speeding = average_counts(speeding_avg*speeding_duration,times)
    speeding_scores = score_all(speeding)

    tot_scores = weight_score(hb_scores,acc_scores,fast_turn_scores,speeding_scores)

    return tot_scores


# testing
def plot_one(counts, scores):
    plt.subplot(2,1,1)
    plt.hist(counts)
    plt.title('counts histogram')
    plt.subplot(2,1,2)
    plt.hist(scores)
    plt.title('scores histogram')
    plt.show()

def plot_all(hb, hb_scores, acc, acc_scores, fast_turn, fast_turn_scores, speeding, speeding_scores, tot_scores):
    # hard braking
    plt.subplot(5,2,1)
    plt.hist(hb)
    plt.title('hard brake histogram')
    plt.subplot(5,2,2)
    plt.hist(hb_scores)
    plt.title('hard brake scores histogram')
    plt.subplot(5,2,3)
    plt.hist(acc)
    plt.title('acceleration histogram')
    plt.subplot(5,2,4)
    plt.hist(acc_scores)
    plt.title('acceleration scores histogram')
    plt.subplot(5,2,5)
    plt.hist(fast_turn)
    plt.title('fast turn histogram')
    plt.subplot(5,2,6)
    plt.hist(fast_turn_scores)
    plt.title('fast turn scores histogram')
    plt.subplot(5,2,7)
    plt.hist(speeding)
    plt.title('speeding histogram')
    plt.subplot(5,2,8)
    plt.hist(speeding_scores)
    plt.title('speeding scores histogram')
    plt.subplot(5,2,9)
    plt.hist(tot_scores)
    plt.title('weighted scores histogram')
    plt.show()



# filters sample population by max_time and stores a new filtered sample population
def screen_population(sample_pop_file, filter_pop_file):
    flag = True
    with open(sample_pop_file) as pop_data:
        reader = csv.DictReader(pop_data, delimiter=',')
        for row in reader:
            agent = row['1Agent_id']
            fast_turn = row['2fast turn number']
            turning_speed = row['3turning_speed']
            hb = row['4hb_number']
            acc = row['5acc_number']
            speeding_avg = row['6Average over speed']
            speeding_duration = row['7ov_duration']
            speeding_count = row['8speeding times']
            time = row['9time']

            time_check = time
            if float(time_check) > MIN_TIME:
                df = pd.DataFrame([{
                    '1Agent_id': agent,
                    '2fast turn number': fast_turn,
                    '3turning_speed': turning_speed,
                    '4hb_number': hb,
                    '5acc_number': acc,
                    '6Average over speed': speeding_avg,
                    '7ov_duration': speeding_duration,
                    '8speeding times': speeding_count,
                    '9time': time
                }])
                df.to_csv(filter_pop_file, mode='a', index=False, header=flag)
                flag = False


# Prints a report of the driver's scores
#
# scores = [hard brake, acceleration, turning, average % over speed, speeding time, weighted score]
def report(scores):
    print("Scored out of 5 where 5 is the safest and 1 is the least safe")
    print("\nOverall driver safety score out of 5: ", scores[4])
    print("\nScoring break down by maneuver:")
    print("--------------------------------")
    print("Hard braking score:             ", scores[0])
    print("Fast acceleration score:        ", scores[1])
    print("Fast turning score:             ", scores[2])
    print("Speeding score:                 ", scores[3])

# Prints a report of the driver's scores and their driving stats
#
# scores: score array from get_scores or get_scores_example
# scores = [hard brake, acceleration, turning, average % over speed, speeding time, weighted score]
# stats: stats array from get_scores or get_scores_example
# stats = [hb count, acc count, turning count, speeding count, time]
def detailed_report(scores, stats):
    time = datetime.timedelta(seconds=stats[5])
    report(scores)
    print("\nDriver statistics:")
    print("--------------------------------")
    print("Total hard brake count:        ", stats[0])
    print("Total fast acceleration count: ", stats[1])
    print("Total fast turning count:      ", stats[2])
    print("Average % over speed:          ", stats[3])
    print("Total time speeding:           ", datetime.timedelta(seconds= stats[4]))
    print("Total drive time:              ", time)


def main():
    scores, stats= get_scores_example('525470', 'filtered_population.csv')
    detailed_report(scores, stats)

    get_scores_all('filtered_population.csv')

    #get_scores('Maneuver detect/Single agent data/test.csv', 'population_new.csv')

if __name__ == "__main__":
    main()
