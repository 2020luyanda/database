from app.db import run_query

user_input = "'OR '1'='1"
#unsafe query
my_query = f"select * from film where title = '{user_input}'"


# print(run_query(my_query))

safe_rows = run_query("SELECT title FROM film WHERE title = %s", (user_input,))
print("SAFE rows returned:", len(safe_rows))