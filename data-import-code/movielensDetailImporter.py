import os
import re
from pyspark import SparkContext
from pyspark.sql import SQLContext, Row

SPARK_HOME = os.environ['SPARK_HOME']
# Regex used to seperate movie movieId, imdbId, and tmdbId
RE = re.compile(r'(?P<movieId>\d+),(?P<imdbId>\d+),(?P<tmdbId>\d+),(?P<director>.+),(?P<cast>.+)')

# (r'(?P<movieId>\d+),"?(?P<name>.+)\((?P<year>\d+)\) ?"?,(?P<genres>.+)')

sc = SparkContext("local", "MovielensDetailImporter")  # Initialize the Spark context
sqlContext = SQLContext(sc)  # Initialize the SparkSQL context

# Read in the text file as an RDD
data = sc.textFile('/home/ubuntu/Recommender/MovieRecommendation/integration/modified.csv')

header = data.first()  # Get the csv header


# data = data.filter(lambda line: line != header) # Filter out the csv header

# Split the CSV file into rows
# Formatter that takes the CSV line and outputs it as a list of datapoints
# Uses a regex with named groups
def formatter(line):
    m = RE.match(line)  # Seperates datapoints
    if (m != None):
        m = m.groupdict()
        movieId = int(m['movieId'])
        imdbId = int(m['imdbId'])
        if m['tmdbId'] != None:
            tmdbId = int(m['tmdbId'])
        else:
            tmdbId = -1
        director = m['director']
        cast = m['cast'].split('|')
        print [movieId, imdbId, tmdbId, director, cast]
        return [movieId, imdbId, tmdbId, director, cast]


data = data.map(formatter)
data = data.filter(lambda line: line != None)  # Filter out rows that dont match

# Test to make sure all the data is imported
print data.count()

# Map the data into a Row data object to prepare it for insertion
rows = data.map(lambda r: Row(movieId=r[0], imdbId=r[1], tmdbId=r[2], director=r[3], cast=r[4]))

# Create the schema for movies and register a table for it
schemaLinks = sqlContext.createDataFrame(rows)
schemaLinks.registerTempTable("detail")
schemaLinks.save('/home/ubuntu/Recommender/MovieRecommendation/integration/tables/detail')
