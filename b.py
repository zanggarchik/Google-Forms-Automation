import os
import time
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Настройка Google Gemini API
genai.configure(api_key="AIzaSyCuvDeFUyWHD6D3qL2fhaatvjVL4LWdlJQ")

# Конфигурация генерации
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 500,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


def get_correct_answer(question, options=None):
    if options:
        prompt = f"""На вопрос: "{question}" выбери правильный ответ из предложенных вариантов.  
        Варианты: {', '.join(options)}.  
        Ответь только текстом одного из предложенных вариантов, без пояснений."""
    else:
        prompt = f"Какой правильный ответ на этот вопрос: '{question}'? Только ответ, без пояснений."

    response = model.generate_content(prompt)
    return response.text.strip()


# Настройка Selenium
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Открываем Google Form
form_url = "https://docs.google.com/forms/d/e/1FAIpQLScf_whB5EID_Hx4PuBuymloIGmqVqCSHouA3R44xcE97Wa7Cw/viewform?usp=sharing"
driver.get(form_url)
time.sleep(30)  # Ждём загрузку страницы

# Найти все вопросы
questions = driver.find_elements(By.XPATH, '//div[@role="listitem"]')

for i, question_elem in enumerate(questions):
    try:
        question_text = question_elem.find_element(By.XPATH, './/div[@role="heading"]').text.strip()
        print(f"Вопрос {i + 1}: {question_text}")

        # Сбор вариантов ответа (если есть)
        options = []
        option_elems = question_elem.find_elements(By.XPATH, './/div[@role="checkbox"] | .//div[@role="radio"]')
        for option in option_elems:
            label = option.find_element(By.XPATH, './ancestor::label').text.strip()
            options.append(label)

        # Получаем правильный ответ
        correct_answer = get_correct_answer(question_text, options if options else None)
        print(f"Ответ: {correct_answer}")

        # Ввод ответа в текстовое поле, если оно есть (включая textarea)
        input_fields = question_elem.find_elements(By.XPATH, './/input[@type="text"] | .//textarea')
        if input_fields:
            input_fields[0].send_keys(correct_answer)

        # Клик по правильному варианту для чекбоксов/радио-кнопок
        for option in option_elems:
            label = option.find_element(By.XPATH, './ancestor::label').text.strip()
            if correct_answer.lower() in label.lower():
                driver.execute_script("arguments[0].click();", option)
                break

    except Exception as e:
        print(f"Ошибка при обработке вопроса {i + 1}: {e}")
    time.sleep(1)

# Отправка формы
# try:
#     submit_button = driver.find_element(By.XPATH, '//span[text()="Отправить"]')
#     driver.execute_script("arguments[0].click();", submit_button)
#     print("Форма успешно отправлена!")
# except:
#     print("Ошибка: Кнопка 'Отправить' не найдена.")

# Закрываем браузер
time.sleep(5000)
driver.quit()
