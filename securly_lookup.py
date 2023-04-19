import requests

file = input('Enter File Name: ')
file_out = input('Enter Output File Name of URL list: ')

with open(file) as f:
    for line in f:
        URL = "https://useast-www.securly.com/application/domains/categories"
        address = str(line)
        headers = {"Cookie":COOKIES_HERE"}
        PARAMS = {'domain':address}

        r = requests.get(url = URL, headers=headers, params = PARAMS)
        data = r.json()
        result = data['type']
        file = open(file_out, "a")

        if result=="success":
            category = data['categories']
            new_line = str(address).rstrip() + '\t' + str(category)
            print(new_line)
            file.write(new_line + '\n')
            file.close()
        else:
            print(str(address).rstrip() + '\t' + str(result))
            file.write(address.rstrip() + '\t' + str(result) + '\n')
            file.close()
