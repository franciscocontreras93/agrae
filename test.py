import matplotlib as mpl
import matplotlib.pyplot as plt



x = range(10)
y = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

fig, ax = plt.subplots()

plt.axhline(y=2, color='r', xmin=0, xmax=10)
plt.show()
