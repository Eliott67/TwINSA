<<<<<<< HEAD
import registration
import users_db
=======
from registration import validate_registration, users_db
from user import User

>>>>>>> be79723 (Application à jour avec logos et registration qui fonctionne)

# Success 
print("Test 1 - Success :")
users_db.users_list = []
users_db.usernames_list = []
u = User("mat", "test@example.com", "Pass123!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is True
assert msg == "Registration successful."

# Missing fields
print("Test 2 - Missing fields :")
users_db.users_list = []
users_db.usernames_list = []
u = User("", "test@example.com", "Pass123!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is False
assert msg == "All fields are required."

users_db.users_list = []
users_db.usernames_list = []
u=User("mat", "", "Pass123!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is False
assert msg == "All fields are required."

users_db.users_list = []
users_db.usernames_list = []
u=User("mat", "test@example.com", "", "Mat", 20, "France")
valid, msg = validate_registration(u, "")
assert valid is False
assert msg == "All fields are required."


# Invalid email format
print("Test 3 - Invalid email format :")
users_db.users_list = []
users_db.usernames_list = []
u = User("mat", "invalidemail", "Pass123!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is False
assert msg == "Invalid email format."

# Passwords do not match
print("Test 4 - Passwords do not match :")
users_db.users_list = []
users_db.usernames_list = []
u = User("mat4", "test4@example.com", "Pass123!", "Mat4", 20, "France")
valid, msg = validate_registration(u, "Different123!")
assert valid is False
assert msg == "Passwords do not match."


# Weak password
print("Test 5 - Weak password :")
users_db.users_list = []
users_db.usernames_list = []
u = User("mat", "test@example.com", "weak", "Mat", 20, "France")
valid, msg = validate_registration(u, "weak")
assert valid is False
assert msg == "Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character."

#Duplicate email
print("Test 6 - Duplicate email :")
users_db.users_list = []
users_db.usernames_list = []
existing = User("mat", "test@example.com", "Pass123!", "Mat", 20, "France")
users_db.add_user(existing)
u=User("mat01", "test@example.com", "Pass234!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass234!")
assert valid is False    
assert msg == "Email already exists. Please choose a different email."

# Duplicate username
print("Test 7 - Duplicate username :")
users_db.users_list = []
users_db.usernames_list = []
existing = User("mat", "existing@example.com", "Pass123!", "Mat", 20, "France")
users_db.add_user(existing)
u=User("mat", "test@example.com", "Pass234!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass234!")
assert valid is False
assert msg == "Username already exists. Please choose a different username."


# Spaces in username or email
print("Test 8 - Spaces in username or email :")
users_db.users_list = []
users_db.usernames_list = []
u=User("mat 00", "test@example.com", "Pass234!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass234!")
assert valid is False    
assert msg == "Username and email cannot contain spaces."

users_db.users_list = []
users_db.usernames_list = []
u=User("mat", "test@ example.com", "Pass234!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass234!")
assert valid is False        
assert msg == "Username and email cannot contain spaces."


