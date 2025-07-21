import random
import string
import time

def generate_password(length=5):
    characters = string.ascii_lowercase + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

target_password = "so@l@"
attempts = 0

start_time = time.time()

while True:
    password = generate_password()
    attempts += 1
    print(f"Attempt {attempts}: {password}")
    if password == target_password:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\nTarget password '{target_password}' found after {attempts} attempts.")
        print(f"Time taken: {duration:.4f} seconds")
        break
    