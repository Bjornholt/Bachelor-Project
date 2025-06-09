import random
import hashlib
import sympy
import secrets
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Util.number import getPrime, isPrime
import gmpy2
from gmpy2 import mpz



def generate_safe_prime() -> Tuple[int, int, int, int, int]:
    """
    Generate a safe prime p = 2q + 1 where q is also prime
    Return (p, q, g, u) where:
    - p is the safe prime
    - q is the prime such that p = 2q + 1
    - g is a generator of the subgroup of order q
    - u is an element such that u^q ≠ 1 (mod p)
    """
    while True:
        q = getPrime(2047)
        p = 2*q + 1

        if isPrime(p):
            g, h = find_generator(p, q)
            u = find_non_subgroup_element(p, q)
            return p, q, h, g, u

def find_generator(p: int, q: int) -> Tuple[int, int]:
    """
    Find a generator g of the subgroup of order q in Z_p*
    This means g^q ≡ 1 (mod p) and g ≠ 1
    """
    while True:
        h = secrets.randbelow(p-1)+1
        g = gmpy2.powmod(mpz(h), mpz(2), mpz(p))
        if g != 1 and gmpy2.powmod(mpz(h), mpz(q), mpz(p)) != 1 and gmpy2.powmod(mpz(g), mpz(q), mpz(p)) == 1:
            return g, h


def find_non_subgroup_element(p: int, q: int) -> int:
    """
    Find an element u in Z_p* such that u^q ≠ 1 (mod p)
    """
    while True:
        u = random.randint(2, p-2)
        if gmpy2.powmod(mpz(u), mpz(q), mpz(p)) != 1:
            return u

        

def check_params(list: list) -> bool:
    """
    Check if the parameters are valid
    """
    if len(list) != 7:
        print("Invalid number of parameters")
        return False
    
    p = int(list['p'])
    q = int(list['q'])
    g = int(list['g'])
    h = int(list['h'])
    u = int(list['u'])
    
    if not (isinstance(p, int) and isinstance(q, int) and isinstance(g, int) and isinstance(u, int)):
        print("Invalid parameter types")
        return False
    if p <= 0 or q <= 0 or g <= 0 or u <= 0:
        return False
    if not (sympy.isprime(p) and sympy.isprime(q)):
        return False
    if not gmpy2.powmod(mpz(g), mpz(q), mpz(p)) == 1 and gmpy2.powmod(mpz(h), mpz(q), mpz(p)) != 1 and g != 1:
        return False
    return True
        
def H3(data: str) -> int:
    """
    Random oracle H₁: {0,1}* → F
    Maps arbitrary strings to field elements
    """
    hash_bytes = hashlib.sha256(data.encode('utf-8')).digest()
    return int.from_bytes(hash_bytes, byteorder='big')+1



def H1(data: str) -> int:
    """
    Random oracle H₁: {0,1}* → F
    Maps arbitrary strings to field elements
    """
    hash_bytes = hashlib.sha256(data.encode('utf-8')).digest()
    return int.from_bytes(hash_bytes, byteorder='big')

def H2(x: str, k: int) -> bytes:
    """
    Random oracle H₂: {0,1}* × F → {0,1}^256
    Maps a string and a field element to a 256-bit string
    """
    data = f"{x}:{k}".encode('utf-8')
    return hashlib.sha256(data).digest()

def encode_group_element(x: int, p: int, u: int) -> str:
    """
    Encode a group element as a byte string with the special encoding
    With probability 1/2, map x to x
    With probability 1/2, map x to u*x mod p
    """
    if secrets.randbelow(2) == 0:
        value = x % p
    else: 
        value = (u*x) % p
    return format(value, '02048b')

def decode_group_element(encoded: int, p: int, q: int, u: int) -> int:
    """
    Decode a byte string back to a group element
    """
    z = encoded
    if z < 1 or z >= p:
        raise ValueError("Invalid encoding")

    if gmpy2.powmod(mpz(z), mpz(q), mpz(p)) == 1:
        return z
    else:
        return (int(gmpy2.invert(mpz(u), mpz(p))) * z) % p


def permutation_mapping(x_bitstring: str, key: bytes, iv: bytes) -> str:
    x_bytes = bitstring_to_bytes(x_bitstring)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(x_bytes)
    encrypted_data_as_bitstring = format(int.from_bytes(encrypted_data, 'big'), '02048b')
    return encrypted_data_as_bitstring

def inverse_permutation(encrypted_bitstring: str, key: bytes, iv: bytes) -> str:
    encrypted_bytes = bitstring_to_bytes(encrypted_bitstring)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_bytes)
    decrypted_data_as_bitstring = format(int.from_bytes(decrypted_data, 'big'), '02048b')
    return decrypted_data_as_bitstring

def diffie_hellman_key_agreement(g: int, p: int) -> Tuple[int, int]:
    """
    Generate Diffie-Hellman key pair (private_key, public_key)
    """
    private_key = random.randint(2, p-2)
    public_key = gmpy2.powmod(mpz(g), mpz(private_key), mpz(p))
    return private_key, public_key


def recv_all(sock, n):
    """Modtag præcis n bytes fra socketten."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Forbindelsen blev lukket uventet")
        data += packet
    return data


def shuffle_list(lst):
    shuffled = lst[:]  
    random.shuffle(shuffled)
    return shuffled

def assign_real_values(sender_instance, receiver_instance, parameters):
    p, q, h, g, u = parameters
    sender_instance.p = p
    sender_instance.q = q
    sender_instance.h = h
    sender_instance.g = g
    sender_instance.u = u
    receiver_instance.p = p
    receiver_instance.q = q
    receiver_instance.h = h
    receiver_instance.g = g
    receiver_instance.u = u
    return sender_instance, receiver_instance

def load_from_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    values = {}
    for line in lines:
        if ':' in line:
            key, value = line.strip().split(':', 1)
            values[key.strip()] = int(value.strip())

    expected_keys = ['p', 'q', 'h', 'g', 'u']
    if not all(k in values for k in expected_keys):
        raise ValueError(f"Filen mangler én eller flere nødvendige værdier: {expected_keys}")

    return values['p'], values['q'], values['h'], values['g'], values['u']


def is_smaller_than_p512(x: int):
    if x <= (2**512)-1:
        return True
    else:   
        return False

def bitstring_to_bytes(s):
    s = s.zfill((8 - len(s) % 8) % 8 + len(s))
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')

    

