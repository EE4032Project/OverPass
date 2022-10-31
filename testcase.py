import random

# [len a,len b, size alphabet]

test_case_param = [ [40,90,30], [40,90,30], [40,90,30], [40,90,30], [40,90,30], [40,90,30] ]

def testcase(A_len,B_len, alphabet_size):
    if alphabet_size > 52:
        alphabet_size = 52

    random.seed(20)
    alphabet = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".upper()
    alphabet = alphabet[:alphabet_size]
    A = random.choices(alphabet,k=A_len)
    B = random.choices(alphabet,k=B_len)

    return ''.join(A), ''.join(B)

def get_testcase(i):
    i = i % len(test_case_param)
    return testcase(test_case_param[i][0],test_case_param[i][1],test_case_param[i][2])
    
