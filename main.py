import src.interface.menus.user_interface as ui
from src.constants     import *
from src.data_loader   import *
from src.analysis      import *
from src.visualization import *

import pandas as pd


def main() -> None:

    # ui.clear()
    # ui.print_logo_centered("interface/menus/program_logo.txt")
    # ui.main_menu()

    df = feat(ld(CSV))

    for c in ["wkd", "tod", "wnd", "frz", "road", "prec"]:
        show(df, c)

    num = ["Severity", "sev", "ngt", "rush", "prec", "bad", "vlow",
           "wkd", "frz", "bump", "cross"]

    X = pd.get_dummies(df[["road", "wnd", "tod"]], drop_first=True)

    data = pd.concat([df[num], X], axis=1) \
        .astype("float32", copy=False)

    corr = data.corr()
    plot_corr(corr)


if __name__ == "__main__":
    main()
