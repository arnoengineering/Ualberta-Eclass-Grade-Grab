import pandas as pd
import os
from pandas.errors import EmptyDataError
from GradeGrabMod import csv_file


def grab_g():
    try:
        if not os.path.exists(csv_file):  # create file
            f = open(csv_file)
            f.close()
        grade_c = pd.read_csv(csv_file, index_col=0)  # reads jason of rand artist
        grade_dict = grade_c.to_dict(orient='index')
    except (EmptyDataError, IOError):
        grade_dict = {}
    return grade_dict


def write_grade(dict_percent):
    df = pd.DataFrame.from_dict(dict_percent, orient='index')
    df.to_csv(csv_file, header=True, index=True)
