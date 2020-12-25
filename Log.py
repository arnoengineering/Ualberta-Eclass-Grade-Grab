def grab_g(file):
    grade_c = pd.read_csv(file, index_col=0)  # reads jason of rand artist
    grade_dict = grade_c.to_dict(orient='index')
    return grade_dict


def write_grade(file, grades):  # todo, class, grades
    df = pd.DataFrame.from_dict(grades, orient='index')
    df.to_csv(file, header=True, index=True)
