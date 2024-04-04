from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("fernet_key.key", "wb") as f:
        f.write(key)
    return key

if __name__ == "__main__":
    generate_key()
    print("Fernet key generated and saved to 'fernet_key.key'")