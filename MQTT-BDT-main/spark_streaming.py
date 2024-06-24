from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, DoubleType, StringType

# Define the schema for the data
schema = StructType([
    StructField("main", StructType([
        StructField("temp", DoubleType(), True),
        StructField("feels_like", DoubleType(), True),
        StructField("temp_min", DoubleType(), True),
        StructField("temp_max", DoubleType(), True),
        StructField("pressure", DoubleType(), True),
        StructField("humidity", DoubleType(), True),
        StructField("sea_level", DoubleType(), True),
        StructField("grnd_level", DoubleType(), True)
    ]), True),
    StructField("visibility", DoubleType(), True),
    StructField("wind", StructType([
        StructField("speed", DoubleType(), True),
        StructField("deg", DoubleType(), True),
        StructField("gust", DoubleType(), True)
    ]), True),
    StructField("rain", StructType([
        StructField("1h", DoubleType(), True)
    ]), True),
    StructField("clouds", StructType([
        StructField("all", DoubleType(), True)
    ]), True),
    StructField("weather", StringType(), True),
    StructField("coord", StructType([
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True)
    ]), True),
    StructField("dt", DoubleType(), True),
    StructField("sys", StructType([
        StructField("type", DoubleType(), True),
        StructField("id", DoubleType(), True),
        StructField("country", StringType(), True),
        StructField("sunrise", DoubleType(), True),
        StructField("sunset", DoubleType(), True)
    ]), True),
    StructField("timezone", DoubleType(), True),
    StructField("id", DoubleType(), True),
    StructField("name", StringType(), True),
    StructField("cod", DoubleType(), True)
])

# Initialize Spark Session
spark = SparkSession.builder.appName("WildfireDetection").getOrCreate()

# Read data from MQTT broker
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "mqtt_broker:1883") \
    .option("subscribe", "wildfire/data") \
    .load()

# Convert the value column from binary to string
df = df.selectExpr("CAST(value AS STRING)")

# Parse the JSON data
df = df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Define the processing logic
def detect_wildfire(df):
    threshold = 5.0  # Example threshold
    df = df.withColumn("fire_risk_index", (col("main.temp") * (100 - col("main.humidity")) * col("wind.speed")) / 1000)
    df = df.filter(col("fire_risk_index") > threshold)
    return df

# Apply the processing logic
result_df = detect_wildfire(df)

# Write the results to the console for now
query = result_df.writeStream.outputMode("append").format("console").start()

query.awaitTermination()
