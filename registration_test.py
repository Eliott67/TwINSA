from registration import validate_registration, users_db
from user import User


# Success 
print("Test 1 - Success :")
users_db.users = {}
u = User("mat", "test@example.com", "Pass123!", "Mat", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is True
assert msg == "Registration successful."

# Missing fields
print("Test 2 - Missing fields :")
users_db.users = {}
u = User("", "test1@example.com", "Pass123!", "Mat01", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is False
assert msg == "All fields are required."

users_db.users = {}
u=User("mat1", "", "Pass123!", "Mat1", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is False
assert msg == "All fields are required."

users_db.users = {}
u=User("mat2", "test2@example.com", "", "Mat2", 20, "France")
valid, msg = validate_registration(u, "")
assert valid is False
assert msg == "All fields are required."


# Invalid email format
print("Test 3 - Invalid email format :")
users_db.users = {}
u = User("mat3", "invalidemail", "Pass123!", "Mat3", 20, "France")
valid, msg = validate_registration(u, "Pass123!")
assert valid is False
assert msg == "Invalid email format."

# Passwords do not match
#print("Test 4 - Passwords do not match :")
#users_db.users = {}


# Weak password
print("Test 5 - Weak password :")
users_db.users = {}
u = User("mat4", "test4@example.com", "weak", "Mat4", 20, "France")
valid, msg = validate_registration(u, "weak")
assert valid is False
assert msg == "Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character."

# Duplicate email
#print("Test 6 - Duplicate email :")
#users_db.users = {}
#u=User("mat5", "test@example.com", "Pass234!", "Mat5", 20, "France")
#valid, msg = validate_registration(u, "Pass234!")
#assert valid is False    
#assert msg == "Email already exists. Please choose a different email."

# Duplicate username
print("Test 7 - Duplicate username :")
users_db.users = {}
u=User("mat", "test6@example.com", "Pass234!", "Mat6", 20, "France")
valid, msg = validate_registration(u, "Pass234!")
assert valid is False
assert msg == "Username already exists. Please choose a different username."


# Spaces in username or email
print("Test 8 - Spaces in username or email :")
users_db.users = {}
u=User("mat 07", "test7@example.com", "Pass234!", "Mat7", 20, "France")
valid, msg = validate_registration(u, "Pass234!")
assert valid is False    
assert msg == "Username and email cannot contain spaces."

users_db.users = {}
u=User("mat07", "test@ example.com", "Pass234!", "Mat07", 20, "France")
valid, msg = validate_registration(u, "Pass234!")
assert valid is False        
assert msg == "Username and email cannot contain spaces."


