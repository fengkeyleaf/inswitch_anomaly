###
# Label input file as bad traffic
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

# label packets as bad (1)
for packet in reader:
    packet.append("1")
    writer.writerow(packet)


