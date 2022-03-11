import pandas as pd

def aggregate():
    "aggregate specified datasets"
    df_lst = []
    df_1 = pd.read_csv("cleaned/agg_df_2.csv", header=0)
    df_2 = pd.read_csv("cleaned/k_car_data.csv", header=0)
    df_2 = fix_150(df_2)
    agg_df = pd.concat([df_2,df_1], ignore_index=True)
    agg_df.to_csv(r"cleaned/agg_df_3.csv", index=False)

def fix_150(df):
    "reformats 150-pt checklist for neural net input"
    for _, row in df.iterrows():
        if len(row["150-pt"]) > 5:
            bool_lst = row["150-pt"][1:-1].split(",")
            count = 0
            print(_)
            for b in bool_lst:
                if _ == 0:
                    df["150-pt_{}".format(str(count))] = b
                    count += 1
                else:
                    df.loc[_, "150-pt_{}".format(str(count))] = b
                    count += 1
        else:
            df = df.drop(_)
    df = df.drop(columns="150-pt")
    return df