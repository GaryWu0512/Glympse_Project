import pymongo
from pymongo import  MongoClient
import googlemaps
from datetime import datetime
import json



class MongoClient:

    def __init__(self, required_databases):
        """ Initialize the MongoClient

        :param required_databases: The database that the user wants to use
        :type required_databases: a list of databases, where a databases is a string
        :rtype: A dict of client, which the database name is the key

        """
        self.mongo_clients = self._get_mongo_client_dict(required_databases)

    def _get_mongo_client(self, database):
        """ Generate the single Client
             readPreference :secondary

        :param database: The database that the we want to generate client
        :type database: a sigle databases, where a databases is a string
        :rtype: Single client

        """
        # Fill these out!
        username = "your user name"
        password = "your password"
        hosts = ""

        uri = "mongodb://{}:{}@{}".format(username,
                                          password,
                                          hosts)
        return pymongo.MongoClient(uri, readPreference="secondary").get_database(database)

    def _get_mongo_client_dict(self, list_of_databases):
        """ Generate a dict of Client

        :param list_of_databases: The database that the we want to generate client
        :type list_of_databases: a list of databases, where a databases is a string
        :rtype: a dict of client
                 Key: database name (string)
                 Value: client
        """
        mongo_clients = {}
        for database in list_of_databases:
            mongo_clients[database] = self._get_mongo_client(database)

        return mongo_clients

    def get_client(self, database_name):
        """ Take the client of a specific database from client dict

        :param database_name: The database that the we want to get client
        :type database_name: single database name, where a databases is a string
        :rtype: Single client
        """
        client = self.mongo_clients[database_name]
        return client


