import requests
import geocoder
import pandas as pd
import os


API_KEY = 'b9223c17622bebeec90cc05201230585'
LINK = 'https://api.openweathermap.org/data/2.5/weather?units=metric&lang=ru&q={}&appid={}'

TEXT_OF_INTERFACE = "Что вы хотите узнать?\n" \
                    "Введите '1' чтобы узнать погоду по вашему местоположению\n" \
                    "Введите '2' чтобы узнать погоду в выбранном городе\n" \
                    "Введите '3' чтобы посмотреть историю\n" \
                    "Введите '4' чтобы очистить историю\n" \
                    "Введите '5' чтобы выйти из программы\n"

TEXT_OF_WEATHER_REPORT = "Город: {}\n" \
                         "Температура: {}°C\n" \
                         "Ощущается как: {}°C\n" \
                         "Облачность: {}\n" \
                         "Скорость ветра: {} м/с\n"


def get_user_city() -> dict[str, float]:
    """
    Определяет город пользователя по его ip

    :return: Название города
    """

    return geocoder.ip('me').city


def get_weather_data_for_city(city) -> dict[str: any]:
    """
    Совершает запрос к веб сервису для определения погоды

    :return: словарь с погодными данными для города, введенного пользователем
    """

    response = requests.get(LINK.format(city, API_KEY))
    return response.json()


def parse_weather_data(weather_data) -> dict[str: any]:
    """
    Функция парсит из словаря следующие данные:
        Город, где были произведены измерения city
        Температура temperature
        Ощущение температуры temp_feels_like
        Облачность cloud
        Скорость ветра wind_speed

    :return: словарь с необходимыми данными
    """

    city = weather_data['name']
    temperature = weather_data['main']['temp']
    temp_feels_like = weather_data['main']['feels_like']
    cloud = weather_data['weather'][0]['description']
    wind_speed = weather_data['wind']['speed']

    useful_weather_data = {'city': city,
                           'temp': temperature,
                           'feels_like': temp_feels_like,
                           'cloud': cloud,
                           'wind_speed': wind_speed}

    return useful_weather_data


def weather_report(useful_weather_data: dict[str, any]):
    """
    Функция формирует строку с данными о погоде

    :param useful_weather_data: Словарь с данными о погоде
    :return: Отформатированная строка с данными
    """

    return TEXT_OF_WEATHER_REPORT.format(useful_weather_data['city'],
                                         useful_weather_data['temp'],
                                         useful_weather_data['feels_like'],
                                         useful_weather_data['cloud'],
                                         useful_weather_data['wind_speed'])


def create_or_read_history() -> pd.DataFrame:
    """
    Функция считывает csv файл с историей, если он есть,
    в противном случае создается пустой шаблон для истории

    :return: История запросов в виде объекта pandas DataFrame
    """

    if os.path.exists('history.csv'):
        return pd.read_csv('history.csv')

    return pd.DataFrame(columns=['city', 'temp', 'feels_like', 'cloud', 'wind_speed'])


def write_data_to_history(weather_data: dict[str, any]) -> None:
    """
    Функция записывает в историю данную информацию о погоде

    :param weather_data: Словарь с данными, которые необходимо записать в историю
    :return: None
    """
    history = create_or_read_history()
    history.loc[len(history)] = weather_data
    history.to_csv('history.csv', index=False)


def see_last_n_requests(n: int) -> None:
    """
    Функция возвращает n последних запросов из истории, если это возможно

    :param n: Целое число, равно количеству запросов, которые желает увидеть пользователь
    :return: None
    """
    history = create_or_read_history()

    if n == 0:
        print('\nВыведено 0 запросов, как вы и просили\n')

    elif n < 0:
        print(f'\nЧисло n должно быть положительно\n')

    elif n > history.shape[0]:
        print(f'\nВ истории нет такого количества запросов\nПопробуйте ввести число от 0 до {history.shape[0]}\n')

    else:
        print(f'\nВыведено {n} запросов\n')
        print('_______________________________')
        for i in range(1, n+1):
            row = history.iloc[-i, :].to_dict()
            weather_data = weather_report(row)

            print(f'\n{weather_data}')
        print('_______________________________')


def delete_history() -> None:
    """
    Функция удаляет файл с историей history.csv

    :return: None
    """
    if os.path.exists('history.csv'):
        os.remove('history.csv')
        print('История очищена\n')
    else:
        print('\nУ вас не было истории, вам нечего очищать...\n')


def action(number: int) -> None:
    """
    Функция выполняет действие, указанное пользователем

    :param number: Номер действия
    :return: None
    """
    if number == 1:
        city = get_user_city()
        all_weather_data = get_weather_data_for_city(city)
        weather_data = parse_weather_data(all_weather_data)
        write_data_to_history(weather_data)

        print(weather_report(weather_data))

    elif number == 2:
        city = input('\nВведите название города\n').strip()
        try:
            all_weather_data = get_weather_data_for_city(city)
            weather_data = parse_weather_data(all_weather_data)
            write_data_to_history(weather_data)

            print(weather_report(weather_data))

        except KeyError:
            print('\nВведенного города нет в базе\n')

    elif number == 3:
        history = create_or_read_history()
        if history.shape[0] == 0:
            print('\nВаша история пуста\n')

        else:
            n = int(input('\nВведите число запросов, которые вы хотите увидеть\n'))
            see_last_n_requests(n)

    elif number == 4:
        delete_history()

    elif number == 5:
        raise Exit("Попутного ветра!")

    else:
        print('\nВведенное целое число не отвечает ни за какую функцию\n')


def interface() -> None:
    """
    Функция, реализующая пользовательский интерфейс

    :return: None
    """

    while True:
        try:
            user_input = int(input(TEXT_OF_INTERFACE).strip())

            action(user_input)

        except ValueError:
            print("Введите целое число\n")

        except Exit as error:
            print(error)
            break


class Exit(Exception):
    def __init__(self, message):
        super().__init__(message)


interface()
