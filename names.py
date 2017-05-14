from __future__ import print_function

import pandas as pd
import seaborn as sns
import numpy as np
import os
import re


YEAR_REG = re.compile("yob([0-9]+)\.txt")
DATA_DIR = os.path.abspath("./names_data")
NAMES = ["Arliss", "Merida", "Dodge"]

def read_babies(filename):
    babynames = pd.read_csv(os.path.join(DATA_DIR, filename),
                                header=None,
                                names=["name", "sex", "count"]).sort_values(
                                    "count", ascending=False)
    return babynames

def grab_names(filename):
    year = int(YEAR_REG.match(filename).group(1))

    babynames = read_babies(filename)

    names = map(lambda name: babynames[babynames.name == name]["count"].sum(),
                NAMES)
    # total baby population and year, respectively
    names += [babynames["count"].sum(), year]

    return names

files = [y for y in os.listdir(DATA_DIR) if YEAR_REG.match(y)]

data = pd.DataFrame(map(grab_names, files),
                    columns=NAMES+["total", "year"]).set_index(
                        "year").sort_index()

def plot_names(name):
    values = data[name]/data.total*100000 # percentage of population
    name_label = "{}\t\t({} total baby count)".format(name, data[name].sum()).expandtabs()
    ax = plt.plot(data.index, values, lw=2, label=name_label)
    plt.fill_between(data.index, 0, values, alpha=0.2)
    return ax

sns.set_style("darkgrid")
sns.set_palette(sns.color_palette("dark"))
map(plot_names, NAMES)
plt.legend(loc="upper mid")
plt.ylabel("Number of Babies born (per 100,000)")
plt.xlabel("Year")
plt.xlim((1910, 2016))
plt.show()

plt.savefig("MeridaArlissDodge.png")

# Total count of "Merida" if the movie "Brave" hadn't been made: ~402
data[data.index < 2011].Merida.sum() + data[data.index < 2011].Merida.mean()*5
