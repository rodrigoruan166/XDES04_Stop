import os
import time
import random
import pytest
import allure
import logging
from datetime import datetime
from enum import Enum, auto
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def pytest_configure(config):
    config.option.allure_report_dir = os.path.join(os.getcwd(), 'allure-results')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_log.log'),
        logging.StreamHandler()
    ]
)

def get_chrome_options():
    options = Options()
    download_folder = os.path.join(os.getcwd(), 'recursos')
    preferences = {
        "download.default_directory": download_folder,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", preferences)
    options.add_argument("--start-maximized")
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--guest')
    options.add_argument("--password-store=basic")
    return options

class AuthResult(Enum):
    SUCCESS = auto()
    INVALID_PASSWORD = auto()
    USER_EXISTS = auto()
    MISSING_FIELDS = auto()
    UNKNOWN_ERROR = auto()

class WebActions:
    @staticmethod
    def handle_alert(driver):
        try:
            alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"    > Alert TEXT: {alert_text}")
            time.sleep(2)
            alert.accept()
            return alert_text.lower()
        except Exception as e:
            logging.error(f"Alert handling failed: {str(e)}")
            raise

    @staticmethod
    def take_screenshot(driver, name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = os.path.join(os.getcwd(), 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
        driver.save_screenshot(filename)
        logging.info(f"Screenshot saved as {filename}")
        allure.attach.file(filename, name=f"{name}_{timestamp}", attachment_type=allure.attachment_type.PNG)

class AuthFunctions:
    @staticmethod
    @allure.step("Register user")
    def registrar(driver, user, email, passw):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/cadastrar.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            username_field = driver.find_element(By.ID, 'username')
            email_field = driver.find_element(By.ID, 'email')
            password_field = driver.find_element(By.ID, 'password')
            
            username_field.clear()
            email_field.clear()
            password_field.clear()
            
            username_field.send_keys(user)
            email_field.send_keys(email)
            password_field.send_keys(passw)
            
            register_button = driver.find_element(By.XPATH, "//button[contains(text(),'Cadastrar')]")
            register_button.click()
            
            alert_text = WebActions.handle_alert(driver)
            
            if "sucesso" in alert_text:
                return AuthResult.SUCCESS
            elif "já cadastrado" in alert_text:
                return AuthResult.USER_EXISTS
            elif "inválido" in alert_text or "não encontrado" in alert_text:
                return AuthResult.INVALID_PASSWORD
            elif "campo obrigatório" in alert_text or "preencha todos" in alert_text:
                return AuthResult.MISSING_FIELDS
            else:
                return AuthResult.UNKNOWN_ERROR
                
        except Exception as e:
            logging.error(f"Registration failed: {str(e)}")
            WebActions.take_screenshot(driver, "registration_error")
            return AuthResult.UNKNOWN_ERROR

    @staticmethod
    @allure.step("Login user")
    def logar(driver, email, passw):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/login.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            email_field = driver.find_element(By.ID, 'email')
            password_field = driver.find_element(By.ID, 'password')
            
            email_field.clear()
            password_field.clear()
            
            email_field.send_keys(email)
            password_field.send_keys(passw)
            
            login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Entrar')]")
            login_button.click()
            
            alert_text = WebActions.handle_alert(driver)
            
            if "sucesso" in alert_text:
                return AuthResult.SUCCESS
            elif "incorreta" in alert_text:
                return AuthResult.INVALID_PASSWORD
            elif "não encontrado" in alert_text:
                return AuthResult.USER_EXISTS
            else:
                return AuthResult.UNKNOWN_ERROR
                
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            WebActions.take_screenshot(driver, "login_error")
            return AuthResult.UNKNOWN_ERROR

class ProfileFunctions:
    @staticmethod
    @allure.step("Edit privacy settings")
    def edita_privacidade(driver, passw):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/perfil.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(2)
            edit_button = driver.find_element(By.XPATH, "//button[contains(text(),'Editar Perfil')]")
            edit_button.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'senhaAtualInput')))

            dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "privacidadeInput")))
            select = Select(dropdown)

            op_atual = select.first_selected_option
            op_index = select.options.index(op_atual)

            time.sleep(2)
            if op_index == 0:
                select.select_by_index(1)
                logging.info("Switched from 0 to 1")
            else:
                select.select_by_index(0)
                logging.info("Switched from 1 to 0")
            
            time.sleep(3)
            password_field = driver.find_element(By.ID, 'senhaAtualInput')
            password_field.clear()
            password_field.send_keys(passw)

            save_button = driver.find_element(By.XPATH, "//button[contains(text(),'Salvar')]")
            save_button.click()

            alert_text = WebActions.handle_alert(driver)

            if "sucesso" in alert_text:
                time.sleep(3)
                return AuthResult.SUCCESS
            elif "inválida" in alert_text:
                return AuthResult.INVALID_PASSWORD
            else:
                return AuthResult.UNKNOWN_ERROR
                
        except Exception as e:
            logging.error(f"Change Privacy failed: {str(e)}")
            WebActions.take_screenshot(driver, "change_privacy_error")
            return AuthResult.UNKNOWN_ERROR

    @staticmethod
    @allure.step("Change profile picture")
    def mudar_foto(driver, passw):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/perfil.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(2)
            edit_button = driver.find_element(By.XPATH, "//button[contains(text(),'Editar Perfil')]")
            edit_button.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'senhaAtualInput')))

            foto = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "imagemInput")))
            foto.clear()
            foto.send_keys(f"https://picsum.photos/id/{random.randint(1, 300)}/200/300")

            time.sleep(3)
            password_field = driver.find_element(By.ID, 'senhaAtualInput')
            password_field.clear()
            password_field.send_keys(passw)

            save_button = driver.find_element(By.XPATH, "//button[contains(text(),'Salvar')]")
            save_button.click()

            alert_text = WebActions.handle_alert(driver)

            if "sucesso" in alert_text:
                time.sleep(3)
                return AuthResult.SUCCESS
            elif "inválida" in alert_text:
                return AuthResult.INVALID_PASSWORD
            else:
                return AuthResult.UNKNOWN_ERROR
                
        except Exception as e:
            logging.error(f"Change Privacy failed: {str(e)}")
            WebActions.take_screenshot(driver, "change_privacy_error")
            return AuthResult.UNKNOWN_ERROR

    @staticmethod
    @allure.step("Change profile name")
    def mudar_nome(driver, passw):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/perfil.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(2)
            edit_button = driver.find_element(By.XPATH, "//button[contains(text(),'Editar Perfil')]")
            edit_button.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'senhaAtualInput')))

            foto = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nomeInput")))
            foto.clear()
            foto.send_keys(f"Nome Maneiro {random.randint(100, 3000)}")

            time.sleep(3)
            password_field = driver.find_element(By.ID, 'senhaAtualInput')
            password_field.clear()
            password_field.send_keys(passw)

            save_button = driver.find_element(By.XPATH, "//button[contains(text(),'Salvar')]")
            save_button.click()

            alert_text = WebActions.handle_alert(driver)

            if "sucesso" in alert_text:
                time.sleep(3)
                return AuthResult.SUCCESS
            elif "inválida" in alert_text:
                return AuthResult.INVALID_PASSWORD
            else:
                return AuthResult.UNKNOWN_ERROR
                
        except Exception as e:
            logging.error(f"Change Privacy failed: {str(e)}")
            WebActions.take_screenshot(driver, "change_privacy_error")
            return AuthResult.UNKNOWN_ERROR

    @staticmethod
    @allure.step("Delete profile")
    def deleta_perfil(driver, passw):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/perfil.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(2)
            del_button = driver.find_element(By.XPATH, "//button[contains(text(),'Deletar Perfil')]")
            del_button.click()

            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                time.sleep(2)
                driver.switch_to.alert.accept()
            except:
                logging.warning("No alert to confirm deletion.")
                return AuthResult.UNKNOWN_ERROR

            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                if "Digite sua senha para confirmar" in alert.text:
                    alert.send_keys(passw)
                    time.sleep(2)
                alert.accept()
            except:
                logging.error("No prompt appeared")
                return AuthResult.UNKNOWN_ERROR
            
            time.sleep(1)
            alert_text = WebActions.handle_alert(driver)

            if "sucesso" in alert_text:
                time.sleep(3)
                return AuthResult.SUCCESS
            elif "inválida" in alert_text:
                return AuthResult.INVALID_PASSWORD
            else:
                return AuthResult.UNKNOWN_ERROR
                
        except Exception as e:
            logging.error(f"Change Privacy failed: {str(e)}")
            WebActions.take_screenshot(driver, "change_privacy_error")
            return AuthResult.UNKNOWN_ERROR

