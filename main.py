import requests #импортируем библиотеки
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import yadisk

def plot_graph(x, y): #функция построения графика через библиотеку matplotlib
    plt.plot(x, y) #строим график с помощью значений из массивов
    plt.xlabel('дата') #называем ось ОХ "дата"
    plt.ylabel('курс') #называем ось ОУ "курс"
    plt.show() #выводим график

def getRate(id, date): #основная функция получения котировок
    url = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req=' + date #официальный xml документ центробанка на заданную дату

    userAgent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15'}
    #используем User-Agent что бы ресурс не думал что это бот

    pars = requests.get(url, userAgent) #получаем страницу с помощью библиотеки requests

    page = BeautifulSoup(pars.content, features="xml") #извлекаем данные с помощью библиотеки BeautifulSoup

    currency = page.findAll("Valute", {"ID": id}) #находим курс нужной валюты в xml документе с помощью id 

    pound = float((currency[0].text)[-7:].replace(',', '.')) #выделяем из строки только цифры курса и преобразуем их в float

    return pound 

def convertor(currency):
    currentDate = datetime.now().date() #получаем текущую дату
    currentDateStr = currentDate.strftime("%d/%m/%Y") #преобразуем дату в строку
    id = {"usd": "R01235", "eur": "R01239"} #id нужной валюты в xml документе
    fid = "R01035"
    print('Курс - ', 1 / getRate(id[currency], currentDateStr) * getRate(fid, currentDateStr)) #вычисляем курс

def history(start, end, key):
    x = [] #массивы для хранения данных для графика x - курс y - дата
    y = []
    fid = "R01035" #идентификатор фунта на сайте центробанка
    start_date = datetime.strptime(start, '%d/%m/%Y') #преобразуем строку в класс date
    end_date = datetime.strptime(end, '%d/%m/%Y') #преобразуем строку в класс date

    current_date = start_date
    while current_date <= end_date: #перебор дат
        date = current_date.strftime('%d/%m/%Y') #преобразуем дату в строку для ссылки
        current_date += timedelta(days=1) #получаем следующую дату 
        currency = getRate(fid, date)
        y.append(currency) #добавляем курс в массив для графика
        x.append(date) #добавляем дату в массив для графика
        print('Курс фунта (', date, ') - ', currency)

    if (key == "Y"): #сохраняем файл на Яндекс.Диск
        yandex = yadisk.YaDisk(token="YOURTOKEN") #личный токен для доступа к Яндекс Диску
        strings = []
        for i in range(len(x)):
            strings.append('Курс фунта (' + str(x[i]) + ') - ' + str(y[i])) #записываем данные в файл

        namefile = start.replace('/', '|') + "to" + end.replace('/', '|') + ".txt";
        with open(namefile, "w") as f: #Создаем и записываем полученные данные в файл
            for s in strings:
                f.write(s + "\n")
        yandex.upload(namefile, "/" + namefile) #записываем файл на Яндекс Диск
    
    plot_graph(x, y) #строим график

def predict_next_day(data, window_size): #прогноз методом скользящего окна
    ma = []
    for i in range(len(data) - window_size + 1):
        ma.append(sum(data[i:i + window_size]) / window_size)
    last_ma = ma[-1]
    return last_ma + (last_ma - ma[-2])

def predict():
    currencyRate = []
    start_date = datetime.now().date() #получаем текущую дату
    previousDate = start_date + timedelta(days=-2) #получаем дату два дня назад

    fid = "R01035" #идентификатор фунта на сайте центробанка

    current_date = previousDate
    while current_date <= start_date: #перебор дат
        date = current_date.strftime('%d/%m/%Y') #преобразуем дату в строку для ссылки
        current_date += timedelta(days=1) #получаем следующую дату 
        currency = getRate(fid, date) #получаем курс от даты
        currencyRate.append(currency) #записываем

    print('Курс на завтра: ', predict_next_day(currencyRate, 2))


def main(): #основная функция
    print('Выберите функцию:')
    print('1 - Онлайн-конверсия валют.')
    print('2 - Исторические данные за выбранный период и построение графика с возможностью сохранения на Yandex.Disk')
    print('3 - Прогноз исходя из колебаний курса за последние 72 часа.')

    userInput = int(input())

    if userInput == 1:
        print('Введите валюту в которую хотите конвертировать фунты')
        print('usd - доллары США, eur - евро')
        userInput = input()
        convertor(userInput)
    elif userInput == 2:
        print('Введите начальную дату в формате ДД/ММ/ГГГГ')
        startDate = input()
        print('Введите конечную дату в формате ДД/ММ/ГГГГ')
        endDate = input()
        print("Нужно ли сохранять данные на Яндекс.Диск?")
        print("Y - да, N - нет")
        key = input()
        history(startDate, endDate, key)
    elif userInput == 3:
        predict()


if __name__ == "__main__":
    main()

#pip install requests bs4 datetime matplotlib yadisk
