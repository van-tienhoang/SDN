"""
Created on Mar, 2019
@author: Morteza Moghaddassian
@Project: ECE1508 - NetSoft Course
"""
# paho is a client library to communicate with Mosquitto broker that implements MQTT V3.1.1 (MMG)
import paho.mqtt.client as paho
import time as clock
import requests, json
import config

'''
    @class_name: Publisher
    @role: Publishing contents to the message broker.
    @number of methods: 3
    @access modifier: public    
'''


class Publisher:
    # The broker address.
    broker_address = None
    # The port that the broker is listening on for incoming connections. The default is 1883 for Mosquitto broker.
    broker_port = None
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(config.hi_token)}
    '''
        @input: address, port
        @role: Constructor method
    '''

    def __init__(self, address, port):
        # The broker IP address (142.150.208.252)
        self.broker_address = address
        # The broker port number (1883)
        self.broker_port = int(port)

    def on_publish(client, userdata, result):
        print("mid:{0}".format(result))

    '''
        @input: topic, message (The content that has to be published).
        @role: Publishing the message to the broker.
        @info: This method maintains a request-respond model with the caller.
    '''

    def publish(self, topic, message):
        # Creating a paho (MQTT) client object.
        pub = paho.Client()
        pub.on_publish = self.on_publish
        # Connecting the "pub" object to the message broker.
        pub.connect(self.broker_address, self.broker_port)
        # Publishing the data.
        answer = pub.publish(topic, message)
        # print("answer is{0}".format(answer))
        print("Published " + topic + " number " + str(message))
        # Disconnecting the client paho (MQTT) objecct.
        pub.disconnect()

    def get_data_(self, url):
        """
        get the data from the api
        :return:
        """
        response = requests.get(url)
        if response.status_code == 200:
            try:
                return json.loads(response.content.decode('utf-8'))['data']['aqi']
            except Exception as e:
                print(e)
                print("error in extracting data")
        else:
            print("Error requesting data")
            return None


if __name__ == "__main__":
    broker_address = config.broker_ip
    broker_port = config.broker_port
    # Instantiate an object of type Publisher
    publisher = Publisher(broker_address, broker_port)
    # Topics that are used to publish data.
    count = 0
    hour_of_day = 24
    print(config.cities)
    while count < hour_of_day:
        print("Number of running is:  " + str(count))
        count = count + 1
        for i in range(0, len(config.cities)):
            city = config.cities[i]
            request_url = config.air_url.format(city)
            data = publisher.get_data_(request_url)
            # print(data)
            if data is None:
                print("Error")
                continue
            topic = "ece1508/ap47240/{0}/aqi".format(city)
            publisher.publish(topic, data)
        clock.sleep(3600)
