from abc import ABC, abstractmethod
from bitarray import bitarray
import os
import string
import logging
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Initialize logging
logging.basicConfig(filename='encryption.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Encryption Schemes
class EncryptionScheme(ABC):
    @abstractmethod
    def encrypt(self, data, key):
        """Encrypt the data using the provided key."""
        pass

    @abstractmethod
    def decrypt(self, data, key):
        """Decrypt the data using the provided key."""
        pass
    
    @abstractmethod
    def get_name(self):
        """Returns the Encryption Scheme's name."""
        pass

class XOREncryption(EncryptionScheme):
    
    def __init__(self):
        self.name = "XOR"

    # data and key are bit arrays with same length
    def encrypt(self, data, key):
        result = bitarray()
        for bit1, bit2 in zip(data, key):
            result.append(bit1 ^ bit2)
        return result
    
    # data and key are bit arrays with same length
    def decrypt(self, data, key):
        result = bitarray()
        for bit1, bit2 in zip(data, key):
            result.append(bit1 ^ bit2)
        return result
    
    def get_name(self):
        return self.name

class DebugEncryption(EncryptionScheme):
    def __init__(self):
        self.name = "Debug"
        
    def encrypt(self, data, key):
        return data
    
    def decrypt(self, data, key):
        return data
    
    def get_name(self):
        return self.name
    
import numpy as np
class AESEncryption(EncryptionScheme):
    def __init__(self, bits=128):
        self.bits = bits
        self.name = f"AES-{bits}"
        self.results = []
        
    # data and key are bit arrays
    # using AES-CBC
    def encrypt(self, data, key):
        # return data
        # print("encrypt ", key)
        # ones = np.frombuffer(b'F' * (len(data)), dtype = np.uint8)
        # data = np.frombuffer(data, dtype = np.uint8).copy()
        # # print(len(ones), len(data))
        # data = (data^ones).tobytes()
        # return data
        # data = np.frombuffer(data, dtype = np.uint8)
        # key = np.frombuffer(key * (len(data)//len(key)), dtype = np.uint8)
        # data = (data^key).tobytes()
        # return data
        # return data[len(data)//2:] + data[:len(data)//2]
        # key = bitarray([i % 2 for i in range(128)]).tobytes()
        # data = data.tobytes()
        # key = key.tobytes()
        # print("encrypt")
        cipher = AES.new(key, AES.MODE_CBC, iv=b'0'*16)
        # print("cipher: ", cipher)
        # cipheredData = cipher.encrypt(data)
        cipheredData = cipher.encrypt(pad(data, AES.block_size))
        # print("ciphered data: ", cipheredData)
        # result_data = bitarray()
        # result_data.frombytes(cipheredData)
        # result_iv = bitarray()
        # result_iv.frombytes(cipher.iv)
        result_data = cipheredData
        result_iv = cipher.iv
        # print("encrypted")
        return result_data
        # print("encrypted")
        # return result_iv + result_data
    
    # data and key are bit arrays
    # data contains iv and encrypted data
    def decrypt(self, data, key):
        # return data
        # print("decrypt ", key)
        # ones = np.frombuffer(b'F' * (len(data)), dtype = np.uint8)
        # data = np.frombuffer(data, dtype = np.uint8).copy()
        # data = (data^ones).tobytes()
        # return data
        # data = np.frombuffer(data, dtype = np.uint8)
        # key = np.frombuffer(key * (len(data)//len(key)), dtype = np.uint8)
        # data = (data^key).tobytes()
        # return data
        # data = [data[i:i+len(key)]^key for i in range(0, len(data), len(key))]
        # return data
        # return data[len(data)//2:] + data[:len(data)//2]
        # key = bitarray([i % 2 for i in range(128)]).tobytes()
        # key = key.tobytes()
        # print("recv")
        # iv = data[:16] #iv always has 128 bits
        iv = b'0'*16
        # cipheredData = data[16:]
        cipheredData = data
        # print("to", str(iv), len(cipheredData))
        # print("ciphered data: ", len(cipheredData))
        # iv = iv.tobytes()
        # cipheredData = cipheredData.tobytes()
        # print("recv")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # print("cipher: ", cipher)
        # print("cipher: ", cipher)
        # print("deciphered data: ", len(cipher.decrypt(cipheredData)))
        # originalData = cipher.decrypt(cipheredData)
        decrypted = cipher.decrypt(cipheredData)
        # print("decrypted: ", decrypted)
        # print("decrypted: ", len(decrypted), decrypted[-16:])
        decrypted = unpad(decrypted, AES.block_size)
        # print("original data: ", len(originalData))
        # print("original data: ", len(originalData))
        # result = bitarray()
        # result.frombytes(originalData)
        result = decrypted
        # print("done")
        return result
    
    def get_name(self):
        return self.name

class EncryptionFactory:
    def create_encryption_scheme(self, type) -> EncryptionScheme:
        if type == "AES":
            return AESEncryption()
        elif type == "XOR":
            return XOREncryption()
        elif type == "DEBUG":
            return DebugEncryption()
        else:
            raise ValueError("Invalid encryption scheme type")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
# Key Generation

class KeyGenerator(ABC):
    
    @abstractmethod
    def generate_key(self, *args, **kwargs):
        """Generate a key, either randomly or preset."""
        pass

    @abstractmethod
    def get_key(self):
        """Return the generated key."""
        pass
    
class DebugKeyGenerator(KeyGenerator):
    def __init__(self):
            self.key: bitarray = bitarray()
            self.key_length = 0
            
    def speficied_keylength(self, length):
        self.key_length = length
        # Default debug key is alternating 1 and 0
        self.key = bitarray([i % 2 for i in range(self.key_length)])
        
    def specified_key(self, key):
        bit_array = bitarray()
        if type(key) == bitarray:
            bit_array = key
            logger.log(f"Now using key ${key}")
        elif type(key) == string:
            encoded_bytes = key.encode('utf-8')
            bit_array.frombytes(encoded_bytes)
        else:
            logger.error("")
            raise ValueError("Error, only bitarray or string allowed")
        self.key = bit_array
        self.length = len(key)
        
    def generate_key(self, key = None, key_length = 0):
        if key is not None:
            self.specified_key(self, key)
            
        elif key_length != 0:
            self.speficied_keylength(key_length)
        
        else:
            raise ValueError("Invalid parameters")
        
    def get_key(self):
        return self.key
    
class RandomKeyGenerator(KeyGenerator):
    def __init__(self, key_length = 0):
        self.key_length = key_length
        self.key: bitarray = None
        
    def generate_key(self, key_length = 0):
        if key_length:
            self.key_length = key_length
        elif self.key_length < 1:
            logger.error(f"Try to make key of length {key_length}")
            raise ValueError("Error, please make key length nonzero")
        self.key = bitarray([int(b) for b in format(int.from_bytes(os.urandom((self.key_length + 7) // 8), 'big'), f'0{self.key_length}b')[:self.key_length]])

    def get_key(self):
        return self.key

class KeyGeneratorFactory:

    def create_key_generator(self, type) -> KeyGenerator:
        if type == "DEBUG":
            return DebugKeyGenerator()
        elif type == "RANDOM":
            return RandomKeyGenerator()
        else:
            raise ValueError("Invalid encryption scheme type")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class KeyExchange(ABC):

    @abstractmethod
    def get_key(self):
        """Generate a key for exchange."""
        pass
    
    @abstractmethod
    def send_key(self):
        """Send the generated key."""
        pass
        
