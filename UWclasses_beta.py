import os

import requests
from bs4 import BeautifulSoup
import getpass


def main():
    # replace "YOUR UW NET ID" and "YOUR PASSWORD"to your own UW netID and password
    net_id = 'YOUR UW NET ID'
    password = 'YOUR PASSWORD'
    # if you don't want to have input everytime you run replace all the variables below
    qtr = input("Which quarter do you which to extract (winter, spring, summer, or autumn)? ")
    qtr_start = input("First day of your quarter, formatted as YYYYMMDD: ")
    qtr_end = input('Last day of your quarter, formatted as YYYYMMDD: ')
    try:
        get_schedule(net_id, password, qtr, qtr_start, qtr_end)
    except Exception as e:
        print('Error:', e)
    os.system('pause')  # so that the program won't shutdown itself when running without an ide


def get_schedule(uwnetid, pass_, quarter, day_start, day_end, filename='visual_schedule.ics'):
    qtr = {
        "winter": "1",
        "spring": "2",
        "summer": "3",
        "autumn": "4",
        "": ""
    }
    assert quarter.lower() in qtr, 'your input for quarter is incorrect! Please check your input!\nThe valid inputs ' \
                                   'are: winter, spring, summer, autumn '
    assert len(day_start) == 8 and len(day_end) == 8, 'Invalid dates input!'
    weburl = 'https://sdb.admin.uw.edu/sisStudents/uwnetid/schedule.aspx?Q=' + qtr[
        quarter.lower()]  # link to schedule
    session = requests.Session()
    session.trust_env = None  # correctly handle the case with Shadowsocks turned on
    r = session.get(weburl)
    soup = BeautifulSoup(r.text, 'html.parser')
    # inspired from https://github.com/ApolloZhu/INFO200/blob/master/script/cec.py
    if soup.find("h1", text="UW NetID sign-in"):
        if 'YOUR UW NET ID' in uwnetid or 'YOUR PASSWORD' in pass_:
            uwnetid = input("Your UW NetID? ")
            # password = input('Enter your password: ')
            pass_ = getpass.getpass('Enter your password: ')  # comment out this line and uncomment the previous one
            # if you run the program from PyCharm
        print('attempt to sign in....')
        path = soup.find(id='idplogindiv')['action']
        url = f"https://idp.u.washington.edu{path}"
        data = {
            "j_username": uwnetid,
            "j_password": pass_,
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
    if 'Class Schedule' in soup.find("h1").text:
        table = soup.find('tbody', {'class': 'sps-data'}).find_all('tr')
        class_name, meet_days, meet_time, class_loc, class_instru = "", "", "", "", ""
        f = open(filename, 'w', encoding='utf-8')  # name of your ics file generated, default is 'visual_schedule.ics'
        f.write('BEGIN:VCALENDAR\n'
                'VERSION:2.0\n'
                'PRODID:-//UW Schedule parser by eyhc1\n'
                'BEGIN:VTIMEZONE\n'
                'TZID:America/Los_Angeles\n'
                'BEGIN:STANDARD\n'
                'DTSTART:19710101T020000\n'
                'TZOFFSETTO:-0800\n'
                'TZOFFSETFROM:-0700\n'
                'TZNAME:PST\n'
                'RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\n'
                'END:STANDARD\n'
                'BEGIN:DAYLIGHT'
                'DTSTART:19710101T020000\n'
                'TZOFFSETTO:-0700\n'
                'TZOFFSETFROM:-0800\n'
                'TZNAME:PDT\n'
                'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU\n'
                'END:DAYLIGHT\n'
                'END:VTIMEZONE\n')
        for child in table:
            class_contents = child.text.splitlines()
            if "To be arranged" in class_contents:
                print(class_contents[2], "has no meeting day/time specified, ignored")
                continue
            for data in class_contents:
                if ('M' in data or 'T' in data or 'W' in data or 'Th' in data or 'F' in data) and len(data) < 5:
                    meet_days = data
                elif '-' in data:
                    meet_time = data
                elif len(data) > 0:
                    if data[-1] in '1234567890':
                        class_loc = data
            if len(class_contents) > 2:
                class_info = [class_contents[2], meet_days, meet_time, class_loc, class_instru]
                export_ics(f, class_info, day_start, day_end)
        f.write('END:VCALENDAR')
        print('schedule successfully exported as', filename)
    else:
        print("wrong netID/password or the page you looked for is not correct!")


def export_ics(file, course_info, start_date, end_date):
    print("export " + course_info[0] + " to your ics file")
    wkday = {
        "M": "MO",
        "T": "TU",
        "W": "WE",
        "h": "TH",
        "F": "FR"
    }
    days = list(course_info[1])
    if days.count("T") == 2:
        days.remove("T")
    byday = ''
    for day in days:
        try:
            byday += wkday[day] + ','
        except KeyError:
            print('ignore invalid key', day)
    file.write('BEGIN:VEVENT\n')
    file.write('RRULE:FREQ=WEEKLY;BYDAY=' + byday[:-1] + ';UNTIL=' + end_date + 'T230000Z\n')
    time = course_info[2].replace('\xa0', '').split("-")
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
    file.write('DTSTART;TZID=America/Los_Angeles:' + start_date + 'T' + hr_1 + min_1 + '00\n')
    file.write('DTEND;TZID=America/Los_Angeles:' + start_date + 'T' + hr_2 + min_2 + '00\n')
    file.write('SUMMARY:' + course_info[0] + '\n')
    file.write('DESCRIPTION:' + course_info[3].lower() + '\n')
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
    main()
