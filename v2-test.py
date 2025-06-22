import os
import time
import random
import pytest
import allure
import logging
from datetime import datetime, timedelta
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

class GameFunctions:
    @staticmethod
    @allure.step("Create game room")
    def criar_partida(driver, nome_sala="Sala de Teste", max_jogadores=8, rodadas=5, tempo_rodada=90, privacidade="public", senha=""):
        try:
            driver.get('file://' + os.path.join(os.getcwd(), 'criarPartida.html'))
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Preencher informações básicas da sala
            nome_sala_field = driver.find_element(By.ID, 'room-name')
            nome_sala_field.clear()
            nome_sala_field.send_keys(nome_sala)

            max_jogadores_field = driver.find_element(By.ID, 'max-players')
            max_jogadores_field.clear()
            max_jogadores_field.send_keys(str(max_jogadores))

            rodadas_field = driver.find_element(By.ID, 'rounds')
            rodadas_field.clear()
            rodadas_field.send_keys(str(rodadas))

            tempo_field = driver.find_element(By.ID, 'time-per-round')
            tempo_field.clear()
            tempo_field.send_keys(str(tempo_rodada))

            # Configurar privacidade
            privacy_select = Select(driver.find_element(By.ID, 'privacy'))
            privacy_select.select_by_value(privacidade)

            if privacidade == "private":
                password_field = driver.find_element(By.ID, 'password')
                password_field.clear()
                password_field.send_keys(senha)

            # Selecionar algumas categorias (seleciona as 3 primeiras)
            categorias = driver.find_elements(By.CSS_SELECTOR, 'input[name="categoria"]')
            for i in range(min(3, len(categorias))):
                if not categorias[i].is_selected():
                    categorias[i].click()

            # Selecionar algumas letras indesejadas (A, B, C)
            for letra in ['A', 'B', 'C']:
                driver.find_element(By.ID, f'letter-{letra}').click()

            # Clicar no botão de criar partida
            criar_button = driver.find_element(By.XPATH, "//button[contains(text(),'CRIAR PARTIDA')]")
            criar_button.click()

            # Verificar se a sala foi criada com sucesso
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'room-info')))

            # Obter código da sala
            codigo_sala = driver.find_element(By.ID, 'room-code').text
            logging.info(f"Sala criada com código: {codigo_sala}")

            return codigo_sala

        except Exception as e:
            logging.error(f"Failed to create game room: {str(e)}")
            WebActions.take_screenshot(driver, "create_game_error")
            return None

    @staticmethod
    @allure.step("Join game room")
    def entrar_partida(driver, codigo_sala):
        try:
            # Simular entrar na partida (em um sistema real, isso seria uma página separada)
            driver.execute_script(f"localStorage.setItem('partidaAtual', JSON.stringify({{codigo: '{codigo_sala}'}}));")
            return True
        except Exception as e:
            logging.error(f"Failed to join game room: {str(e)}")
            return False

    @staticmethod
    @allure.step("Wait in game room")
    def esperar_na_sala(driver):
        try:
            driver.get('file://' + os.path.join(os.getcwd(), 'salaEspera.html'))
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Marcar como pronto
            ready_button = driver.find_element(By.ID, 'ready-btn')
            ready_button.click()

            # Verificar se o botão mudou de estado
            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.ID, 'ready-btn'), 'NÃO ESTOU PRONTO'))

            return True

        except Exception as e:
            logging.error(f"Failed in waiting room: {str(e)}")
            WebActions.take_screenshot(driver, "waiting_room_error")
            return False

    @staticmethod
    @allure.step("Play round")
    def jogar_rodada(driver):
        try:
            driver.get('file://' + os.path.join(os.getcwd(), 'responderRodada.html'))
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Preencher respostas para todas as categorias
            inputs = driver.find_elements(By.CSS_SELECTOR, '.answer-input')
            for i, input_field in enumerate(inputs):
                input_field.send_keys(f"Resposta Teste {i+1}")

            # Esperar o botão STOP ficar habilitado (após metade do tempo)
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, 'btn-stop')))

            # Clicar no botão STOP
            stop_button = driver.find_element(By.ID, 'btn-stop')
            stop_button.click()

            return True

        except Exception as e:
            logging.error(f"Failed to play round: {str(e)}")
            WebActions.take_screenshot(driver, "play_round_error")
            return False

    @staticmethod
    @allure.step("Validate answers")
    def validar_respostas(driver):
        try:
            driver.get('file://' + os.path.join(os.getcwd(), 'validarRespostas.html'))
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Validar algumas respostas (marcar a primeira como inválida)
            first_answer = driver.find_element(By.CSS_SELECTOR, '.answer-card')
            first_answer.click()

            # Confirmar validações
            confirm_button = driver.find_element(By.ID, 'btn-confirm')
            confirm_button.click()

            # Verificar se o botão mudou de estado
            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.ID, 'btn-confirm'), 'VALIDADO!'))

            return True

        except Exception as e:
            logging.error(f"Failed to validate answers: {str(e)}")
            WebActions.take_screenshot(driver, "validate_answers_error")
            return False

