import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from logs import get_runs

view_df = pd.DataFrame(get_runs("atomics"))

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
df.drop(columns=["params", "measure_per_run"], inplace=True)


ax = sns.barplot(
    data=df,
    x="num_threads",
    y="mean",
    hue="runtime",
    hue_order=["native", "firefox", "google-chrome"],
)
ax.set(
    xlabel="Number of Threads",
    ylabel="Mean running time (ms)",
    title="Average Durations per Number of Threads per Platform",
)
ax.legend(title="Platform")
plt.show()
