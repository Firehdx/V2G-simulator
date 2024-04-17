import numpy as np

a = np.array([1,2,3,4,-1,-2,-3,0])

b = np.sum(a>=0)

print(b)
print(a[1:])