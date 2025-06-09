from utils import generate_safe_prime, permutation_mapping, inverse_permutation, assign_real_values, load_from_file, is_smaller_than_p512, encode_group_element, decode_group_element, diffie_hellman_key_agreement
# interpolate_polynomial, evaluate_polynomial,
import receiver
import time
import threading
import sender
import galois
from Crypto.Random import get_random_bytes
import base64
import math
import string
import random

def test(fn):
    def wrapper():
        try:
            fn()
            print(f"✅ {fn.__name__} passed")
        except AssertionError as e:
            print(f"❌ {fn.__name__} failed: {e}")
    return wrapper

@test
def test_generate_safe_prime_function(): 
     # Test the generate_safe_prime function    
     # Generate a safe prime
     p, q, h, g, u = generate_safe_prime()
     print(f"Generated safe prime p: {p}")
     print(f"Generated prime q: {q}")
     print(f"Generator g: {g}")

@test
def permutation_test(): 
    # Original list
    original_list = ["apple", "banana", "grape", "lemon", "orange"]
    # Get the permutation mapping
    perm = permutation_mapping(len(original_list))
    # Apply the permutation to the original list
    permuted_list = [original_list[i] for i in perm]
    # Get the inverse permutation
    inverse_perm = inverse_permutation(perm)
    # Apply the inverse permutation to the permuted list
    restored_list = [permuted_list[i] for i in inverse_perm]
    # Check if the restored list matches the original list
    assert restored_list == original_list, "Test failed: Restored list does not match the original list"
  
    
def initialize(sender_set, receiver_set, filename=None):
    global receiver_data, sender_data

    # Create sender and receiver instances
    sender_instance = sender.Sender(sender_set)
    receiver_instance = receiver.Receiver(receiver_set)

    if filename is None:
        sender_instance, receiver_instance = assign_real_values(sender_instance, receiver_instance, generate_safe_prime())
    else:
        # Load sender and receiver state from file
        sender_instance, receiver_instance = assign_real_values(sender_instance, receiver_instance, load_from_file(filename))

    key = get_random_bytes(32)
    iv = get_random_bytes(16)
    receiver_instance.iv = iv
    sender_instance.iv = iv
    receiver_instance.key = key
    sender_instance.key = key

    # Start timing
    start_time = time.time()

    # Start the receiver in a thread first (because it needs to bind and listen)
    def run_receiver():
        receiver_instance.run_protocol(host="localhost", port=65432)

    receiver_thread = threading.Thread(target=run_receiver)
    receiver_thread.start()

    # Give the receiver a second to start up
    time.sleep(1)

    # Start sender
    sender_instance.start_protocol(host="localhost", port=65432)

    receiver_thread.join()

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total protocol runtime: {elapsed_time:.2f} seconds")

    return sender_instance, receiver_instance


@test
def testProtocolStepByStep():   
    # Test the protocol step by step with a small set of strings
    sender_set = ["hej", "hallo"]
    receiver_set = ["hej", "Hallo"]
    sender_instance, receiver_instance = initialize(sender_set,receiver_set)

    
@test
def test_with_set_of_4():
    sender_set = ["30202", "30203", "30204", "30205"]
    receiver_set = ["30205", "30206", "30207", "30208"]
    sender_instance, receiver_instance = initialize(sender_set,receiver_set, 'dummy_2048')
    assert receiver_instance.Output == ["30205"]

@test
def test_with_set_of_10():
    sender_set= ['apple', 'banana', 'cherry', 'date', 'elephant', 'fox', 'grape', 'hat', 'ice', 'jug']
    receiver_set = ['apple', 'banana', 'cherry', 'date', 'kite', 'lemon', 'mango', 'nut', 'orange', 'pear']
    sender_instance, receiver_instance = initialize(sender_set,receiver_set)
    assert receiver_instance.Output == ['apple', 'banana', 'cherry', 'date']

