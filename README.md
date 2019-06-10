## Overview

- [MongoDB Connection](#MongoDB_Connection)
- [Query](#Query)
- [Data Preprocessed](#Data_Preprocessed)
- [Maneuver Detection](#Maneuver_Detection)
- [Scoring](#Scoring)

## System Requirements
- Python 3 or later.
- A Google Maps API key.
- Python Package (pymongo, [googlemaps](https://github.com/googlemaps/google-maps-services-python), [mpu](https://github.com/MartinThoma/mpu), numpy, pandas, json)

## Installation

- pymongo
``` python -m pip install pymongo```
- googlemaps
```pip install -U googlemaps```
- mpu ```pip install git+https://github.com/MartinThoma/mpu.git```

## MongoDB_Connection

### Class MongoClient:

- This is a class object including three methods 

- ReadPreference :secondary

<<<<<<< HEAD
####\_get\_mongo\_client(self, database):
=======
#### _get_mongo_client(self, database):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Generate the single Client (readPreference :secondary) 

:param database: The database that the we want to generate client
:type database: a sigle databases, where a databases is a string
:rtype: Single client
```

<<<<<<< HEAD
####\_get\_mongo\_client\_dict(self, list\_of\_databases):
=======
#### _get_mongo_client_dict(self, list_of_databases):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Generate a dict of Client

:param list_of_databases: The database that the we want to generate client
:type list_of_databases: a list of databases, where a databases is a string
:rtype: a dict of client
         Key: database name (string)
         Value: client
```

<<<<<<< HEAD
####get\_client(self, database_name):
=======
#### get_client(self, database_name):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Take the client of a specific database from client dict

:param database_name: The database that the we want to get client
:type database_name: single database name, where a databases is a string
:rtype: Single client
```

## Query

### Class Query:

- This is a class object to query the data in MongoDB

- User can query data by hierarchy org_id, agent_id, task_id

- Output the query result to json file


<<<<<<< HEAD
####query\_orgid(self, hierarchy):
=======
#### query_orgid(self, hierarchy):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find all relevant org_ids based on a specific hierarchy

:param hierarchy: The hierarchy number that we want to  get relevant org_ids
:type hierarchy: a single hierarchy number, where a  hierarchy number is a integer
:rtype: a list of org_id, which have the same hierarchy number
```
<<<<<<< HEAD
####query\_agents(self, org\_id):
=======
#### query_agents(self, org_id):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find the all agent id with the same org_id

:param org_id: The org_id that we want to get agent_id
:type org_id: a single org_id number, where a  org_id number is a integer
:rtype: a list of agent_id, which with the same org_id
```


<<<<<<< HEAD
####query\_tasks(self, agent_id):
=======
#### query_tasks(self, agent_id):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find all the tasks id done by a particular agent
if agent did not do any task it will return None, and print out empty

:param agent_id: The agent_id that we want to look for
:type agent_id: a list of agent_id, where a agent_id is a integer
:rtype: a dict of task_id
          Key: agent_id (int)
          Value: a list of tasks
```

<<<<<<< HEAD
####find\_locationpoints(self, task_id):
=======
#### find_locationpoints(self, task_id):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find all the location_point string according to each task_id

:param task_id: The task that we want to look for
:type task_id: a list of task_id, where a task_id is a integer
:rtype: a dict of location point string
          Key: task_id (int)
          Value: a list of location point
```

<<<<<<< HEAD
####to\_json(self, location_dict, filename):
=======
#### to_json(self, location_dict, filename):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Output the location_dict to the json file

:param location_dict: The dict of the location point according to the task id
:param filename: The filename user want to ouput, where the filename is a String
:return: dict_one_agent: a dict of location point info
                            Key: task_id (int)
                            Value: an array including [latitude, longitude, speed, angle, time]
```

## Data_Preprocessed

- In the Maneuver_detect.py, there are some public function relate to the data processing

- User can select single function to finish specific purpose, or use organize_data automatically complete all data processing

#### smooth(speed, box_pts):
```
Smooth the speed data

:param speed: a list of data that you want to smooth
:type speed: list
:param box_pts: the number of box points
:type box_pts: int
:return: a list of data after smooth
```

<<<<<<< HEAD
####google\_speed(lat1, lon1, lat2, lon2, time):
=======
### google_speed(lat1, lon1, lat2, lon2, time):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Calculate the single speed between two points by using Google API

:param lat1: start point latitude
:param lon1: start point longitude
:param lat2: end point latitude
:param lon2: end point longitude
:param time: time interval (second)
:return: speed , float
```

<<<<<<< HEAD
####cal\_speed(lat1, lon1, lat2, lon2, time):
=======
#### cal_speed(lat1, lon1, lat2, lon2, time):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Calculate the single speed between two points by using mpu

:param lat1: start point latitude
:param lon1: start point longitude
:param lat2: end point latitude
:param lon2: end point longitude
:param time: time interval (second)
:return: speed , float
```

<<<<<<< HEAD
####fill\_speed(speed, time, lat, long):
=======
#### fill_speed(speed, time, lat, long):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Filling out the missing speed point, this function will check every point in given list
   if the speed = None or 0, I will recalculate the speed

:param speed: a list of speed
:param time: a list of timestamp
:param lat: a list of latitude
:param long: a list of longitude
:return: a list of speed after filling out
```

<<<<<<< HEAD
####fill\_heading(heading):
=======
#### fill_heading(heading):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Filling out the missing heading point, this function will check out every point in the given list
   if the heading = None, I will fill out the missing heading

:param heading: a list of heading angle
:return: a list of heading after filling out
```

<<<<<<< HEAD
####organize\_data(data):
=======
#### organize_data(data):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Organize the data, including filling out missing points & delete too short location points list
   & delete unuseful data

:param data: a dict of data
:return: a dict of data after processing
```

## Maneuver_Detection

<<<<<<< HEAD
####find\_dic_turning(data):
=======
#### find_dic_turning(data):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find the turning in every task and store to a new dict that including 
a list of turning start & end point and the count of turning

:param data: a dict of data
:return dict_turning: a dict of turning list & the count of turning
        key : task id
        value : an array including a list of turning start & end point and the count of turning
        [breakpoint, number]
:return total_number: a count of turning in the data, int
```
<<<<<<< HEAD
####count\_fast_turn(data, key, turning_list):
=======
#### count_fast_turn(data, key, turning_list):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Count the fast turn number

:param data: a dict of data
:param key: task id
:param turning_list: a list of turning start & end points
:return: the count of fast turn, int
```
<<<<<<< HEAD
####find\_dic_ACC(data):
=======
#### find_dic_ACC(data):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find the acceleration in every task and store to a new dict that including 
a list of acceleration start & end point and the count of acceleration

:param data: a dict of data
:return dict_acc: a dict of acceleration list & the count of acceleration
        key : task id
        value : an array including a list of acceleration start & end point and the count of acceleration
        [breakpoint, number]
:return total_number: a count of acceleration in the data, int
```

<<<<<<< HEAD
####find\_dic_HB(data):
=======
#### find_dic_HB(data):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find the hardbrake in every task and store to a new dict that including a list of hardbrake points
    and the count of hardbrake

:param data: a dict of data
:return dict_hb: a dict of hardbrake list & the count of hardbrake
        key : task id
        value : an array including a list of hardbrake and the count of hardbrake
        [breakpoint, number]
:return total_number: a count of hardbrake in the data, int
```

<<<<<<< HEAD
####total\_time(data):
=======
#### total_time(data):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Calculate the total task time in data

:param data: the dict of data
:return: the total task duration, unit second
```

<<<<<<< HEAD
####find\_dic_over(data):
=======
#### find_dic_over(data):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Find the speeding duration & ratio & the count of speeding location points

:param data:the dict of data
:return dict_ov: a dict of [overspeed, over_time, duration]
            key: task id
            value : an array including [overspeed, over_time, duration]
:return total_duration: the total time speeding
:return total_overspeed: the total of speeding ratio
:return total_times: the total count of the speeding location points
```

<<<<<<< HEAD
####get\_info(data):
=======
#### get_info(data):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Calculate the Speeding & turning & Hard brake & Acceleration

:param data: the dict of data
:return:
```

<<<<<<< HEAD
####generate\_population(data, agent_id):
=======
#### generate_population(data, agent_id):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
Generate the population data and store into population database
data must be the single agent data

:param data: the dict of data
:param agent_id: agent id number
```

## Scoring

- all scoring functions are contained in scoring_func.py

- scoring requires a sample population of detected maneuvers - population_new.csv is the example sample population

- Sample population must contain at least 100 agents

- Agents in the sample population should have minimum driver time of 10 hours

<<<<<<< HEAD
####get\_scores\_example(agent\_id, sample\_pop_file):
=======
#### get_scores_example(agent_id, sample_pop_file):
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a

```
scores an agent from the sample population against the sample population
```

<<<<<<< HEAD
####get\_scores(maneuver\_filename, sample\_pop\_file)
=======
#### get_scores(maneuver_filename, sample_pop_file)
>>>>>>> 6339c36db5f8431e1e75482f30129948a43ab70a
```
scores an agent from a separate file (must be csv) against the sample population
```
