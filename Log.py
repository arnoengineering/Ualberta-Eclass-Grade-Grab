import pandas as pd
from pandas.errors import EmptyDataError
from GradeGrab import csv_file, dict_percent


def grab_g():
    try:
        grade_c = pd.read_csv(csv_file, index_col=0)  # reads jason of rand artist
        grade_dict = grade_c.to_dict(orient='index')
    except EmptyDataError:
        grade_dict = {}
    return grade_dict


def write_grade():  # todo, class, dict_percent, log
    df = pd.DataFrame.from_dict(dict_percent, orient='index')
    df.to_csv(csv_file, header=True, index=True)
