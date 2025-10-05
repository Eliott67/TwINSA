from registration import registration, users_db

# PROBLEME : add_user prend que 2 arguments or on en donne 4 dans les tests

def reset_users_db():
    users_db.users = []

# Success 
print("Test 1 - Success :")
reset_users_db()
users_db.add_user("test@example.com", "mat", "Pass123!", "Pass123!")
print(registration())
print()

# Missing fields
print("Test 2 - Missing fields :")
reset_users_db()
users_db.add_user("test1@example.com", "mat01", "Pass234!", "")
print(registration())
reset_users_db()
users_db.add_user("", "mat", "Pass234!", "Pass234!")
print(registration())
reset_users_db()
users_db.add_user("test1@example.com", "", "Pass234!", "Pass234!")
print(registration())
print()

# Invalid email format
print("Test 3 - Invalid email format :")
reset_users_db()
users_db.add_user("test2example.com", "mat02", "Pass234!", "Pass234!")
print(registration())
print()

# Passwords do not match
print("Test 4 - Passwords do not match :")
reset_users_db()
users_db.add_user("test3@example.com", "mat03", "Pass234!", "Pass123!")
print(registration())
print()

# Weak password
print("Test 5 - Weak password :")
reset_users_db()
users_db.add_user("test4@example.com", "mat04", "pass234", "pass234")
print(registration())
print()

# Duplicate email
print("Test 6 - Duplicate email :")
reset_users_db()
users_db.add_user("mat05", "Pass234!")
print(registration())
print() 

# Duplicate username
print("Test 7 - Duplicate username :")
reset_users_db()
users_db.add_user("test5@example.com", "mat", "Pass234!", "Pass234!")
print(registration())
print()

# Spaces in username or email
print("Test 8 - Spaces in username or email :")
reset_users_db()
users_db.add_user("test6@example.com", "mat 06", "Pass234!", "Pass234!")
print(registration())
reset_users_db()
users_db.add_user("test 7@example.com", "mat07", "Pass234!", "Pass234!")
print(registration())
print()