@test
def test_with_set_of_50():
    shared = ["hej", "hello", "hallo", "hi", "water", "sun"]
    sender_unique = [
        "apple", "banana", "cherry", "dog", "elephant", "fox", "grape", "house", "ice", "jump",
        "kite", "lemon", "mango", "nut", "orange", "pear", "queen", "rabbit", "tree",
        "umbrella", "violin", "xylophone", "yacht", "zebra", "ant", "bear", "cat", "duck",
        "eagle", "frog", "goat", "horse", "iguana", "jellyfish", "koala", "lion", "monkey", "newt",
        "owl", "penguin", "quail", "rhino", "snake", "tiger"
    ]
    receiver_unique = [
        "blue", "red", "green", "yellow", "black", "white", "purple", "pink", "brown", "gray",
        "gold", "silver", "copper", "brass", "steel", "iron", "wood", "glass", "plastic", "paper",
        "rock", "sand", "fire", "earth", "wind", "rain", "snow", "moon",
        "star", "cloud", "storm", "light", "dark", "shadow", "sunset", "sunrise", "dawn", "dusk",
        "morning", "night", "evening", "noon", "midnight", "twilight"
    ]
    sender_set = shared + sender_unique 
    receiver_set = shared + receiver_unique
    sender_instance, receiver_instance = initialize(sender_set,receiver_set)
    assert receiver_instance.Output == shared

@test
def test_with_set_of_100():
    shared = ["hej", "hello", "hallo", "hi", "water", "sun", "grape", "kiwi", "lemon", "mango"]
    sender_unique = [
        "apple", "banana", "cherry", "dog", "elephant", "fox", "grape", "house", "ice", "jump",
        "kite", "lemon", "mango", "nut", "orange", "pear", "queen", "rabbit", "tree",
        "umbrella", "violin", "xylophone", "yacht", "zebra", "ant", "bear", "cat", "duck",
        "eagle", "frog", "goat", "horse", "iguana", "jellyfish", "koala", "lion", "monkey", "newt",
        "owl", "penguin", "quail", "rhino", "snake", "tiger", "unicorn", "vulture", "walrus", "yak",
        "zucchini", "avocado", "beet", "carrot", "daikon", "eggplant", "fig", "guava", "honeydew",
        "jackfruit", "kiwi", "lychee", "mushroom", "nectarine", "okra", "papaya", "quince", "radish",
        "spinach", "tomato", "ugli", "vanilla", "watermelon", "yam", "zinnia", "almond", "basil",
        "cinnamon", "dill", "elderberry", "fennel", "ginger", "hazelnut", "iris", "jasmine", "kale"
        "lavender", "mint", "nutmeg", "oregano", "parsley", "quinoa", "br   ownie"
    ]
    receiver_unique = [
        "blue", "red", "green", "yellow", "black", "white", "purple", "pink", "brown", "gray",
        "gold", "silver", "copper", "brass", "steel", "iron", "wood", "glass", "plastic", "paper",
        "rock", "sand", "fire", "earth", "wind", "rain", "snow", "moon",
        "star", "cloud", "storm", "light", "dark", "shadow", "sunset", "sunrise", "dawn", "dusk",
        "morning", "night", "evening", "noon", "midnight", "twilight", "amber", "beige", "cyan",
        "denim", "emerald", "fuchsia", "goldenrod", "honey", "indigo", "jade", "khaki", "lavender",
        "magenta", "navy", "olive", "peach", "quartz", "rose", "sapphire", "teal", "umber", 
        "violet", "wheat", "xanadu", "yellowgreen", "zinnwaldite", "aqua", "burgundy", "chartreuse",
        "denimblue", "eggshell", "forestgreen", "grapevine", "hotpink", "ivory", "jetblack", "kellygreen",
        "jelly", "potato", "love", "cabbage", "egg", "slope", "grapefruit", "honeycomb", "jalapeno",
    ]
    sender_set = shared + sender_unique 
    receiver_set = shared + receiver_unique
    if len(sender_set) != len(receiver_set):
        print(f"Sender set: {len(sender_set)}")
        print(f"Receiver set: {len(receiver_set)}")
        raise ValueError("Sender and receiver sets must be of the same length")
    else:
        sender_instance, receiver_instance = initialize(sender_set,receiver_set)
    assert receiver_instance.Output == shared



def generate_random_string(min_length=5, max_length=15):
    """Generate a random string of letters and digits"""
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_string_set(size, min_length=5, max_length=15):
    """Generate a set of 'size' unique random strings"""
    result = set()
    while len(result) < size:
        result.add(generate_random_string(min_length, max_length))
    return list(result)