@allure.feature("Game Flow Tests")
class TestGameSystem:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=get_chrome_options()
        )
        self.driver.implicitly_wait(5)
        
        # Configurar dados iniciais no localStorage para simular o estado do jogo
        self.setup_test_data()
        
        yield
        self.driver.delete_all_cookies()
        self.driver.quit()

    def setup_test_data(self):
        # Simular usuário logado
        usuario_logado = {
            "id": 1,
            "nome": "Usuário Teste",
            "avatar": "https://i.pravatar.cc/150?img=1"
        }
        self.driver.execute_script(f"localStorage.setItem('usuarioLogado', JSON.stringify({usuario_logado}));")
        
        # Simular categorias disponíveis
        categorias = [
            {"nome": "País", "descricao": "Nome de países", "origem": "sistema"},
            {"nome": "Animal", "descricao": "Animais de todos os tipos", "origem": "sistema"},
            {"nome": "Nome", "descricao": "Nomes próprios", "origem": "sistema"},
            {"nome": "Objeto", "descricao": "Objetos do cotidiano", "origem": "sistema"},
            {"nome": "Comida", "descricao": "Pratos e alimentos", "origem": "sistema"}
        ]
        self.driver.execute_script(f"localStorage.setItem('categorias', JSON.stringify({categorias}));")
        
        # Simular respostas da rodada para validação
        respostas_rodada = {
            "partidaId": 1,
            "letra": "T",
            "respostas": {
                "País": "Tailândia",
                "Animal": "Tigre",
                "Nome": "Tiago",
                "Objeto": "Teclado",
                "Comida": "Tomate"
            },
            "jogadorId": 1,
            "timestamp": datetime.now().isoformat()
        }
        self.driver.execute_script(f"localStorage.setItem('respostasRodada', JSON.stringify({respostas_rodada}));")

    @allure.story("Game Creation Tests")
    @allure.title("Test create public game room")
    def test_create_public_game(self):
        codigo_sala = GameFunctions.criar_partida(self.driver)
        assert codigo_sala is not None
        assert len(codigo_sala) == 6  # Verifica se o código tem 6 caracteres

    @allure.story("Game Creation Tests")
    @allure.title("Test create private game room")
    def test_create_private_game(self):
        codigo_sala = GameFunctions.criar_partida(
            self.driver,
            privacidade="private",
            senha="senha123"
        )
        assert codigo_sala is not None
        assert len(codigo_sala) == 6

    @allure.story("Game Flow Tests")
    @allure.title("Test complete game flow")
    def test_complete_game_flow(self):
        # Criar sala
        codigo_sala = GameFunctions.criar_partida(self.driver)
        assert codigo_sala is not None
        
        # Entrar na sala (simulado)
        assert GameFunctions.entrar_partida(self.driver, codigo_sala)
        
        # Esperar na sala e marcar como pronto
        assert GameFunctions.esperar_na_sala(self.driver)
        
        # Jogar uma rodada (preencher respostas)
        assert GameFunctions.jogar_rodada(self.driver)
        
        # Validar respostas
        assert GameFunctions.validar_respostas(self.driver)

    @allure.story("Game Components Tests")
    @allure.title("Test answer validation screen")
    def test_answer_validation(self):
        assert GameFunctions.validar_respostas(self.driver)

    @allure.story("Game Components Tests")
    @allure.title("Test round answering screen")
    def test_round_answering(self):
        # Configurar partida atual para o teste
        partida_atual = {
            "id": 1,
            "nome": "Sala de Teste",
            "codigo": "TEST12",
            "maxJogadores": 8,
            "rodadas": 5,
            "tempoPorRodada": 90,
            "privada": False,
            "categorias": [
                {"nome": "País", "descricao": "Nome de países"},
                {"nome": "Animal", "descricao": "Animais de todos os tipos"},
                {"nome": "Nome", "descricao": "Nomes próprios"}
            ],
            "letraSorteada": "T",
            "status": "iniciada"
        }
        self.driver.execute_script(f"localStorage.setItem('partidaAtual', JSON.stringify({partida_atual}));")
        
        assert GameFunctions.jogar_rodada(self.driver)

