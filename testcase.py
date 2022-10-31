import random
def testcase(A_len,B_len, alphabet_size):
    alphabet = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".upper()
    alphabet = alphabet[:alphabet_size]
    A = random.choices(alphabet,k=A_len)
    B = random.choices(alphabet,k=B_len)

    return ''.join(A), ''.join(B)

print(testcase(10, 20,5))