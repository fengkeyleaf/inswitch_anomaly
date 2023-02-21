###
# Psuedorandomly interlace two given .csv files and write to the output
# Riley McGinn
###

import csv
import sys
import random

# open the csv files passed in
file1 = open(sys.argv[1])
file2 = open(sys.argv[2])
output = open(sys.argv[3],"w",newline="")

# create readers
reader1 = csv.reader(file1)
reader2 = csv.reader(file2)
writer = csv.writer(output)

# keep one of the headers, discard the other
writer.writerow(next(reader1))
next(reader2)

# Loop through input simultaneously
while True:
    # Choose a random number of rows to read from file 1
    num_rows1 = random.randint(0, 10)

    # Choose a random number of rows to read from file 2
    num_rows2 = random.randint(0, 10)

    # Write num_rows1 pkts from file1
    for i in range(num_rows1):
        try:
            row1 = next(reader1)
            writer.writerow(row1)
        except StopIteration:
            # file1 out of rows, write the rest of file 2 and break
            for row2 in reader2:
                writer.writerow(row2)
            break
    
    # Write num_rows2 pkts from file2
    for i in range(num_rows2):
        try:
            row2 = next(reader2)
            writer.writerow(row2)
        except StopIteration:
            # file2 out of rows, write the rest of file 1 and break
            for row1 in reader1:
                writer.writerow(row1)
            break

