# Crowdmark function
def crowd():
    # Changes grade column index for crowdmark tests
    def crowd_test(table, mod):  # Mod is modulus

        crowd_percent = []
        ass_crowd = 0  # Number of assignments

        for g in table:  # Changes to text
            g = g.text
            ass_crowd += 1

            if ass_crowd % mod == 0:  # Returns 4th column
                if g != '' and g != '   ^`^t':
                    g_per = g.split("%")  # Removes percent sign
                    crowd_percent.append(g_per[0])
                else:
                    crowd_percent.append(not_marked_yet)

        return crowd_percent

    # Change for course.
    def crowd_change(course):
        # direct link for faster operation
        driver.get(crowd_link + course)
        WebDriverWait(driver, 10).until(g_load)

        # Local Variables
        table_percent = []
        num = 0

        # Changes index for dict_percent if test or assignment
        tables = driver.find_elements_by_tag_name('table')

        if len(tables) == 1:  # Gos directly to assignments if no tests
            data_val = 4
            table_data = tables[0].find_elements_by_tag_name('td')
            table_percent = crowd_test(table_data, data_val)

        else:
            for table_id in tables:  # Looks for table data in each table
                table_data = table_id.find_elements_by_tag_name('td')
                num += 1

                # Goes to tests for first table, and assignments for second.
                if num == 1:
                    data_val = 3

                else:
                    data_val = 4

                # Gets percent from tests then percent from assignments
                crowd_per = crowd_test(table_data, data_val)
                table_percent += crowd_per

        return table_percent

    # Element locators for wait function
    g_load = ec.presence_of_element_located((By.TAG_NAME, 'td'))  # grade tables
    # crowdmark loading
    driver.get('https://app.crowdmark.com/sign-in')
    driver.find_element_by_id('user_email').send_keys(c_usr)
    driver.find_element_by_id('user_password').send_keys(c_psw)
    driver.find_element_by_xpath('/html/body/section/main/section/div/div[1]/form/div/input').click()

    # Crowdmark calling function
    for cc in crowd_course.keys():  # Grabs id
        percent_crowd = crowd_change(crowd_course[cc])

        # Reveres Crowdmark's stupid ordering and appends to percent dict
        percent_crowd.reverse()
        dict_percent[cc] = percent_crowd