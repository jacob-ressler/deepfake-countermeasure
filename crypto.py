import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

# Generate Asymmetric Key Pair
def genAsyKeys():
    private_key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048,
        backend = default_backend()
    )
    public_key = private_key.public_key()
    #save keys
    serial_private = private_key.private_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PrivateFormat.PKCS8,
        encryption_algorithm = serialization.NoEncryption()
    )
    with open('private_noshare.pem', 'wb') as f: 
        f.write(serial_private)

    serial_public = public_key.public_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open ('public_shared.pem', 'wb') as f: 
        f.write(serial_public)

    print("Public and Private key generated")
    return  

######### Public (shared) device only ##########
def read_public (filename = "public_shared.pem"):
    with open("public_shared.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key

#########      Private device only    ##########
def read_private (filename = "private_noshare.pem"):
    with open(filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


# Generate a signature from a message
def sign(message):
    ######### Public (shared) device only #########
    message = bytes(message,'utf-8')
    private_key = read_private()
    signature = private_key.sign(
                    message,
                    padding.PSS(
                        mgf = padding.MGF1(hashes.SHA256()),
                        salt_length = padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
    return signature 

# Verify a signature-message pair
def verify(signature, message):
    #########      Private device only    ##########
    public_key = read_public()
    original = bytes(message,'utf-8')
    original_message = public_key.verify(
        signature,
        original,
        padding.PSS(
            #mask generated function object 
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return original_message


# Call the file to generate asymmetric keys if you don't already have them
if __name__ == '__main__':
    genAsyKeys()