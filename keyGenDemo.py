# Alexander Penney 2020 
''' Implementing DSA keyPair generation with user selection of:
1. Hash Function (H), 2. Key Length (L), 3. modulus length (N), 5. g paramater
''' 
import random, hashlib, time

keyLengths = [64*(2**i) for i in range(4)]


# TODO implement https://en.wikipedia.org/wiki/AKS_primality_test
def isPrime(n):
    if n%2 == 0 or n < 2:
        return False
    maxFact = round(n**0.5)
    for fact in range(3, maxFact + 1, 2):
        if n%fact == 0:
            return False
    return True


# generates a random prime number q where 2^(N-1) < q < 2^N
def getNBitPrime(N):
    while True:
        q = random.getrandbits(N)
        # make first bit a 1 with mask to ensure we have an N-bit number
        q |= (1 << N-1)
        if isPrime(q):
            return q


def genKeyPair(H, L):
    assert(L in keyLengths)
    hashL = 256
    N = random.randint(0, min(L, hashL))
    q = getNBitPrime(N)
    p = getpPrime(q)

