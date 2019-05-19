"""
Created on Mar, 2019
@author: Morteza Moghaddassian
@Project: ECE1508 - NetSoft Course
"""
# paho is a client library to communicate with Mosquitto broker that implements MQTT V3.1.1
import paho.mqtt.client as paho
import config
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import pickle

'''
    @class_name: Subscriber
    @role: Subscribing for contents and keeping them in memory.
    @number of methods: 4
    @access modifier: public    
'''


class Subscriber:
    # The topic that the subscriber needs to use for receiving the content from the message broker.
    subscriber_topic = None
    # Broker IP address.
    broker_address = None
    # The port that the broker is listening on for incoming connections. The default is 1883 for Mosquitto broker.
    broker_port = None
    # Is used to save the message received from the broker.
    message_received = ''
    # stores all the the aqi of each city, cities' names are key the the value is a list of aqi
    aqi_dict = defaultdict(list)
    # number of receiving message for each city, in dict format
    # i.e., number_of_rev_message_dict["Montreal"] = 1
    number_of_rev_message_dict = defaultdict(int)
    #
    MAX_MESSAGE = 24
    '''
        @input: address, port, topic
        @role: Constructor method
    '''

    def __init__(self, address, port, topic):
        # The broker IP address (142.150.208.252)
        self.broker_address = str(address)
        # The broker port number (1883)
        self.broker_port = int(port)
        # Subscription Topic
        self.subscriber_topic = topic
        print("topic is {0}".format(self.subscriber_topic))

    '''
        @input: client, userdate, flags, rc
        @role: Is being used to pair with the on_connect method on the broker to exchange the subscription topic.
    '''

    def on_connect(self, client, userdata, flags, rc):
        # Subscribing for contents with the specified topic.
        client.subscribe(self.subscriber_topic)

    '''
        @input: client, userdata, message
        @role: save the received data to csv files according to the topic, for instance, 
        data from topic ece1508/Toronto/hi will be saved to Toronto.csv
        receiving MAX_MESSAGE = 24 for each city only
            
    '''

    def on_message(self, client, userdata, message):
        # Printing the message which is obtained from the broker.
        message_data = str(message.payload, encoding='utf-8')
        print("The city : {0}/{1}".format(message.topic, message_data))
        for city in config.cities:
            if (city in message.topic) and (self.number_of_rev_message_dict[city] < self.MAX_MESSAGE):
                try:
                    self.number_of_rev_message_dict[city] = self.number_of_rev_message_dict[city] + 1
                    self.aqi_dict[city].append(float(message_data))
                    # save data to csv file
                    with open("aqi_" + city + ".csv", "a") as city_file:
                        # save the data to csv files with file name is city's name
                        city_file.write(message_data + "\n")
                    for topic, message in self.aqi_dict.items():
                        print("{0} has {1} message".format(topic, len(message)))
                except Exception as e:
                    print(e)
                    continue
        # Disconnecting from the broker.
        client.disconnect()

    '''
        @role: Subscribing to the broker and enabling the retrieval of the contents specified by the topics of interest.
    '''

    def subscribe(self):
        # Creating an MQTT client object.
        sub = paho.Client()
        # An infinite loop to keep the subscriber alive.
        while self.is_continuing_receiving():
            # Connecting to the broker.
            sub.connect(self.broker_address, self.broker_port)
            # Receiving the message (MMG)
            sub.on_message = self.on_message
            # Providing the topic of interest.
            sub.on_connect = self.on_connect
            # Keep the subscriber running until the whole message is received.
            sub.loop_forever()

    def is_continuing_receiving(self):
        """
        check if all data is received
        :return: True if each city receive 24 data points, otherwise False
        """
        for city in config.cities:
            if self.number_of_rev_message_dict[city] != self.MAX_MESSAGE:  # 24 message
                return True
        return False

    def creat_graph(self):
        if len(self.aqi_dict) < 1:
            print("aqi is not collected")
        # save a backup of data
        print("Saving dictionary to backup")
        with open("aqi.pkl", "wb") as f:
            pickle.dump(self.aqi_dict, f)
        print(self.aqi_dict)
        heat_index_df = pd.DataFrame.from_dict(self.aqi_dict)
        ax = heat_index_df.plot(title="Air Quality Index", grid=True)
        ax.set_xlabel("time")
        ax.set_ylabel("value")
        plt.savefig("aqi_index.png")


if __name__ == "__main__":
    broker_address = config.broker_ip
    broker_port = config.broker_port
    # all the topics associated with the cities
    topics = [("ece1508/ap47240/{0}/aqi".format(city), 0) for city in config.cities]
    subscriber = Subscriber(broker_address, broker_port, topics)
    subscriber.subscribe()
    # subscriber.creat_graph()
    print("Finish")
