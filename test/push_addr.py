import subprocess
import uuid
import netifaces as ni
import requests

interface = subprocess.check_output("ip route get 8.8.8.8 | grep -w dev | awk '{print $5}'", shell=True).decode()[:-1]
print(interface)
ip_addr = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
print(ip_addr)
redir_str = f'http://{ip_addr}:1515'
uuid = uuid.getnode()

requests.post("http://icsl-lambda.ee.columbia.edu:16600/register", data={'uuid': uuid, 'redirect': redir_str})
