from database import create_database, create_api_key


create_database()


key = create_api_key("development")


print()
print("================================")
print("YOUR API KEY")
print("================================")
print(key)
print("================================")
print()
print("Save this key. You will use it")
print("to test your API.")
print()