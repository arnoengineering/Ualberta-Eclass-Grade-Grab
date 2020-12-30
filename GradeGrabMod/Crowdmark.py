from GradeGrabMod.Creds import not_marked_yet

# Import variables
from selenium.webdriver.support.ui import WebDriverWait  # Wait condition


# Crowdmark function
class Crowdmark:
    def __init__(self, course, driver):
        self.driver = driver
        self.course = course
        self.crowd_percent = []
        self.t_data = []
        self.ass_num = 0
        self.mod = 2

    # Changes grade column index for crowdmark tests
    def crowd_test(self):  # Mod is modulus
        for g in self.t_data:  # Changes to text
            g = g.text
            self.ass_num += 1

            if self.ass_num % self.mod == 0:  # Returns 4th column  # todo fix auto
                if g != '' and g != '   ^`^t':
                    g_per = g.split("%")  # Removes percent sign
                    self.crowd_percent.append(g_per[0])
                else:
                    self.crowd_percent.append(not_marked_yet)

    # Change for course.
    # def crowd_change(self):
    #     # direct link for faster operation
    #     self.driver.get(crowd_link + self.course)  # todo fix total
    #     # g_load = ec.presence_of_element_located((By.TAG_NAME, 'td'))  # grade tables
    #     # WebDriverWait(self.driver, 10).until(g_load)
    #
    #     # Local Variables
    #     table_percent = []
    #     num = 0
    #
    #     # Changes index for dict_percent if test or assignment
    #     tables = self.driver.find_elements_by_tag_name('table')
    #
    #     if len(tables) == 1:  # Gos directly to assignments if no tests
    #         data_val = 4
    #         table_data = tables[0].find_elements_by_tag_name('td')
    #         table_percent = self.crowd_test()
    #
    #     else:
    #         for table_id in tables:  # Looks for table data in each table
    #             table_data = table_id.find_elements_by_tag_name('td')
    #             num += 1
    #
    #             # Goes to tests for first table, and assignments for second.
    #             if num == 1:
    #                 data_val = 3
    #
    #             else:
    #                 data_val = 4
    #
    #             # Gets percent from tests then percent from assignments
    #             crowd_per = self.crowd_test()
    #             table_percent += crowd_per