class ReportFunctions:
    @staticmethod
    @allure.step("Filtering infraction")
    def filter_infraction_type(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioModeracao.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(3)
            select_element = Select(driver.find_element("id", "filterTipo"))
            options = select_element.options
            random_option = random.choice(options)
            random_option_value = random_option.get_attribute("value")

            # Select the random option
            select_element.select_by_value(random_option_value)
            last_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(2)
            while True:
                # Scroll down by scroll_step pixels
                driver.execute_script(f"window.scrollBy(0, {300});")
                
                # Wait to load the content
                time.sleep(0.2)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            time.sleep(3)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to filter infraction: {str(e)}")
            WebActions.take_screenshot(driver, "filter_infraction_error")
            return None
        
    @staticmethod
    @allure.step("Filtering second offense")
    def filter_second_offense(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioModeracao.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(3)
            rein_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'filterReincidencias'))
            )
        
            # Click to focus the field first
            rein_field.click()
            
            # Clear any existing value
            rein_field.clear()
            
            # Generate random number
            random_number = random.randint(1, 4)
            
            # Send the number as string
            rein_field.send_keys(str(random_number))
            time.sleep(2)
            while True:
                # Scroll down by scroll_step pixels
                driver.execute_script(f"window.scrollBy(0, {300});")
                
                # Wait to load the content
                time.sleep(0.2)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            time.sleep(3)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to filter second offense: {str(e)}")
            WebActions.take_screenshot(driver, "filter_sec_offense_error")
            return None
        
    @staticmethod
    @allure.step("Filtering status")
    def filter_status(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioModeracao.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(3)
            select_element = Select(driver.find_element("id", "filterStatus"))
            options = select_element.options
            random_option = random.choice(options)
            random_option_value = random_option.get_attribute("value")

            # Select the random option
            select_element.select_by_value(random_option_value)
            last_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(2)
            while True:
                # Scroll down by scroll_step pixels
                driver.execute_script(f"window.scrollBy(0, {300});")
                
                # Wait to load the content
                time.sleep(0.2)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            time.sleep(3)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to filter status: {str(e)}")
            WebActions.take_screenshot(driver, "filter_status_error")
            return None
        
    @staticmethod
    @allure.step("Filtering severity")
    def filter_severity(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioModeracao.html')
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))

            time.sleep(3)
            select_element = Select(driver.find_element("id", "filterGravidade"))
            options = select_element.options
            random_option = random.choice(options)
            random_option_value = random_option.get_attribute("value")

            # Select the random option
            select_element.select_by_value(random_option_value)
            last_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(2)
            while True:
                # Scroll down by scroll_step pixels
                driver.execute_script(f"window.scrollBy(0, {300});")
                
                # Wait to load the content
                time.sleep(0.2)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            time.sleep(3)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to filter status: {str(e)}")
            WebActions.take_screenshot(driver, "filter_status_error")
            return None

