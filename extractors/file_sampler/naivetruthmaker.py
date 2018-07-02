import csv

with open("naivetruth.csv", 'w') as g:

    with open("naivetruth2.csv", 'r') as f:
        for line in f:
            print(type(line))
            line2 = line.replace('/home/tskluzac/pub8/', '/home/skluzacek/Downloads/pub8/')
            print(line2)

            g.write(line2)

