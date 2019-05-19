# contains all configuration
traffic_sensor_url = "http://portal.cvst.ca/api/0.1/HW_speed"
bixi_url = "http://portal.cvst.ca/api/0.1/bixi"
aqi_token = "f4774fbfc70f0dd6a2a0da722e5bc75d56f6ee72"
hi_token = "6608518ffb733383ab395358aa969571"
cities = ["toronto", "montreal", "new york", "shanghai", "tehran", "london", "seoul", "jakarta", "sydney", "tokyo"]
country_codes = ["ca", "ca", "us", "cn", "ir", "uk", "kr", "id", "au", "jp"]
broker_ip = "142.150.208.252"
broker_port = 1883
# url
air_url = "http://api.waqi.info/feed/{0}/?token=f4774fbfc70f0dd6a2a0da722e5bc75d56f6ee72"
weather_url = "https://api.openweathermap.org/data/2.5/weather?q={0},{1}&appid=6608518ffb733383ab395358aa969571"
csv_aqi = "aqi.csv"
csv_aqi_headers = ["aqi", "name", "co", "no2", "o3", "p", "pm25", "so2", "t", "w", "time"]
csv_hi = "hi.csv"
csv_hi_header = []