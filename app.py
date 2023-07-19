import meze as mz

if __name__ == "__main__":

    t = mz.Tools
    f = mz.FileIO
    c = mz.Container("deneme")

    c.load_file("data/test/ombx.xlsx")
    c.load_file("data/test/qfcy.xlsx")
    c.load_file("data/test/yosm.xlsx")
    