import matplotlib.pyplot as plt
import numpy as np

# Fixing random state for reproducibility
np.random.seed(19680801)


plt.rcdefaults()
fig, ax = plt.subplots()

# Example data
people = ('Nitrogeno', 'Fosforo', 'Potasio', 'carbonatos')
y_pos = np.arange(len(people))
performance = [9,56,21.4,13.6]
error = np.random.rand(len(people))

ax.barh(y_pos, performance, align='center')
ax.set_yticks(y_pos, labels=people)
ax.invert_yaxis()  # labels read top-to-bottom
# ax.set_xlabel('Performance')
# ax.set_title('How fast do you want to go today?')
plt.xlim([0,100])

plt.show()
