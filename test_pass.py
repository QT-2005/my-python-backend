import bcrypt

password = "Tuan1234"
# Tạo salt mới
salt = bcrypt.gensalt()

# Hash mật khẩu với salt
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

print(hashed_password)