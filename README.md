# Ualberta-Eclass-Grade-Grab
Grabs grades from ualberta eclass

Imput your class names and id in the dictionaries in 'GradeGrab.py'.

the sending email works with google api and works beter with 2 factor authentcation
[Create App Key](https://support.google.com/accounts/answer/185833?hl=en&authuser=2)
put this in for api password for email

Replace info in 'UserInfo.txt' 
with your respective usernames and passwords.

you might want to run with crontab.
To run main programj 3/day and program to check error file 1/week
change location of python and progams

```
# For python
0 0,6,12,18 * * * /home/arno/anaconda3/envs/GradeTest/bin/python /home/arno/anaconda3/envs/Ualberta-Eclass-Grade-Grab/GradeGrab.py
# weekly log
0 0 * * 0 /home/arno/anaconda3/envs/GradeTest/bin/python /home/arno/anaconda3/envs/Ualberta-Eclass-Grade-Grab/LogClear.py
```

Issues arise with chromedriver ocassionaly, please make sure chrome and chromedriver are at the same versions. 
If you are running headless linux:
download latest chrome [1]: 
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```
download latest chromedriver [2]:
```
wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
```

[1] https://linuxize.com/post/how-to-install-google-chrome-web-browser-on-ubuntu-18-04/
[2] https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/
