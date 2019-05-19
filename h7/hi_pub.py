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
        pass

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
            return json.loads(response.content.decode('utf-8'))
        else:
            print("Error requesting data")
            return None

    def calculate_heat_index(self, message):
        """
        calculate the heat index
        :param message: json format of message
        :return: the heat index
        """

        HI = 0.0  # heat index
        T = message["main"]['temp'] - 273.15  # temperature in celcius
        print("Temperature is {0}".format(T))
        R = message["main"]['humidity'] / 100  # humidify in percentage

        c1 = -8.78469475556
        c2 = 1.61139411
        c3 = 2.33854883889
        c4 = -0.14611605
        c5 = -0.012308094
        c6 = -0.0164248277778
        c7 = 0.002211732
        c8 = 0.00072546
        c9 = -0.000003582

        HI = c1 + c2 * T + c3 * R + c4 * T * R + c5 * T * T + c7 * T * T * R + c8 * T * R * R + c9 * T * T * R * R

        return str(HI)


if __name__ == "__main__":
    broker_address = config.broker_ip
    broker_port = config.broker_port
    # Instantiate an object of type Publisher
    publisher = Publisher(broker_address, broker_port)
    # Topics that are used to publish data.
    count = 0
    hour_of_day = 24
    print(config.cities)
    while count <= hour_of_day:
        print("Number of running is:  " + str(count))
        count = count + 1
        # sending the heat index for all cities
        for i in range(0, len(config.cities)):
            city = config.cities[i]
            country_code = config.country_codes[i]
            request_url = config.weather_url.format(city, country_code)
            data = publisher.get_data_(request_url)
            if data is None:
                print("Error")
                continue
            message = publisher.calculate_heat_index(data)
            topic = "ece1508/ap47240/{0}/hi".format(city)
            publisher.publish(topic, message)
        # wait
        clock.sleep(3600)