@test
def test_with_set_of_generated_100():
    # Generate a set of 100 unique random strings
    set_size = 90
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = ["hej", "hello", "hallo", "hi", "water", "sun", "grape", "kiwi", "lemon", "mango"]
    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared)
    assert receiver_instance.Output == shared

@test
def test_with_set_of_generated_500():
    # Generate a set of 100 unique random strings
    set_size = 490
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = ["hej", "hello", "hallo", "hi", "water", "sun", "grape", "kiwi", "lemon", "mango"]
    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_1000():
    # Generate a set of 1000 unique random strings
    
    set_size = 990
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = ["hej", "hello", "hallo", "hi", "water", "sun", "grape", "kiwi", "lemon", "mango"]
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_2000():
    # Generate a set of 2000 unique random strings
    set_size = 1980
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = generate_string_set(20)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_4000():
    # Generate a set of 2000 unique random strings
    set_size = 3960
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = generate_string_set(40)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_8000():
    # Generate a set of 2000 unique random strings
    set_size = 7950
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = generate_string_set(50)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared


@test
def interpolation():
    print(len(str(abs(10045172038642792519194899047285160601565368456073133209466952779017022558081914274258054264320750137134679851423441453915544836303146939272165637681575719))))
    x = [70687216502068564285822632352004536373559744002011958957835951508101042365370]
    y = [9403137467230145052615671497056784287107063961864631483277844974091845818545804586658882163254806331005239279625294449060465904580547416460638848665643039]  
    coeffs = interpolate_polynomial(x, y)
    print(f"This is x: {x}")
    print(f"Coefficients: {coeffs}")
    print(evaluate_polynomial(coeffs, 7068721650206856428582263235200453637355974400201195895783595150810104236537070687216502068564285822632352004536373559744002011958957835951508101042365370))

    assert evaluate_polynomial(coeffs, 7068721650206856428582263235200453637355974400201195895783595150810104236537070687216502068564285822632352004536373559744002011958957835951508101042365370) == 9403137467230145052615671497056784287107063961864631483277844974091845818545804586658882163254806331005239279625294449060465904580547416460638848665643039
    


@test
def test_galois():
    p, q, h, g, u = generate_safe_prime()
    poly = galois.primitive_poly(2, 513)
    GF = galois.GF(2**int(math.log2(p)+1), irreducible_poly=poly)
    print(p)
    print("+++++++++++++++++++++++")
    a= GF(p)
    bitstring = format(a, '02048b')
    print(bitstring)
    

@test
def testProtocolStepByStepWithDummy():
     sender_set = ["hej"]
     receiver_set = ["Hej"]
     sender_instance, receiver_instance = initialize(sender_set,receiver_set, 'dummy_1')
    


@test
def test_load_from_file():
    p, q, h, g, u = load_from_file('dummy_1')
    print(p,"\n")
    print(q,"\n")
    print(h,"\n")
    print(g,"\n")
    print(u,"\n")


@test
def test_real_perm():
     x = "100011000101111010100110101000000001000110010011000100000111000110010011110111011001011011011010010101000010001111111001010110010001011101001110100110001000010101010101000101110110001011011111010111100011011100000100100010010010010010101110011001111100101001111101011101111001010111000010000110111010110101110000011011111001111010100100001111011101111011001011101000001010101011001000101001001111000110100000011000011010011010101011110001100100001001010000101101110111101111000011101011100001000100111000001011100"
     print(f"Original x: {x}")
     print(len(x))
     key = get_random_bytes(32)
     iv = get_random_bytes(16)
     perm = permutation_mapping(x, key, iv)
     print(f"Permuted x: {perm}")
     is_smaller_than_p = is_smaller_than_p512(int(perm, 2))
     print(f"Is permuted x smaller than 2^512: {is_smaller_than_p}")
     original_x = inverse_permutation(perm, key, iv)
     print(f"Returned x: {original_x}")


