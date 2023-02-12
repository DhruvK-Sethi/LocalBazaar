import pandas as pd
import sqlite3

# Load the .xlsx file into a pandas DataFrame
dfProducts = pd.read_excel('daveydark/src/Products Db.xlsx')
dfSellers = pd.read_excel('daveydark/src/Database.xlsx')
dfscores = pd.read_excel('daveydark/src/Prediction Db.xlsx')
dfbuyers = pd.read_excel('daveydark/src/buyers.xlsx')
# dfProducts = pd.read_excel('products.xlsx')

# Connect to an SQLite database
conn = sqlite3.connect('instance/db.sqlite3')
# conn = sqlite3.connect('../var/main-instance/db.sqlite3')
cursor = conn.cursor()
table_names = ['sellers','products']
for table_name in table_names:
    cursor.execute(f"DELETE FROM {table_name};")
conn.commit()


# Write the DataFrame to the database
dfProducts.to_sql('products', conn, if_exists='replace', index=False)
dfSellers.to_sql('sellers', conn, if_exists='replace', index=False)
dfscores.to_sql('scores', conn, if_exists='replace', index=False)
dfbuyers.to_sql('buyers', conn, if_exists='replace', index=False)
# dfProducts.to_sql('products', conn, if_exists='replace', index=False)

# Close the connection to the database
conn.close()
