import argparse
import requests
import threading
import pycountry

def ping(host, countries):
    if not host.replace('.', '').isnumeric():
        url = f'https://cloudflare-dns.com/dns-query?name={host}&type=A'
        host = requests.get(url, headers={'Referer': 'https://console.zenlayer.com', 'Accept': 'application/dns-json'}).json()['Answer'][0]['data']

    locations = []
    name_location = []
    list = requests.get('https://console.zenlayer.com/lgApi/api/devices').json()
    for i in list:
        name = i['name']
        name = name.replace(' ', '_').replace('(', '').replace(')', '').lower().replace(',', '')
        name_location.append({'name': name, 'normalized': i['name']})
        locations.append(name)

    threads = []
    for location in locations:
        if not countries or location[:2].upper() in countries:
            thread = threading.Thread(target=check_ping, args=(host, location, name_location))
            thread.start()
            threads.append(thread)

    if not threads:
        print('No nodes with that country. Exiting.')
    else:
        for thread in threads:
            thread.join()

def check_ping(host, location, name_location):
    for i in name_location:
        if i['name'] == location:
            location_n = i['normalized']
            break

    payload = {"query_vrf": "global", "query_location": location, "query_type": "ping", "query_target": host}
    response = requests.post(f'https://console.zenlayer.com/lgApi/api/query/', json=payload)
    if response.text.startswith('{"output":'):
        try:
            ping = response.json()['output'].split('min/avg/max')[1].split('/')[2]
            loss = response.json()['output'].split('received,')[1].split('%')[0]
        except:
            if 'Error connecting to' in response.json()['output']:
                status = 'Node offline'
            elif 'none is not an allowed value' in response.json()['output']:
                status = 'Error on node'
            else:
                status = 'Error on node'
            ping = '0 ms'
            loss = '100'
    else:
        status = 'Error on node'
        ping = '0 ms'
        loss = '100'

    if location_n[:2].isalpha():
        location_n = f'{pycountry.countries.get(alpha_2=location_n[:2]).flag} {location_n[:2]}'

    print(f'{location_n} - {status} - {ping} - {loss}% loss {"- CACHED" if "cached" in response.json() and response.json()["cached"] else ""}')

def list_countries():
    list = requests.get('https://console.zenlayer.com/lgApi/api/devices').json()
    countries = []
    for i in list:
        countries.append(i['name'])
    print(countries)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ping tool')
    parser.add_argument('--host', help='Host to ping')
    parser.add_argument('--country', nargs='+', help='Countries to ping from')
    parser.add_argument('--list', action='store_true', help='List all nodes')
    args = parser.parse_args()
    if args.list:
        list_countries()
        raise SystemExit
    if not args.host:
        print('Please provide a host to ping. Exiting.')
        raise SystemExit
    ping(args.host, args.country)
