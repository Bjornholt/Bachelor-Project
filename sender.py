import pickle
import socket
import json
from fractions import Fraction
import struct
import base64
from typing import Set
from utils import (H1, H2, diffie_hellman_key_agreement, recv_all, inverse_permutation, shuffle_list, decode_group_element, H3)
from poly import evaluate
import base64
import time
import gmpy2
from gmpy2 import mpz


class Sender:
    def __init__(self, set_X: Set[str]):
        """
        Initialize Sender with set X
        """
        self.set_X = set_X
        
    def save_state(self, filename: str = "sender_state.pkl"):
        """
        Save sender state for later use
        """
        state = {
            'set_X': self.set_X,
            'params': self.params
        }
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
    
    @classmethod
    def load_state(cls, filename: str = "sender_state.pkl"):
        """
        Load sender state from file
        """
        with open(filename, 'rb') as f:
            state = pickle.load(f)
        
        sender = cls(state['set_X'])
        sender.params = state['params']
        
        return sender
    
    def start_protocol(self, host: str = 'localhost', port: int = 65432):
        a, m = diffie_hellman_key_agreement(self.g, self.q, self.p)
        self.a = a
        self.a = format(self.a, '02048b')
        self.m = format(m, '02048b')
    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            runningTime = time.time()
            # Send public key g^a mod p = m
            m = {'m': self.m}
            m_json = json.dumps(m).encode('utf-8')
            s.sendall(struct.pack('!I', len(m_json)))
            s.sendall(m_json)
            print(f"Sender sent m\n")

            #Step 4
            size = struct.unpack('!I', recv_all(s, 4))[0]
            data = recv_all(s, size)
            P_as_str = json.loads(data.decode('utf-8'))
            self.Poly = [Fraction(f) for f in P_as_str]
        
            #Step 5
            self.K = [0] * len(self.set_X)

            Hashedset = [0] * len(self.set_X)
            for i in range(len(self.set_X)):
                Hashedset = [H1(x) % self.p for x in self.set_X]

            start = time.time()
            polyset = evaluate(self.Poly, Hashedset, self.p)
            end = time.time()
            print("This is the time for the eval function", end-start)

            for i in range(len(self.set_X)):
                P_h1_xi = polyset[i]
                P_h1_xi = (int(P_h1_xi) * 1) % self.p
                P_h1_xi_as_bitstring = format(int(P_h1_xi), '02048b')
                inverse_perm_P_h1_xi = inverse_permutation(P_h1_xi_as_bitstring, self.key, self.iv)
                inverse_perm_P_h1_xi_as_int = int(inverse_perm_P_h1_xi, 2)
                inverse_perm_P_h1_xi_as_int_mod_p = inverse_perm_P_h1_xi_as_int % self.p
                inverse_perm_P_h1_xi_as_int_mod_p_as_bitstring = format(inverse_perm_P_h1_xi_as_int_mod_p, '02048b') 
                inverse_perm_P_h1_xi_as_int = int(inverse_perm_P_h1_xi_as_int_mod_p_as_bitstring, 2)
                decoded_inverse_perm_P_h1_xi_as_fieldarray = decode_group_element(inverse_perm_P_h1_xi_as_int, self.p, self.q, self.u)
                decoded_inverse_perm_P_h1_xi_as_bitstring = format(decoded_inverse_perm_P_h1_xi_as_fieldarray, '02048b')
                decoded_inverse_perm_P_h1_xi_as_int = int(decoded_inverse_perm_P_h1_xi_as_bitstring, 2) 
                g_b_a = gmpy2.powmod(mpz(decoded_inverse_perm_P_h1_xi_as_int), mpz(a), mpz(self.p))
                g_b_a_as_bitstring = format(g_b_a, '02048b')
                k_i = H3(g_b_a_as_bitstring)
                k_i_prime = H2(self.set_X[i], k_i)
                self.K[i] = k_i_prime

            # Step 6    
            self.K = shuffle_list(self.K)
            encoded_K = [base64.b64encode(k).decode('utf-8') for k in self.K]
            k_json = json.dumps({"K": encoded_K}).encode('utf-8')

            s.sendall(struct.pack('!I', len(k_json)))
            s.sendall(k_json)
            end_time = time.time()  # Record the end time
            elapsed_time = end_time - runningTime
            print("-------------------------")
            print("Communication + calculation time: ", elapsed_time)
            print("-------------------------")

