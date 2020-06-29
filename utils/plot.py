import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from logs import get_runs

assert len(sys.argv) == 2
runs = get_runs(sys.argv[1])
assert runs, "Check alg_name"

view_df = pd.DataFrame(runs)

sns.set()

# R generic
df = view_df.drop(columns=["alg_name", "path", "arch"])
df["runtime"] = df["runtime"].astype("category")

for i in df.index:
    params = dict(df.at[i, "params"])
    for k, v in params.items():
        df.at[i, k] = v
    durs = np.array(df.at[i, "durs"])
    df.at[i, "mean"] = np.mean(durs) / 1000  # ms


# Drop specific
df.drop(columns=["params"], inplace=True)


ax = sns.barplot(
    data=df,
    x="num_threads",
    y="mean",
    hue="runtime",
    hue_order=["native", "firefox", "google-chrome"],
    ci=None,
)
ax.set(
    xlabel="Number of Threads",
    ylabel="Mean running time (ms)",
    title="Average Durations per Number of Threads per Platform",
)
ax.legend(title="Platform")
plt.show()
