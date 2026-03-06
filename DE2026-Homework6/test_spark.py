import pyspark
from pyspark.sql import SparkSession
import os

# Configurar log4j antes de iniciar Spark
log4j_path = os.path.join(os.path.dirname(__file__), "log4j2.properties")

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .config("spark.ui.showConsoleProgress", "false") \
    .config("spark.driver.extraJavaOptions", f"-Dlog4j.configuration=file:{log4j_path}") \
    .getOrCreate()

# Configurar nivel de logging para suprimir warnings
spark.sparkContext.setLogLevel("ERROR")

print(f"Spark version: {spark.version}")

df = spark.range(10)
df.show()

spark.stop()