@test
def test_encode_decode():
    p, q, h, g, u = generate_safe_prime()
    poly = galois.primitive_poly(2, 512)
    GF = galois.GF(2**int(math.log2(p)+1), irreducible_poly=poly)
    for i in range(10):
        _,m = diffie_hellman_key_agreement(g, p)
        print(f"m: {m}")
        encoded = encode_group_element(m, p, u, GF)
        int_encode = int(encoded, 2)
        print("Encoded as int: ", int_encode)
        decoded = decode_group_element(int_encode, p, q, u)
        print(f"Decoded: {decoded}")
        print(m==decoded)


# Tests for comparison to article protocol

@test
def test_with_set_of_2_to_power_7():
    # Generate a set of 2^7 unique random strings
    set_size = pow(2,7) - 10
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = generate_string_set(10)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_2_to_power_8():
    # Generate a set of 2^8 unique random strings
    set_size = pow(2,8) - 20
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = generate_string_set(20)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared


@test
def test_with_set_of_2_to_power_9():
    # Generate a set of 2^9 unique random strings
    set_size = pow(2,9) - 20
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = generate_string_set(20)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_2_to_power_10():
    # Generate a set of 2^10 unique random strings
    set_size = pow(2,10) - 20
    receiver_set = generate_string_set(set_size)
    sender_set = generate_string_set(set_size)
    shared = generate_string_set(20)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_2_to_power_12_and_8():
    # Generate a set of 2000 unique random strings
    s_set_size = pow(2,8) - 20
    r_set_size = pow(2,12) - 20
    receiver_set = generate_string_set(r_set_size)
    sender_set = generate_string_set(s_set_size)
    shared = generate_string_set(20)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

@test
def test_with_set_of_2_to_power_16_and_12():
    # Generate a set of 2000 unique random strings
    s_set_size = pow(2,12) - 20
    r_set_size = pow(2,16) - 20
    receiver_set = generate_string_set(r_set_size)
    sender_set = generate_string_set(s_set_size)
    shared = generate_string_set(20)
    print(f"Sender set: {len(sender_set+shared)}")
    print(f"Receiver set: {len(receiver_set+shared)}")
    print(receiver_set)
    print(sender_set)

    sender_instance, receiver_instance = initialize(sender_set+shared,receiver_set+shared, 'dummy_2048')
    assert receiver_instance.Output == shared

# List of tests
# test_generate_safe_prime_function()
# permutation_test()
# interpolation()
# testProtocolStepByStep()
# testProtocolStepByStepWithDummy()
# test_load_from_file()
# test_real_perm()
# test_encode_decode()
# test_with_set_of_4() 
# test_with_set_of_10() 
# test_with_set_of_50() 
# test_with_set_of_100() 
# test_with_set_of_generated_100()
# test_with_set_of_generated_500() 
# test_with_set_of_1000() # 128
# test_with_set_of_2000() # 346.24, 321.41, 63.82, 51 :OOOO  😎 
# test_with_set_of_4000() # 165.56
# test_with_set_of_8000() # 584.32

# ------------------------------------TESTS FOR ACTUAL COMPARISON------------------------------ #
# test_with_set_of_2_to_power_7() 
# Time for fast_modular_interpolation:  0.089080810546875
# This is the time for the eval function 0.04504108428955078
# Total protocol runtime: 2.33 seconds

# test_with_set_of_2_to_power_8() 
# Time for fast_modular_interpolation:  0.3333897590637207
# This is the time for the eval function 0.16715168952941895
# Total protocol runtime: 3.87 seconds

# test_with_set_of_2_to_power_9() 
# Time for fast_modular_interpolation:  1.2889537811279297
# This is the time for the eval function 0.6455965042114258
# Total protocol runtime: 7.81 seconds

# test_with_set_of_2_to_power_10() 
# Time for fast_modular_interpolation:  5.088987588882446
# This is the time for the eval function 2.5705454349517822
# Total protocol runtime: 18.91 seconds

# test_with_set_of_2_to_power_12_and_8() 
# Time for fast_modular_interpolation:  80.8332028388977
# This is the time for the eval function 1.7335879802703857
# Total protocol runtime: 105.63 seconds

# test_with_set_of_2_to_power_16_and_12() # DENNE HER KAN VÆRE MEGET LANGSOM
# MERE END 1 TIME