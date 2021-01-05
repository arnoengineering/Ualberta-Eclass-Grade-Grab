# Ualberta-Eclass-Grade-Grab
## Grabs grades from ualberta eclass


## Add Classes
Input your class names and id in the dictionaries in *GradeGrabMod/Creds.py*. Last year I had some courses on crowdmark, 
so I left the option and dicts in there. For eclass, the id is the last 6 digits of the URL: 
https:<span>//eclass.srv.ualberta.ca</span>/course/view.php?id=<ins>62226</ins> 

To send the email, I used the *smtplib* module with google api. Thus, the sending email works better with 2 factor authentication (and an api key).
[Create App Key](https://support.google.com/accounts/answer/185833?hl=en&authuser=0)


## Replace info in 'UserInfo.txt' 
copy file: remove'.example' from file name and replace all non comments with your respective usernames and passwords. 
The email password is the api *app password* in the above step.


# Info
## Dependancys
This program has a few dependencies

- Anaconda
    - Pandas
- Selenium
    - Chrome
    - Chromedriver
- pycurl
    
This program uses pandas, so it should be run by anaconda.
[Using and Installer](https://www.anaconda.com/products/individual)
[For linux terminal](https://docs.anaconda.com/anaconda/install/linux/)

Pycurl is used in a script to update chrome/chromedriver, thus it can be ignored if you would prefer to do this yourself.
Also, I think it is already installed in linux.

these can be installed by:
```
conda install pandas
pip install selenium
pip install pycurl
```


### Module
Recently change the file into multiple smaller docs. Thus *Creds.py* is new file with most of the global variables.

 
### Chromedriver
Issues arise with chromedriver occasionally, please make sure chrome and chromedriver are at the same versions. 

**To download on linux:**
*UpdateChrome* is a script that allows for automatic updates once run.

If you would like to do this manually:
- Download latest chrome: [detailed explanation](https://linuxize.com/post/how-to-install-google-chrome-web-browser-on-ubuntu-18-04/)
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```
- Download latest chromedriver: [detailed explanation](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/)

To get version:`curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE`
then run, replacing *version* with the version returned by previous.
```
wget https://chromedriver.storage.googleapis.com/version/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
```


## Optional (but recommended)
### Crontab
you might want to run with crontab.
To run main program 3 times/day and the program to check error file once per week.

```
# For python
0 0,6,12,18 * * * /path_to_annaconda_python /path_to_dir/GradeGrab.py
# weekly log
0 0 * * 0 /path_to_annaconda_python /path_to_dir/LogClear.py
```
