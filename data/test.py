
import pandas as pd

dataset = 'CrossingTraffic'
df = pd.read_csv(f"{dataset}/{dataset}.tsv", sep='\t')
data = df.values

count = 0


rewards = data[:,-1]

from collections import Counter

freq = Counter(rewards)

print(freq)


for x in data:
	if x[-1] == -4:
		print(x)