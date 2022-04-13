import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="daniel",
    passwd="mynewpassword"
)

my_cursor = mydb.cursor()

# to prevent accidental creation of a new database
my_cursor.execute("CREATE DATABASE membership")
# my_cursor.execute("DROP DATABASE membership")

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)
