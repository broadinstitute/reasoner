def db_select(db, sql, data=None):
    cursor = db.cursor(dictionary=True)
    # try:
    if data is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, data)
    results = cursor.fetchall()
    # except:
    #     print("Error: unable to fetch data")
    return(results)
