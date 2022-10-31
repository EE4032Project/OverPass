
import random

# [len a,len b, size alphabet]

test_case_param = [ [40,90,30], [2000,500,15], [100000000,100000000,50], 
                    [99999999999,222222222,40],[100,50000,30], [4000, 200, 3] ]

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


for i in range(0,10):
    print(get_testcase(i))

