
import pandas as pd

df = pd.read_csv(f"Elevators_new.tsv", sep='\t')
data = df.values

count = 0
for x in data:
	if x[-1]> 0:
		count += 1

print(count)
