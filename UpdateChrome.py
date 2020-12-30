import pycurl
import platform
from io import BytesIO
from os import system


def update_chrome():
    b_obj = BytesIO()
    crl = pycurl.Curl()

    ch_url = 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
    ch_drive_url = 'https://chromedriver.storage.googleapis.com/'

    def url_get(url):
        # Set URL value
        crl.setopt(crl.URL, url)

        # Write bytes that are utf-8 encoded
        crl.setopt(crl.WRITEDATA, b_obj)
        crl.perform()
        crl.close()

        # Get the content stored in the BytesIO object (in byte characters)
        get_body = b_obj.getvalue()
        op = get_body.decode('utf8')
        return op

    ch_drive_url += url_get(ch_drive_url + 'LATEST_RELEASE') + '/chromedriver_linux64.zip'

    ch_cmd = """wget {}
                sudo apt install ./google-chrome-stable_current_amd64.deb
                """.format(ch_url)

    drive_cmd = """wget {}
    unzip chromedriver_linux64.zip
    sudo mv chromedriver /usr/bin/chromedriver
    sudo chown root:root /usr/bin/chromedriver
    sudo chmod +x /usr/bin/chromedriver
    """.format(ch_drive_url)

    # make sure format is correct
    print('Command 1: ', ch_cmd, '\n')
    print('Command 2: ', drive_cmd, '\n')
    con = input('Would you like to continue? [y,n]: ')

    if con.lower() == 'y' or con.lower() == 'yes':
        system(ch_cmd)
        system(drive_cmd)


if 'Linux' in platform.system():
    update_chrome()
else:
    print('Only for running on Linux')
