import random

def gen_input(N: int, fileName = None):
  # S, T
  # K
  # b_k
  # ...
  # N
  # 1 size arrival_time processing_time weight
  # ...

  # size random 1 -> 50
  # arrival_time random 1 -> 50
  # processing_time random(1-10) + int(random(0.5, 1)*size)
  # weight random(1,5)

  # S random(10, sum(size)/2)
  # T max 9999
  # b_1 = max(size)
  # b_i = b_1 + random(1, max(size))
  # K = count(i)

  sizes = []
  arrival_times = []
  processing_times = []
  weights = []

  for _ in range(N):
    sizes.append(random.randint(1,50))
    arrival_times.append(random.randint(1,50))
    weights.append(random.randint(1,5))
  
  for i in range(N):
    processing_times.append(random.randint(1,10) + int(random.random()*sizes[i]))
  
  sumSizes = sum(sizes)
  maxSizes = max(sizes)

  S = random.randint(maxSizes, int(sumSizes/2))
  T = 9999
  blocks = []
  bTemp = 0
  while bTemp < S:
    if bTemp == 0:
      if maxSizes < S:
        blocks.append(maxSizes)
        bTemp = bTemp + maxSizes
      else:
        break
    else:
      value = bTemp + random.randint(1, maxSizes - 1)
      if value < S:
        blocks.append(value)
        bTemp = bTemp + value
      else:
        break
  K = len(blocks)

  # print(S, T)
  # print(K)
  # for i in range(K):
  #   print(blocks[i])
  # print(N)
  # for i in range(N):
  #   print(i+1, sizes[i], arrival_times[i], processing_times[i], weights[i])

  if fileName:
    with open(fileName, "w") as f:
      f.write("{S} {T}\n".format(S=S, T=T))
      f.write("{K}\n".format(K=K))
      for i in range(K):
        f.write("{block}\n".format(block=blocks[i]))
      f.write("{N}\n".format(N=N))
      for i in range(N):
        f.write("{id} {size} {arrival_time} {processing_time} {weight}\n".format(id=i+1, size=sizes[i], arrival_time=arrival_times[i], processing_time=processing_times[i], weight=weights[i]))
if __name__ == "__main__":
  for i in range(50):
    fileName = "input/input-{num:02d}.txt".format(num=i+1)
    N = i + 11
    gen_input(N, fileName)
  
  for i in range(50,60):
    fileName = "input/input-{num:02d}.txt".format(num=i+1)
    N = i + 101
    gen_input(N, fileName)