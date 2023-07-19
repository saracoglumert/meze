import meze as mz

if __name__ == "__main__":

    tools = mz.Tools
    cont = mz.Container("deneme")

    cont.load_file("data/test/ombx.xlsx")
    cont.load_file("data/test/qfcy.xlsx")
    cont.load_file("data/test/yosm.xlsx")
    