import pickle
import socket
import json
import base64
import struct
from typing import Set
from utils import (H1, H2, diffie_hellman_key_agreement, encode_group_element, permutation_mapping, H3)
from poly import fast_modular_interpolation
import sys
import time
import gmpy2
from gmpy2 import mpz

class Receiver:
    def __init__(self, set_Y: Set[str]):
        """
        Initialize Receiver with set Y
        """
        self.set_Y = set_Y
    
    def save_state(self, filename: str = "receiver_state.pkl"):
        """
        Save receiver state for later use
        """
        state = {
        "set_Y": self.set_Y,
        }
        with open(filename, "wb") as f:
            pickle.dump(state, f)
        
    
    @classmethod
    def load_state(cls, filename: str = "receiver_state.pkl"):
        """
        Load receiver state from file
        """
        with open(filename, "rb") as f:
            state = pickle.load(f)
        return cls(set_Y=state["set_Y"])
    
    def run_protocol(self, host: str = 'localhost', port: int = 65432):
        """
        Run the PSI protocol as the Receiver
        """
        # Connect to sender
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(1)
            conn, addr = s.accept()
            with conn:

                # Step 2
                data_size = struct.unpack('!I', conn.recv(4))[0]
                data = conn.recv(data_size)
                message = json.loads(data.decode('utf-8'))
                self.m = str(message['m'])

                # Step 3 
                self.b_set = [0] * len(self.set_Y)
                self.encode_perm_set = [0] * len(self.set_Y)
                hashed_set_Y = [0] * len(self.set_Y)
                for i in range(len(self.set_Y)):
                    while True:
                        b_i, m_i = diffie_hellman_key_agreement(self.g, self.q, self.p)
                        m_i_encoded_bitstring = encode_group_element(m_i, self.p, self.u)
                        m_i_perm = permutation_mapping(m_i_encoded_bitstring, self.key, self.iv)
                        if int(m_i_perm,2) < self.p:
                            break
                    self.b_set[i] = b_i
                    self.encode_perm_set[i] = m_i_perm
                for i in range(len(self.set_Y)):
                    hashed_set_Y[i] =  H1(self.set_Y[i])

                # Step 4
                encode_perm_set_as_int = [int(x, 2) for x in self.encode_perm_set]

                testTime = time.time()

                self.Poly = fast_modular_interpolation(hashed_set_Y, encode_perm_set_as_int, self.p)

                teststoptime = time.time()
                elapsed = teststoptime - testTime
                print("time for fast_modular_interpolation: ", elapsed)
                
                print(f"Receiver made Polynomial\n")
                sys.set_int_max_str_digits(0)
                P_as_str = [str(f) for f in self.Poly]
                m_json = json.dumps(P_as_str).encode('utf-8')
                conn.sendall(struct.pack('!I', len(m_json)))
                conn.sendall(m_json)
                
                #step 6
                data_size = struct.unpack('!I', conn.recv(4))[0]
                data = conn.recv(data_size)
                message = json.loads(data.decode('utf-8'))
                self.K = [base64.b64decode(b) for b in message['K']]
                # print(f"Receiver's K: {self.K}")

                # Step 7
                print(f"Starting to compute the Comparison\n")
                self.Output = []
                for i in range(len(self.set_Y)):
                    g_a_b = gmpy2.powmod(mpz(int(self.m, 2)), mpz(self.b_set[i]), mpz(self.p))
                    g_a_b_as_bitstring = format(g_a_b, '02048b')
                    kA_key2 = H3((g_a_b_as_bitstring))
                    H_2 = H2(self.set_Y[i], kA_key2)
                    if H_2 in self.K:
                        self.Output.append(self.set_Y[i])
                print(f"Receiver's Output: {self.Output}")
                           
