# Ualberta-Eclass-Grade-Grab
## Grabs grades from ualberta eclass

## Add Classes
Imput your class names and id in the dictionaries in *GradeGrab.py*. Last year I had some courses on croudmar, so I left the option and dicts in there.
For eclass, the id is the last 6 digits of the URL: https:<span>//eclass.srv.ualberta.ca</span>/course/view.php?id=<ins>62226</ins> 

To send the email, I used the *smtplib* module with google api. Thus, the sending email works better with 2 factor authentcation (and an api key).
[Create App Key](https://support.google.com/accounts/answer/185833?hl=en&authuser=0)

## Replace info in 'UserInfo.txt' 
with your respective usernames and passwords. The email pasword is the api *app password* in the above step.

# Info
## Dependancys
This program has a few dependancies
1.Anaconda
  1.Pandas
2.Selenium
  1.Chrome
  2.Chromedriver
This program uses pandas, so it should be run by anaconda.
[Using and Installer](https://www.anaconda.com/products/individual)
[For linux terminal](https://docs.anaconda.com/anaconda/install/linux/)
Instaling numpy: `conda install pandas`
Selenium: `pip install selenium`

### Chromedriver
Issues arise with chromedriver ocassionaly, please make sure chrome and chromedriver are at the same versions. 
If you are running headless linux:
download latest chrome: [detailed explaination](https://linuxize.com/post/how-to-install-google-chrome-web-browser-on-ubuntu-18-04/)
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```
download latest chromedriver: [detailed explaination](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/)
You may need to change *2.41*, but i am not positive
```
wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
```

## Optional (but recomended)
### Crontab
you might want to run with crontab.
To run main program 3 times/day and the program to check error file once per week.


```
# For python
0 0,6,12,18 * * * /path_to_annaconda_python /path_to_dir/GradeGrab.py
# weekly log
0 0 * * 0 /path_to_annaconda_python /path_to_dir/LogClear.py
```
