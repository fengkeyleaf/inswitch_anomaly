###
# Label input file as benign traffic
# Riley Mcginn
###

import csv
import sys

input = open(sys.argv[1])

output = open(sys.argv[2], "w", newline="")

reader = csv.reader(input)
writer = csv.writer(output)

# write header to new file
headers = next(reader)
headers.append("Label")
writer.writerow(headers)

# label packets as benign (0)
for packet in reader:
    packet.append("1")
    writer.writerow(packet)