@allure.feature("Report Filter Tests")
class TestReportFilterSystem:
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

    @allure.story("Moderation Tests")
    @allure.title("Test infraction type")
    def test_infraction_type(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ReportFunctions.filter_infraction_type(self.driver)
        assert result == AuthResult.SUCCESS

    @allure.story("Moderation Tests")
    @allure.title("Test second offense")
    def test_second_offense(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ReportFunctions.filter_second_offense(self.driver)
        assert result == AuthResult.SUCCESS
        
    @allure.story("Moderation Tests")
    @allure.title("Test status")
    def test_filter_status(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ReportFunctions.filter_status(self.driver)
        assert result == AuthResult.SUCCESS
        
    @allure.story("Moderation Tests")
    @allure.title("Test severity")
    def test_severity(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ReportFunctions.filter_severity(self.driver)
        assert result == AuthResult.SUCCESS
        
class ActivityFunctions:
    @staticmethod
    @allure.step("Filter by date range")
    def filter_by_date(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioAtividade.html')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)

            # Set random dates (last 7 days)
            start_date = '04/06/2025'
            end_date = '06/06/2025'

            # Set start date
            start_field = driver.find_element(By.ID, 'filterDataInicio')
            start_field.clear()
            start_field.send_keys(start_date)

            # Set end date
            end_field = driver.find_element(By.ID, 'filterDataFim')
            end_field.clear()
            end_field.send_keys(end_date)

            # Scroll to load all data
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(0.2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            time.sleep(2)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to filter by date: {str(e)}")
            WebActions.take_screenshot(driver, "filter_date_error")
            return None

    @staticmethod
    @allure.step("Filter by metric type")
    def filter_by_metric(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioAtividade.html')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)

            # Select random metric
            select_element = Select(driver.find_element(By.ID, 'filterMetrica'))
            options = [opt for opt in select_element.options if opt.get_attribute("value")]
            random_option = random.choice(options)
            select_element.select_by_value(random_option.get_attribute("value"))

            # Scroll to load all data
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(0.2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            time.sleep(2)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to filter by metric: {str(e)}")
            WebActions.take_screenshot(driver, "filter_metric_error")
            return None

    @staticmethod
    @allure.step("Sort by active players")
    def sort_by_players(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioAtividade.html')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)

            # Select random sort order
            select_element = Select(driver.find_element(By.ID, 'sortJogadores'))
            select_element.select_by_value(random.choice(['asc', 'desc']))

            time.sleep(2)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to sort by players: {str(e)}")
            WebActions.take_screenshot(driver, "sort_players_error")
            return None

    @staticmethod
    @allure.step("Clear all filters")
    def clear_filters(driver):
        try:
            driver.get('https://xdes-04-stop-front-end-rodrigoruans-projects.vercel.app/pages/relatorioAtividade.html')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)

            # Click clear filters button
            clear_btn = driver.find_element(By.CLASS_NAME, 'clear-filters')
            clear_btn.click()

            time.sleep(2)
            return AuthResult.SUCCESS
        except Exception as e:
            logging.error(f"Failed to clear filters: {str(e)}")
            WebActions.take_screenshot(driver, "clear_filters_error")
            return None

@allure.feature("Activity Report Tests")
class TestActivityReportSystem:
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

    @allure.story("Activity Report Tests")
    @allure.title("Test date range filter")
    def test_date_filter(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ActivityFunctions.filter_by_date(self.driver)
        assert result == AuthResult.SUCCESS

    @allure.story("Activity Report Tests")
    @allure.title("Test metric type filter")
    def test_metric_filter(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ActivityFunctions.filter_by_metric(self.driver)
        assert result == AuthResult.SUCCESS

    @allure.story("Activity Report Tests")
    @allure.title("Test sorting by players")
    def test_sort_players(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ActivityFunctions.sort_by_players(self.driver)
        assert result == AuthResult.SUCCESS

    @allure.story("Activity Report Tests")
    @allure.title("Test clear filters")
    def test_clear_filters(self):
        result = AuthFunctions.logar(self.driver, "rodolfo@gmail.com", "abc123")
        result = ActivityFunctions.clear_filters(self.driver)
        assert result == AuthResult.SUCCESS
def main():
    pytest.main(["-v", "--alluredir=allure-results"])

if __name__ == "__main__":
    main()