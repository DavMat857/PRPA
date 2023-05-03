from pyspark import SparkContext
import sys
import string

def write_file(filename, txt):
    with open(filename, "w") as f:
        f.write(txt)
    print("Information saved in file " + filename + " successfully.")

def word_split(line):
    for c in string.punctuation + "¿!«»":
        line = line.replace(c, " ")
        line = line.lower()
    return len(line.split())

def main(filename):
    with SparkContext() as sc:
        sc.setLogLevel("ERROR")
        lines_rdd = sc.textFile(filename)
        words_rdd = lines_rdd.map(word_split)
        print(words_rdd.collect())
        total_sum = words_rdd.sum()
        print("The total sum is: " + str(total_sum))
        if filename == "quijote_s05.txt":
            write_file("out_quijote_s05.txt", str(total_sum))
        else:
            write_file("out_quijote.txt", str(total_sum))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {0} <file>".format(sys.argv[0]))
    else:
        main(sys.argv[1])
