import argparse
import requests
import threading
import pycountry

def ping(host, countries):
    global avg_ping, avg_loss
    if not host.replace('.', '').isnumeric():
        url = f'https://cloudflare-dns.com/dns-query?name={host}&type=A'
        host = requests.get(url, headers={'Referer': 'https://console.zenlayer.com', 'Accept': 'application/dns-json'}).json()
        if 'Answer' in host:
            host = host['Answer'][0]['data']
        else:
            print("Couldn't resolve host via CloudFlare. Exiting.")
            raise SystemExit

    locations, name_location, avg_ping, avg_loss = [], [], [], []
    list = requests.get('https://console.zenlayer.com/lgApi/api/devices')
    if list.status_code != 200:
        print('Error while fetching nodes. Exiting.')
        raise SystemExit
    for i in list.json():
        name = i['name'].replace(' ', '_').replace('(', '').replace(')', '').lower().replace(',', '')
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
        print(f'Average ping: {sum(avg_ping) // len(avg_ping)} ms - Average loss: {sum(avg_loss) // len(avg_loss)}%')
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
            loss = int(response.json()['output'].split('received,')[1].split('%')[0])
        except:
            if 'Error connecting to' in response.json()['output']:
                status = 'Node offline'
            else:
                status = 'Error on node'
            ping = '0 ms'
            loss = 100
        status = 'Online' if loss < 50  else 'Offline'
        if location_n[:2].isalpha():
            location_n = f'{pycountry.countries.get(alpha_2=location_n[:2]).flag} {location_n[2:]}'
        print(f'{location_n} - {status} - {ping} - {loss}% loss {"- CACHED" if "cached" in response.json() and response.json()["cached"] else ""}')
        avg_ping.append(int(ping.split('.')[0].replace('ms', ''))), avg_loss.append(loss)
    else:
        print(f'Error while pinging from location: {location_n} \n Recieved: {response.text}')

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
