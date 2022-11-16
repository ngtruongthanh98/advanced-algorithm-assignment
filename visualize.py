from matplotlib import pyplot as plt

exec_time = []

for i in range(1, 61):
    with open(f"./new-result/result-{i:02}.txt") as f:
        exec_time.append(float(f.read().split("\n")[2].split(": ")[1]))

plt.figure()
plt.plot(range(1, 61), exec_time)
plt.show()
