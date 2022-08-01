import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import xlsxwriter

ua = fake_useragent.UserAgent()

def get_links(text):
    data = requests.get(
        url = f"https://hh.ru/search/vacancy?text={text}&from=suggest_post&fromSearchLine=true&area=1&page=1",
        headers={"user-agent":ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        #page_count = int(soup.find("div",attrs={"class":"pager"}).find_all("span",recursive=False)[-1].find("a").find("span").text)
        page_count = 1
    except:
        return
    print(page_count)
    for page in range(page_count):
        try:
            data = requests.get(
            url = f"https://hh.ru/search/vacancy?text={text}&from=suggest_post&fromSearchLine=true&area=1&page={page}",
            headers={"user-agent":ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
            for a in soup.find_all("span",attrs={"class":"g-user-content"}):
                yield f"{a.find('a').attrs['href'].split('?')[0]}"
        except Exception as e:
            print(f"{e}")
        time.sleep(1)

def get_company(link, parsed_data):
    
    pass

def get_resume(link, parsed_data):
    data = requests.get(
        url = link,
        headers={"user-agent":ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        parsed_data["name"] = soup.find("h1", attrs={"data-qa":"vacancy-title"}).text
    except:
        parsed_data["name"] = 0
    try:
        parsed_data["salary"] = soup.find("div", attrs={"data-qa":"vacancy-salary"}).text
    except:
        parsed_data["salary"] = 0
    try:
        parsed_data["experience"] = soup.find("p", attrs={"class":"vacancy-description-list-item"}).text
    except:
        parsed_data["experience"] = ""
    try:
        parsed_data["mode"] = soup.find("p", attrs={"class":"vacancy-description-list-item", "data-qa":"vacancy-view-employment-mode"}).text
    except:
        parsed_data["mode"] = ""
    try:
        parsed_data["skills"] = " ".join([value.text for value in soup.find_all("div", attrs={"class":"bloko-tag bloko-tag_inline", "data-qa":"bloko-tag bloko-tag_inline skills-element"})])
    except:
        parsed_data["skills"] = ""
    return parsed_data

if __name__ == "__main__":
    workbook = xlsxwriter.Workbook('headhunter.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    column = 0
    for item in ["Ссылка", "Название", "Зарплата", "Опыт", "Режим работы", "Навыки"]:
        worksheet.write(row, column, item)
        column += 1
    for link in get_links("python"):
        row += 1
        column = 0
        vacancy = {}
        vacancy["link"] = link
        get_resume(link, vacancy)
        for value in vacancy.values():
            worksheet.write(row, column, value)
            column += 1
    print("finish")
    workbook.close()