class Query:
    def __init__(self, client):
        """ Initialize the Query

        :param client: The client that the user wants to query
        :type client: a sigle client, where a client is a client type
        :rtype: None

        """
        self.client = client

    def query_orgid(self, hierarchy):
        """ Find all relevant org_ids based on a specific hierarchy

        :param hierarchy: The hierarchy number that we want to  get relevant org_ids
        :type hierarchy: a single hierarchy number, where a  hierarchy number is a integer
        :rtype: a list of org_id, which have the same hierarchy number
        """

        list_of_orgs_ids = []
        query = {
            "hierarchy": hierarchy, "removed": {"$exists": False}
        }
        cursor = self.client["tracking.agents"].find(query)

        for org in cursor:
            if org["org_id"] in list_of_orgs_ids:
                continue
            else:
                list_of_orgs_ids.append(org["org_id"])
        return list_of_orgs_ids

    def query_agents(self, org_id):
        """ Find the all agent id with the same org_id

        :param org_id: The org_id that we want to get agent_id
        :type org_id: a single org_id number, where a  org_id number is a integer
        :rtype: a list of agent_id, which with the same org_id
        """
        list_of_agents_ids = []
        query = {
            "org_id": org_id, "removed": {"$exists": False}
        }
        cursor = self.client["tracking.agents"].find(query)

        for agent in cursor:
            list_of_agents_ids.append(agent["_id"])
        return list_of_agents_ids

    def query_tasks(self, agent_id):
        """ Find all the tasks id done by a particular agent
             if agent did not do any task it will return None, and print out empty

        :param agent_id: The agent_id that we want to look for
        :type agent_id: a list of agent_id, where a agent_id is a integer
        :rtype: a dict of task_id
                  Key: agent_id (int)
                  Value: a list of tasks
        """

        task_dict = {}
        list_of_tasks_ids = []

        query = {
            "agent_id": {"$in": agent_id}, "completed": {"$exists": True}
        }
        cursor = self.client["tracking.tasks"].find(query)
        for task in cursor:
            id = task["agent_id"]
            if id in task_dict:
                task_dict[id] += [task["_id"]]
            else:
                task_dict[id] = [task["_id"]]
        if task_dict != {}:
            return task_dict
        else:
            print("empty")
            return None

    def find_locationpoints(self, task_id):
        """ Find all the location_point string according to each task_id

        :param task_id: The task that we want to look for
        :type task_id: a list of task_id, where a task_id is a integer
        :rtype: a dict of location point string
                  Key: task_id (int)
                  Value: a list of location point
        """
        location_dict = {}
        location_point = []
        query = {
            "_id": {"$in": task_id}, "location_shared": {"$exists": True}
        }
        cursor = self.client["stats.tasks_full"].find(query)

        for task in cursor:
            id = task["_id"]
            location_point = []
            for i in range(len(task["ticket"]["location"])):
                location_point.append(task["ticket"]["location"][i])

            location_dict[id] = location_point

        return location_dict

    def speed_angle(self, location_dict, tid):
        """ Find a list of speed point and heading angle

        :param location_dict: the dict of the location point according to the task id
        :param tid: task id which the task we are looking for
        :type location_dict: a dict of location point
        :type tid: a number of the task id, where the task id is a integer
        :rtype speed: a list of speed
        :rtype heading: a list of heading angle
        """
        speed = []
        heading = []
        lat = []
        long = []
        for i in range(len(location_dict[tid])):
            speed.append(location_dict[tid][i][3])
            heading.append(location_dict[tid][i][4])
            lat.append(location_dict[tid][i][1])
            long.append(location_dict[tid][i][2])

        return speed, heading, lat, long

    def start_end(self, location_dict, tid):
        """ Find the start point and end point latitude & longitude

        :param location_dict: the dict of the location point according to the task id
        :param tid: task id which the task we are looking for
        :type location_dict: a dict of location point
        :type tid: a number of the task id, where the task id is a integer
        :rtype start_point: [latitude, longitude]
        :rtype end_point:  [latitude, longitude]
        """
        start_point = [location_dict[tid][0][1], location_dict[tid][0][2]]
        end_point = [location_dict[tid][len(location_dict[tid]) - 1][1],
                     location_dict[tid][len(location_dict[tid]) - 1][2]]

        return start_point, end_point

    def timestamp(self, location_dict, tid):
        """Find the list of the timestamp in specific ticket id
            & convert 13 digits to 10 digits

        :param location_dict: The dict of the location point according to the task id
        :param tid: task id which the task we are looking for
        :rtype: time_stamp: a list of timestamp
        """
        time_stamp = []
        for i in range(len(location_dict[tid])):
            time_stamp.append(location_dict[tid][i][0] // 1000)

        return time_stamp

    def convert_datetime(self, timestamp):
        """Convert the timestamp to human readable datetime

        :param timestamp: a list of timestamp
        :rtype: datetime: a list of datetime
        """
        datatime = []
        for i in range(len(timestamp)):
            dt_object = datetime.fromtimestamp(timestamp[i])
            datatime.append(dt_object)
        return datatime

    def to_json(self, location_dict, filename):
        """Output the location_dict to the json file

        :param location_dict: The dict of the location point according to the task id
        :param filename: The filename user want to ouput, where the filename is a String
        :return: dict_one_agent: a dict of location point info
                                    Key: task_id (int)
                                    Value: an array including [latitude, longitude, speed, angle, time]
        """
        dict_one_agent = {}
        for key, value in location_dict.items():
            speed, angle, lat, long = self.speed_angle(location_dict, key)
            timestamp = self.timestamp(location_dict, key)
            dict_one_agent[key] = [lat, long, speed, angle, timestamp]

        with open(filename + '.json', 'w') as fp:
            json.dump(dict_one_agent, fp)
        return dict_one_agent

def generate_query(database_name):
    """Generate query object by given database name

    :param database_name: The database name user want to generate query object
    :type database_name: String
    :return: a single query object
    """
    Mongo_client = MongoClient([database_name])
    client = Mongo_client.mongo_clients[database_name]
    query = Query(client)
    return query

def find_all_agent(org_list, ENROUTE_TRACKING):
    """Find all of agents by given org_id list

    :param org_list: The org_id that we want to look for
    :type org_list: a list of org_id
    :param ENROUTE_TRACKING: database name
    :return: a list of agent id
    """
    query = generate_query(ENROUTE_TRACKING)
    total_agent = []
    for i in range(len(org_list)):
        total_agent += query.query_agents(org_list[i])

    return total_agent

def find_all_tasks(total_agent, ENROUTE_TRACKING):
    """Find all of tasks by given agents

    :param total_agent: The agent_id that we want to look for
    :type total_agent: a list of agent id
    :param ENROUTE_TRACKING:  database name
    :return: a dict of the task
            key: agent id
            value: a list of tasks
    """
    query = generate_query(ENROUTE_TRACKING)
    task_dict = query.query_tasks(total_agent)

    return task_dict

def find_all_location(task_dict, ENROUTE_STATS):
    """Find all of location point by task dict

    :param task_dict: A dict of task, key is the agent id & value is the list of tasks
    :param ENROUTE_STATS: database name
    :return:
    """
    total_task = []
    for key, value in task_dict.items():   # take out all of task is from task dict
        total_task += value

    query = generate_query(ENROUTE_STATS)
    total_location = query.find_locationpoints(total_task)

    return total_location

def dict_to_json(dict, filename):
    """ Output any dict to json file

    :param dict: The dict you want to ouput
    :param filename: The filename for ouput file, where the filename is String
    """
    with open(filename + '.json', 'w') as fp:
        json.dump(dict, fp)

def main():
    """
    Run this main function you can output the location point json file
    by Company, shop or agent.
    c : Company (org_id)
    s : Shop (org_id)
    a : Agent (agent_id)
    """

    ENROUTE_TRACKING = "tracking_core"
    ENROUTE_STATS = "tracking_stats"

    tp = input('Query all or single agent: (c(company)/s(Shop)/a(Agent))')
    if (str(tp) == "c"):
        query = generate_query(ENROUTE_TRACKING)
        og = input('Input hierarchy org_id number: ')
        org_list = query.query_orgid(int(og))
        print("The number of org_id in the given hierarchy number:", len(org_list))
        print("OrgID query finished-------------------------------------------------")

        total_agent = find_all_agent(org_list, ENROUTE_TRACKING)
        print("The number of agent in the given hierarchy number:", len(total_agent))
        print("Agent query finished-------------------------------------------------")

        task_dict = find_all_tasks(total_agent, ENROUTE_TRACKING)
        filename_agent = input('Input filename for the Agent_task_dict:')
        filename_agent = 'Query/Agent task/' + filename_agent
        dict_to_json(task_dict, str(filename_agent))
        print("Task query finished--------------------------------------------------")

        print("Query location point, it might take a while...(8min)")
        total_location = find_all_location(task_dict, ENROUTE_STATS)
        print("The number of task:", len(total_location))
        filename_task = input('Input filename for the Task_location_dict:')
        filename_task = 'Query/Company location/' + filename_task
        location_dict = query.to_json(total_location, str(filename_task))

        print("All done")


    elif (str(tp) == "s"):
        query = generate_query(ENROUTE_TRACKING)
        sp = input('Input shop org_id number: ')
        shop_agent = find_all_agent([int(sp)], ENROUTE_TRACKING)
        print("The number of agent in the given shop number:", len(shop_agent))
        print("Agent query finished-------------------------------------------------")

        task_dict = find_all_tasks(shop_agent, ENROUTE_TRACKING)
        print("Task query finished--------------------------------------------------")
        print("Query location point, it might take a while...(8min)")
        total_location = find_all_location(task_dict, ENROUTE_STATS)
        print("The number of task:", len(total_location))
        filename_task = input('Input filename for the Task_location_dict:')
        filename_task = 'Query/Shop location/' + filename_task
        location_dict = query.to_json(total_location, str(filename_task))

        print("All done")

    elif (str(tp) == "a"):
        query = generate_query(ENROUTE_TRACKING)
        ag = input('Input agent_id number: ')
        agent_task = find_all_tasks([int(ag)], ENROUTE_TRACKING)
        print("Task query finished--------------------------------------------------")
        print("Query location point, it might take a while...")
        agent_location = find_all_location(agent_task, ENROUTE_STATS)
        print("The number of task:", len(agent_location))
        filename_task = input('Input filename for the Agent_location_dict:')
        filename_task = 'Query/Single Agent location/' + filename_task
        agent_dict = query.to_json(agent_location, str(filename_task))

        print("All done")


if __name__ == "__main__":
    main()
