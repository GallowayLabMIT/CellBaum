import pandas as pd
import matplotlib.pyplot as plt
import seaborn

well_list = ['XY01', 'XY02', 'XY03', 'XY04']
type_list = ['None', '6F', '6FDD', '6FDDRR']
data = {}
dir = "/Users/ConradOakes/Desktop/Galloway_2021/btrack_results"

for well in range(len(well_list)):
    data[type_list[well]] = pd.read_csv(dir + '/'+well_list[well]+'_velocity.csv')['velocity']

data = pd.DataFrame(data)
fig, axes = plt.subplots()
violin = seaborn.violinplot(data = data)
violin.set(ylabel = 'Velocity')
plt.show()
