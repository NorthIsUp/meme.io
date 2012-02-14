import random

# Simple bijective function
#   Basically encodes any integer into a base(n) string,
#     where n is ALPHABET.length.
#   Based on pseudocode from http://stackoverflow.com/questions/742013/how-to-code-a-url-shortener/742047#742047

ALPHABET = [x for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]
ALPHABET = random.sample(ALPHABET, len(ALPHABET))
  # make your own alphabet using:
  # (('a'..'z').to_a + ('A'..'Z').to_a + (0..9).to_a).shuffle.join
BASE = len(ALPHABET)


def bijective_encode(i):
  # from http://refactormycode.com/codes/125-base-62-encoding
  # with only minor modification
    if i == 0:
        return ALPHABET[0]
    s = ''
    while i > 0:
        s += ALPHABET[i % BASE]
        i /= BASE
    return s[::-1]


def bijective_decode(s):
    i = 0
    for c in s:
        i = i * BASE + ALPHABET.index(c)
    return i

# Two little demos:

# Encoding ints, decoding them back:
# num = pow(2, 16)
# for i in xrange(num, num + 300):
#     print i, " ", bijective_encode(i), " ", bijective_decode(bijective_encode(i))
#     assert(i == bijective_decode(bijective_encode(i)))

i = "this is a long thing does it actually work like this?"
print i, " ", bijective_encode(i), " ", bijective_decode(bijective_encode(i))

# Decoding string mentioned in original SO question:
print bijective_decode("e9a")
