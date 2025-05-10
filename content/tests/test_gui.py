import time

from django.test import TestCase

from unittest import skip
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

class GuiTestWithSelenium(TestCase):
    @skip
    def test_page_titles(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://127.0.0.1:8000/")
        assert "Blog Platform" in self.driver.title
        time.sleep(1)
        self.driver.get("http://127.0.0.1:8000/about/")
        assert "O Platforme" in self.driver.title
        time.sleep(1)
        self.driver.get("http://127.0.0.1:8000/qa/")
        assert "Q & A" in self.driver.title

    @skip
    def test_signup(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://127.0.0.1:8000/accounts/signup/")
        time.sleep(1)
        username_input = self.driver.find_element(by=By.NAME, value="username")
        username_input.send_keys("SlavojZizek")
        time.sleep(1)
        firstname_input = self.driver.find_element(by=By.NAME, value="first_name")
        firstname_input.send_keys("Slavoj")
        time.sleep(1)
        lastname_input = self.driver.find_element(by=By.NAME, value="last_name")
        lastname_input.send_keys("Žižek")
        time.sleep(1)
        email_input = self.driver.find_element(by=By.NAME, value="email")
        email_input.send_keys("slavojzizek@mail.io")
        time.sleep(1)
        password1_input = self.driver.find_element(by=By.NAME, value="password1")
        password1_input.send_keys("ZPc5dash32u0")
        time.sleep(1)
        password2_input = self.driver.find_element(by=By.NAME, value="password2")
        password2_input.send_keys("ZPc5dash32u0")
        time.sleep(3)
        submit_btn = self.driver.find_element(By.ID, 'id_submit')
        submit_btn.send_keys(Keys.RETURN)

        assert ("Prihláste sa do svojho účtu" or "Toto užívateľské meno je už obsadené." in self.driver.page_source)

    def test_login(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://127.0.0.1:8000/accounts/login/")
        time.sleep(1)
        username_input = self.driver.find_element(by=By.NAME, value="username")
        username_input.send_keys("SlavojZizek")
        time.sleep(1)
        password_input = self.driver.find_element(by=By.NAME, value="password")
        password_input.send_keys("ZPc5dash32u0")
        time.sleep(1)
        submit_btn = self.driver.find_element(By.ID, 'id_submit')
        submit_btn.send_keys(Keys.RETURN)

        assert ("Slavoj Žižek" or "Please enter a correct username and password. Note that both fields may be case-sensitive." in self.driver.page_source)

