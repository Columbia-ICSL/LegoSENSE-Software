import time

class ExampleLibrary:
    def __init__(self):
        pass
    
    def read_a(self):
        return time.time() * 10 % 100
    
    def read_b(self):
        return time.time() % 10
    
    def read_c(self):
        return 50 + self.read_a()
