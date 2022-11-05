import sys
import trace
import threading
import time
import os
import fcntl


import random

# [len a,len b, size alphabet]

test_case_param = [ [40,90,30], [2000,500,15], [100000,100000,50], 
                    [999999,22222,40],[100,50000,30], [4000, 200, 3] ]

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
    


# https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
class thread_with_trace(threading.Thread):
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False
 
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run     
    threading.Thread.start(self)
 
  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
 
  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None
 
  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace
 
  def kill(self):
    self.killed = True


class lock:
  @staticmethod
  def acquire(lock_file):
      open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
      fd = os.open(lock_file, open_mode)

      pid = os.getpid()
      lock_file_fd = None
      
      timeout = 5.0
      start_time = current_time = time.time()
      while current_time < start_time + timeout:
          try:
              # The LOCK_EX means that only one process can hold the lock
              # The LOCK_NB means that the fcntl.flock() is not blocking
              # and we are able to implement termination of while loop,
              # when timeout is reached.
              # More information here:
              # https://docs.python.org/3/library/fcntl.html#fcntl.flock
              fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
          except (IOError, OSError):
              pass
          else:
              lock_file_fd = fd
              break
          print(f'  {pid} waiting for lock')
          time.sleep(1.0)
          current_time = time.time()
      if lock_file_fd is None:
          os.close(fd)
      return lock_file_fd

  @staticmethod
  def release(lock_file_fd):
      # Do not remove the lockfile:
      #
      #   https://github.com/benediktschmitt/py-filelock/issues/31
      #   https://stackoverflow.com/questions/17708885/flock-removing-locked-file-without-race-condition
      fcntl.flock(lock_file_fd, fcntl.LOCK_UN)
      os.close(lock_file_fd)
      return None


class OverPassException(Exception):
    def __init__(self, _type="py",_message="OverPassError"):
        self.message = _message
        self.type = _type
        super().__init__(self.message)

    def __str__(self):
        return f'OverPassError: {self.type} -> {self.message}'

