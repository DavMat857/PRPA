from pyspark import SparkContext
import sys
import random

def roll_dice():
    #Simulate rolling a 6-sided dice
    return random.randint(1, 6)

def get_percentage():
    #Return a random integer between 0 and 100
    return random.randint(0, 100)

def main(input_file, output_file):
    #Read lines from input file, filter them randomly, and write to output file.
    with SparkContext() as sc:
        sc.setLogLevel("ERROR")
        lines_rdd = sc.textFile(input_file)
        with open(output_file, "w") as f:
            for line in lines_rdd.collect():
                dice_roll = roll_dice()
                percentage = get_percentage()
                if dice_roll < percentage:
                    f.write(line)
        print("END")
        print("Lines written to file {0} successfully.".format(output_file))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {0} <input_file>".format(sys.argv[0]))
    else:
        main(sys.argv[1], "quijote_s05.txt")
