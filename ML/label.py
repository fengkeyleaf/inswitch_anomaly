###
# python file to label data as
#	0 -> not attack
#	1 -> attack
# sean bergen
###

import csv
import sys

# source and destination dictionaries
# we will use these to get actual counts of ip addresses
# and based on how many we have seen we will try to classify
# the packets as attacks or legitimate
src_dict = {}
dst_dict = {}

# open csv file that is passed in
file1 = open(sys.argv[1])
file2 = open(sys.argv[2])
output = open(sys.argv[3],"w",newline="")

reader1 = csv.reader(file1)
reader2 = csv.reader(file2)
writer = csv.writer(output)

# add label column to header
headers = next(reader1)
next(reader2)
headers.append("Label")
writer.writerow(headers)

# reader 1 is the benign traffic
# writing out 200,000 packets
i = 0
for packet in reader1:
    if i >= 500:
        break
    packet.append("0")
    writer.writerow(packet)
    i = i + 1

# reader 2 is attack traffic
# writing out 500,000 packets
#
# bad_list is the list of bad ips and the victim ip that was attacked
# which will let us see the bad traffic
bad_list = ['18.216.24.42',
            '18.218.115.60',
            '18.216.200.189',
            '18.218.83.150',
            '172.31.69.25',
            '18.219.32.43',
            '18.218.55.126',
            '172.31.69.28',
            '18.218.229.235',
            '52.14.136.135',
            '131.202.242.193',
            '18.219.5.43',
            '18.219.9.1',
            '195.22.125.42',
            '18.218.11.51',
            '91.185.191.213',
            '221.194.47.239',
            '18.218.229.235',
            '18.216.200.189',
            '94.231.103.172',
            '115.238.245.8',
            '195.22.125.42',
            '200.241.132.151',
            '221.194.47.233',
            '185.171.50.102',
            '18.218.115.60',
            '18.216.24.42',
            '66.198.240.13',
            '18.219.32.43',
            '131.202.242.193',
            '84.73.10.63',
            '18.219.5.43',
            '12.156.73.33',
            '18.219.9.1',
            '122.226.181.165',
            '18.218.11.51',
            '18.218.55.126',
            '52.14.136.135',
            '107.180.108.2',
            '37.97.217.235',
            '190.214.77.75',
            '122.226.181.166',
            '172.31.69.25',
            '52.15.106.142',
            '172.31.69.18']
i = 0
for packet in reader2:
    if i >= 5000:
        break
    if packet[1] in bad_list or packet[2] in bad_list:
        packet.append("1")
    else:
        packet.append("0")
    writer.writerow(packet)
    i = i + 1


#print(src_dict)