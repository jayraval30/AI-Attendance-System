import redis

# Connect to Redis Client
hostname = 'redis-12072.c92.us-east-1-3.ec2.cloud.redislabs.com'
portnumber = 12072
password = 'zjefqIKhAZqzAkUCYpJtgas5RYyMEobi'

r = redis.StrictRedis(host=hostname,
                      port=portnumber,
                      password=password)

# Simulated Logs
with open('simulated_logs.txt', 'r') as f:
    logs_text = f.read()

encoded_logs = logs_text.split('\n')

# Push into Redis database
r.lpush('attendance:logs', *encoded_logs)
