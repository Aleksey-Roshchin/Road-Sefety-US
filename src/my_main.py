import os, matplotlib.pyplot as plt, pandas as pd, utils as ut
CSV=r"D:\dataset\US_Accidents_March23.csv"

def show(d,c):
    t,b=ut.agg(d,c)
    print(f"\n* {c.upper()}  base={b:.3f}")
    for _,r in t.iterrows():
        print(f"{str(r[c]):>4}  cnt={int(r.cnt):7d}  share={r.share:.3f}  diff={r.d_pct:+6.1f}%")

def main():

    df=ut.feat(ut.ld(CSV))

    for c in["wkd","tod","wnd","frz","road","prec"]:show(df,c)

    num=["Severity","sev","ngt","rush","prec","bad","vlow",
         "wkd","frz","bump","cross"]
    X=pd.get_dummies(df[["road","wnd","tod"]],drop_first=True)
    corr=pd.concat([df[num],X],axis=1).corr()


    plt.figure(figsize=(12, 9), dpi=200)
    plt.imshow(corr, vmin=-1, vmax=1)
    plt.xticks(range(len(corr)),corr.columns,rotation=90,fontsize=6)
    plt.yticks(range(len(corr)),corr.index,fontsize=6)
    plt.colorbar();plt.tight_layout();plt.show()

if __name__=="__main__":main()
