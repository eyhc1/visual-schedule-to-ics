import requests
from bs4 import BeautifulSoup
import getpass


# replace "YOUR UW NET ID" and "YOUR PASSWORD"to your own UW netID and password
def get_schedule(uwnetid="YOUR UW NET ID", password="YOUR PASSWORD"):
    weburl = 'https://sdb.admin.uw.edu/sisStudents/UWNetID/vschedule.aspx?Q=2'  # link to visual schedule
    session = requests.Session()
    r = session.get(weburl)
    soup = BeautifulSoup(r.text, 'html.parser')
    # inspired from https://github.com/ApolloZhu/INFO200/blob/master/script/cec.py
    if 'YOUR UW NET ID' in uwnetid or 'YOUR PASSWORD' in password:
        uwnetid = input("Your UW NetID? ")
        # password = input('Enter your password: ')
        password = getpass.getpass('Enter your password: ')  # comment out this line and uncomment the previous one if
        # you run the program from PyCharm
    if soup.find("h1", text="UW NetID sign-in"):
        print('attempt to sign in....')
        path = soup.find(id='idplogindiv')['action']
        url = f"https://idp.u.washington.edu{path}"
        data = {
            "j_username": uwnetid,
            "j_password": password,
            "_eventId_proceed": "Sign in"
        }
        fill = session.post(url, data=data)
        soup = BeautifulSoup(fill.text, 'html.parser')
        url = soup.find("form")['action']
        data = {
            "RelayState": soup.find("form").find("input", attrs={"name": "RelayState"})["value"],
            "SAMLResponse": soup.find("form").find("input", attrs={"name": "SAMLResponse"})["value"],
        }
        session.post(url, data=data)
        soup = BeautifulSoup(session.get(weburl).text, 'html.parser')
    if 'Visual Schedule' in soup.find("h1").text:
        print('login complete! looking at your classes')
        block_lists = soup.find_all("td", {"colspan": "1"})
        week_days = ["MO", "TU", "WE", "TH", "FR"]
        day_count = 0
        for elements in block_lists:
            if day_count != 5:
                if len(elements) > 1:
                    field = []
                    for items in elements:
                        if '<br/>' not in str(items):
                            field.append(items)
                    field.append(elements.get("title"))
                    field.append(week_days[day_count])
                    print('found ' + field[0] + ' from the page!')
                    export_ics(f, field)
                day_count += 1
            else:
                day_count = 0
    else:
        print("wrong netID/password or the page you looked for is not correct!")


def export_ics(file, course_info):
    print("export " + course_info[0] + " to your ics file")
    start_date = str(20210305)  # the day when your classes should start, format as YYYYMMDD
    end_date = str(20210601)  # the day when your classes should end, format as YYYYMMDD
    time = course_info[2].split("-")
    print(course_info[2])
    hr_1 = ''
    min_1 = ''
    hr_2 = ''
    min_2 = ''
    t = time[0]
    if len(t) == 3:
        hr_1 = pm_convert(t[:1])
        min_1 = t[1:]
    elif len(t) == 4:
        hr_1 = t[:2]
        min_1 = t[2:]
    t = time[1]
    if len(t) != 4:
        hr_2 = pm_convert(t[:1])
        min_2 = t[1:3]
    elif len(t) == 4:
        hr_2 = t[:2]
        min_2 = t[2:]
    file.write('BEGIN:VEVENT\n')
    file.write('DTSTART:' + start_date + 'T' + hr_1 + min_1 + '00\n')
    file.write('RRULE:FREQ=WEEKLY;BYDAY=' + course_info[3] + ';UNTIL=' + end_date + 'T230000Z\n')
    file.write('DTEND:' + start_date + 'T' + hr_2 + min_2 + '00\n')
    file.write('SUMMARY:' + course_info[0] + '\n')
    file.write('DESCRIPTION:' + course_info[1] + '\n')
    file.write('END:VEVENT\n')


def pm_convert(time):
    print("correcting to .ics time...")
    result = int(time)
    if result < 8:
        print('found this this pm time, converting...')
        result += 12

    if result < 10:
        return '0' + str(result)
    else:
        return str(result)


if __name__ == '__main__':
    f = open('visual_schedule.ics', 'w')  # name of your ics file generated
    f.write('BEGIN:VCALENDAR\n')
    get_schedule()
    f.write('END:VCALENDAR')
    print('DONE!')
