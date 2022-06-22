from dotenv import load_dotenv
import requests
import os
from twilio.rest import Client

load_dotenv()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)


headers = {
  'authority': 'tools.usps.com',
  'accept': 'application/json, text/javascript, */*; q=0.01',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'content-type': 'application/json;charset=UTF-8',
  'origin': 'https://tools.usps.com',
  'pragma': 'no-cache',
  'referer': 'https://tools.usps.com/rcas.htm',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
}

spots = {
  1387114: "West New Brighton",
  1380337: "Saint George",
  1383301: "Stapleton",
  1379875: "Rose Bank",
  1378109: "Port Richmond",
  1433897: "Staten Island -- Manor rd",
  1374693: "New Dorp",
  1384858: "Totenvile",
}

def get_dates(id):
  res = requests.post(
    'https://tools.usps.com/UspsToolsRestServices/rest/v2/appointmentDateSearch',
    headers=headers,
    json={
      "numberOfAdults":"1",
      "numberOfMinors":"3",
      "fdbId":str(id),
      "productType":"PASSPORT"
    }
  )

  if res.json().get('dates'):
    dates = [{'date': d, 'm':d[4:6], 'd': d[6:]} for d in res.json().get('dates')]

    return dates
  else:
    return []

def get_times(id, date):
  res = requests.post(
    'https://tools.usps.com/UspsToolsRestServices/rest/v2/appointmentTimeSearch',
    headers=headers,
    json={
      "date":date,
      "productType":"PASSPORT",
      "numberOfAdults":"1",
      "numberOfMinors":"3",
      "excludedConfirmationNumber":[""],
      "fdbId":[str(id)],
      "skipEndOfDayRecord":True
    }
  )
  
  out = []
  for time in res.json()['appointmentTimeDetailExtended']:
    if time['appointmentStatus'] == 'Available':
      out.append(time)

  return out


def find_before(month, day, spots):
  to_check_date = []
  out = []
  for id in spots:
    for date in get_dates(id):
      # print('checking', int(date['m']), '<', month)
      if int(date['m']) < month:
        to_check_date.append([id, date['date']])
        continue
      # print('checking', int(date['m']), '==', month, 'and', int(date['d']), '<=', day)
      if int(date['m']) == month and int(date['d']) <= day:
        to_check_date.append([id, date['date']])

  for to_check in to_check_date:
    checked = get_times(*to_check)
    for found in checked:

      out.append(f"{spots[to_check[0]]} at {found['startTime']} on {found['startDateTime'].split('T')[0]}")

  return out


if __name__ == "__main__":
  found = find_before(7, 2, spots)
  print(found)
  if found:
    message = '\n'.join(found)
    client.messages.create(
       body=message,
       from_=os.environ['TWILIO_FROM_NUMBER'],
       to='+13475591493'
    )