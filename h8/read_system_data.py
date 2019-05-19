#%%
import pandas as pd
#%%
header_names = ["time", "temperature", "power1", "power2",
                "total_power"]
#
NUM_CPU = 12

for i in range(0, NUM_CPU):
    header_names.append("cpu{0}_utilization".format(i))
    header_names.append("cpu{0}_frequency".format(i))

#%%
data = pd.read_csv("system.csv", sep=",", index_col=False, names=header_names)
#%%