class CategoryFunctions:
    @staticmethod
    @allure.step("Create category")
    def criar_categoria(driver, nomeCat=' ', descCat=' '):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/categoria.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(2)

            nomeCat_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nomeCategoriaInput")))
            nomeCat_button.clear()
            nomeCat_button.send_keys(nomeCat)

            descCat_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "descricaoCategoriaInput")))
            descCat_button.clear()
            descCat_button.send_keys(descCat)
            time.sleep(3)

            criar_button = driver.find_element(By.XPATH, "//button[contains(text(),'Adicionar')]")
            criar_button.click()

            alert_text = WebActions.handle_alert(driver)

            if "sucesso" in alert_text:
                time.sleep(3)
                return AuthResult.SUCCESS
            elif "já cadastrada":
                return AuthResult.USER_EXISTS
            else:
                return AuthResult.MISSING_FIELDS
                
        except Exception as e:
            logging.error(f"Create Category failed: {str(e)}")
            WebActions.take_screenshot(driver, "create_category_error")
            return AuthResult.UNKNOWN_ERROR

    @staticmethod
    @allure.step("Edit category")
    def editar_categoria(driver, novoNome=' ', novaDesc=' '):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/categoria.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(2)

            first_li = driver.find_element(By.CSS_SELECTOR, "#listaCategorias li:first-child")
            edit_button = first_li.find_element(By.CSS_SELECTOR, ".edit-btn")
            edit_button.click()

            input_box = WebDriverWait(first_li, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".edit-input"))
            )
            textarea = WebDriverWait(first_li, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".edit-textarea"))
            )

            input_box.clear()
            input_box.send_keys(novoNome)
            textarea.clear()
            textarea.send_keys(novaDesc)

            time.sleep(3)

            salvar_button = first_li.find_element(By.XPATH, ".//button[contains(text(),'Salvar')]")
            salvar_button.click()

            time.sleep(2)

            return AuthResult.SUCCESS
                    
        except Exception as e:
            logging.error(f"Edit Category failed: {str(e)}")
            WebActions.take_screenshot(driver, "edit_category_error")
            return AuthResult.UNKNOWN_ERROR

    @staticmethod
    @allure.step("Delete category")
    def deletar_categoria(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/categoria.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(2)

            first = driver.find_element(By.CSS_SELECTOR, "#listaCategorias li:first-child")
            first.find_elements(By.TAG_NAME, "button")[1].click()
            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                time.sleep(2)
                driver.switch_to.alert.accept()
            except:
                logging.warning("No alert to confirm deletion.")
                return AuthResult.UNKNOWN_ERROR
            
            time.sleep(2)

            return AuthResult.SUCCESS
                    
        except Exception as e:
            logging.error(f"Edit Category failed: {str(e)}")
            WebActions.take_screenshot(driver, "edit_category_error")
            return AuthResult.UNKNOWN_ERROR

@allure.feature("Authentication Tests")
class TestAuthSystem:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=get_chrome_options()
        )
        self.driver.implicitly_wait(5)
        yield
        self.driver.delete_all_cookies()
        self.driver.quit()

    #@pytest.fixture
    #def registered_user(self):
        #result = AuthFunctions.registrar(self.driver, "testuser", "test@test.com", "TestPass123!")
        #assert result == AuthResult.SUCCESS

    @allure.story("Registration Tests")
    @allure.title("Test successful registration")
    def test_successful_registration(self):
        result = AuthFunctions.registrar(self.driver, "newuser123", "newuser123@test.com", "StrongPass123!")
        assert result == AuthResult.SUCCESS

    @allure.story("Registration Tests")
    @allure.title("Test existing email registration")
    def test_existing_email_registration(self):
        result = AuthFunctions.registrar(self.driver, "differentuser", "test@test.com", "Pass123!")
        assert result == AuthResult.USER_EXISTS
        
    @allure.story("Registration Tests")
    @allure.title("Test invalid password registration")
    def test_invalid_password_registration(self):
        result = AuthFunctions.registrar(self.driver, "user123", "user123@test.com", "weak")
        assert result == AuthResult.INVALID_PASSWORD

    @allure.story("Login Tests")
    @allure.title("Test successful login")
    def test_successful_login(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "TestPass123!")
        assert result == AuthResult.SUCCESS

    @allure.story("Profile Tests")
    @allure.title("Test edit privacy settings")
    def test_edit_privacy(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "TestPass123!")
        assert result == AuthResult.SUCCESS
        result = ProfileFunctions.edita_privacidade(self.driver, "TestPass123!")
        assert result == AuthResult.SUCCESS
        
    @allure.story("Login Tests")
    @allure.title("Test wrong password login")
    def test_wrong_password_login(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "WrongPass123!")
        assert result == AuthResult.INVALID_PASSWORD
        
    @allure.story("Login Tests")
    @allure.title("Test non-existent user login")
    def test_nonexistent_user_login(self):
        result = AuthFunctions.logar(self.driver, "nonexistent@test.com", "AnyPass123!")
        assert result == AuthResult.USER_EXISTS

    @allure.story("Profile Tests")
    @allure.title("Test change profile picture")
    def test_change_profile_picture(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "TestPass123!")
        assert result == AuthResult.SUCCESS
        result = ProfileFunctions.mudar_foto(self.driver, "TestPass123!")
        assert result == AuthResult.SUCCESS

    @allure.story("Profile Tests")
    @allure.title("Test change profile name")
    def test_change_profile_name(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "TestPass123!")
        assert result == AuthResult.SUCCESS
        result = ProfileFunctions.mudar_nome(self.driver, "TestPass123!")
        assert result == AuthResult.SUCCESS

    @allure.story("Category Tests")
    @allure.title("Test create category")
    def test_create_category(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "TestPass123!")
        assert result == AuthResult.SUCCESS
        result = CategoryFunctions.criar_categoria(self.driver, "Test Category", "Test Description")
        assert result == AuthResult.SUCCESS

    @allure.story("Category Tests")
    @allure.title("Test edit category")
    def test_edit_category(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "TestPass123!")
        assert result == AuthResult.SUCCESS
        CategoryFunctions.criar_categoria(self.driver, "Initial Category", "Initial Description")
        result = CategoryFunctions.editar_categoria(self.driver, "Edited Category", "Edited Description")
        assert result == AuthResult.SUCCESS

    @allure.story("Category Tests")
    @allure.title("Test delete category")
    def test_delete_category(self):
        result = AuthFunctions.logar(self.driver, "test@test.com", "TestPass123!")
        assert result == AuthResult.SUCCESS
        CategoryFunctions.criar_categoria(self.driver, "Initial Category", "Initial Description")
        result = CategoryFunctions.deletar_categoria(self.driver)
        assert result == AuthResult.SUCCESS

    @allure.story("Profile Tests")
    @allure.title("Test delete profile")
    def test_delete_profile(self):
        result = AuthFunctions.registrar(self.driver, "tempuser", "tempuser@test.com", "TempPass123!")
        assert result == AuthResult.SUCCESS
        result = AuthFunctions.logar(self.driver, "tempuser@test.com", "TempPass123!")
        assert result == AuthResult.SUCCESS
        result = ProfileFunctions.deleta_perfil(self.driver, "TempPass123!")
        assert result == AuthResult.SUCCESS
        result = AuthFunctions.logar(self.driver, "tempuser@test.com", "TempPass123!")
        assert result == AuthResult.USER_EXISTS

def main():
    pytest.main(["-v", "--alluredir=allure-results"])

if __name__ == "__main__":
    main()