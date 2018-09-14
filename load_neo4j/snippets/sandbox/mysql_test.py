import mysql.connector

# Open database connection
db = mysql.connector.connect(user='reasoner', password='reasoner',
                              host='127.0.0.1',
                              database='semmeddb')

# prepare a cursor object using cursor() method
cursor = db.cursor()

sql = 'SELECT * FROM PREDICATION LIMIT 10'

try:
   # Execute the SQL command
   cursor.execute(sql)
   # Fetch all the rows in a list of lists.
   results = cursor.fetchall()
   for row in results:
        print(row);
except:
   print("Error: unable to fetch data")

# disconnect from server
db.close()