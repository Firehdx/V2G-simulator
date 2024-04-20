import numpy as np

# a = np.array([1,2,3,4,-1,-2,-3,0])

# b = np.sum(a>=0)

# print(b)
# print(a[1:])

class A:
    def __init__(self, data):
        self.data = data
    
    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

class B:
    def __init__(self) -> None:
        self.l = [A(0), A(1), A(2), A(3)]
    
    def get_data(self):
        return self.l
    
    def get_idx_data(self, idx):
        return self.l[idx].get_data()
    
b = B()
l = b.get_data()
l.append(A(4))
print(l == b.get_data())
print(l[4].get_data())
print(b.get_idx_data(4))