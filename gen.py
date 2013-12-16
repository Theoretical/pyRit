import requests

def createAccount(region, user, password):
    url = 'http://g4me-hack.de/acc/index.php'
    params = {
        'realm': region,
        'refid': 'ID Only',
        'username': user,
        'password': password,
        'email':    '{0}-{1}@rython.net'.format(region, user),
        'dob_mm': 2,
        'dob_dd': 8,
        'dob_yyyy': 1991
    }

    print params
    print requests.post(url, params)


accountKey = 'rython'
accountPass = 'asdasdzx123'

for i in range(0, 3):
    createAccount('na', '{0}{1}'.format(accountKey, i), accountPass)
