import numpy as np
import matplotlib.pyplot as plt

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


def score_one(count, mu, std):
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

def weight_score(acceleration, hard_brake, turning, speeding):
    tot_score = .15*acceleration + .25*hard_brake + .45*turning + .15*speeding
    return tot_score
