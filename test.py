from selenium import webdriver
import os

phantomjs_path = "C:\Python27\misc\phantomjs-2.1.1-windows\\bin\phantomjs.exe"

browser = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull)
browser.set_window_size(1400, 1000)

browser.get("http://stackoverflow.com/")

print browser.title