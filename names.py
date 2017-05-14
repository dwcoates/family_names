from __future__ import print_function

import os
import re

import pandas as pd
import seaborn as sns
import numpy as np
from scipy.interpolate import spline
from scipy.stats.mstats import zscore
from pylab import rcParams

YEAR_REG = re.compile("yob([0-9]+)\.txt")
DATA_DIR = os.path.abspath("./names_data")
NAMES = ["Arliss", "Merida", "Dodge", "Alisa"]

def read_babies(filename):
    babynames = pd.read_csv(os.path.join(DATA_DIR, filename),
                                header=None,
                                names=["name", "sex", "count"]).sort_values(
                                    "count", ascending=False)
    return babynames

def grab_babies(filename):
    year = int(YEAR_REG.match(filename).group(1))

    babynames = read_babies(filename)

    names = map(lambda name: babynames[babynames.name == name]["count"].sum(),
                NAMES)
    # total baby population and year, respectively
    names += [babynames["count"].sum(), year]

    return names


def pivot_babies(babies):
    return pd.pivot_table(babies, index=["year", "sex"],
                              values="count",
                              columns="name").fillna(0).applymap(int)

def get_yearified_babies(filename):
    babies = read_babies(filename)

    year = int(YEAR_REG.match(filename).group(1))
    babies["year"] = [year]*babies.index.size

    return babies

def squash_babies(baby_files):
    "Get all baby names in baby_files, in wide format, each name a column."
    babies = [get_yearified_babies(baby_file) for baby_file in baby_files]

    return pivot_babies(pd.concat(babies))

files = [y for y in os.listdir(DATA_DIR) if YEAR_REG.match(y)]

data = pd.DataFrame(map(grab_babies, files),
                    columns=NAMES+["total", "year"]).set_index(
                        "year").sort_index()

all_babies = squash_babies(files)

def plot_names(name, smooth=True):
    """
    Plot the names defined in NAMES. Interpolates by default with argument
    smooth.
    """
    name_data = data[name]
    index = data.index
    total_data = data.total
    if smooth:
        # interpolate
        new_index = np.linspace(index.min(), index.max(), 1000)
        name_data = spline(index, name_data, new_index)
        flatten = np.vectorize(lambda x: 0 if x <= 0 else x)
        name_data = flatten(name_data)
        total_data = spline(index, total_data, new_index)
        index = new_index
    values = name_data/total_data*100000 # percentage of population
    name_label = "{}\t\t({} total baby count)".format(name, data[name].sum()).expandtabs()
    ax = plt.plot(index, values, lw=2, label=name_label)
    plt.fill_between(index, 0, values, alpha =0.2)
    return ax

plt.clf()
rcParams['figure.figsize'] = 16, 10
sns.set_style("darkgrid")
sns.set_palette(sns.color_palette("dark"))

plt.figure(1)
plt.subplot(211)
map(plot_names, NAMES)
plt.xlim((1910, 2016))
plt.legend(loc="upper mid")
plt.title("Baby name popularity over last 100 years (with popularity interpolated)")
plt.ylabel("Number of Babies born (per 100,000)")
plt.xlabel("Year")

plt.figure(1)
plt.subplot(212)
map(lambda x: plot_names(x, smooth=False), NAMES)
plt.title("Baby name popularity over last 100 years (raw data)")
plt.legend(loc="upper mid")
plt.ylabel("Number of Babies born (per 100,000)")
plt.xlabel("Year")
plt.xlim((1910, 2016))

# plt.show()

plt.savefig("AlisaMeridaArlissDodge.png")

# Total count of "Merida" if the movie "Brave" hadn't been made: ~402
data[data.index < 2011].Merida.sum() + data[data.index < 2011].Merida.mean()*5
