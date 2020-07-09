import socket
import sys
import os

_connection = 5
_bytes = 2048

#analysis to take username and password
def analysis_data(data):
    #find index take data is username
    start = data.find('username') + 9
    end = start

    _usname = ''
    for i in data[start:]:
        if i == '&':
            break
        _usname += i
        end += 1
    
    _psword = data[end + 10:]
    return _usname, _psword
    

def get_filepath(req_pack):
    filepath = req_pack.split(' ')[1]      #file name is index 1 near get/post method in http request package
    filepath = filepath[1:]         #erase '/'

    if filepath == '':
        filepath = 'index.html'

    return os.path.join(os.path.dirname(__file__), filepath)

#create a response package to send
def create_response(status, data):
    if status == 200:
        status_code = 'HTTP/1.1 200 OK\r\n'
    elif status == 404:
        status_code = 'HTTP/1.1 404 NOT FOUND\r\n'

    header = 'Content-Type: text/html\r\n'
    header += 'Accept: */*\r\n'
    header += 'Accept-Language: en_US\r\n'
    header += 'Connection: close\r\n\r\n'

    res_header = status_code + header
    return res_header, data

#read file function
def read_file(filename):
    try:
        file_open = open(filename, 'rb')
        data = file_open.read()
        file_open.close()
        response_code = 200

    except FileNotFoundError:
        print('File Not Found')
        response_code = 404
        data = ""

    return response_code, data


def main():
    PORT = 4000

    #create a TCP/IP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #bind the socket to the port
    s.bind(('', PORT))

    #listening for maximum number of queue connection
    s.listen(_connection)

    #get the directory of __file__ (where __file__ is this .py file - main.py)
    cur_path = os.path.dirname(__file__)
    print('Server is listening on PORT: ', PORT)

    stop = 0
    #a forever loop
    while True:
        try:
            #establish connection with client
            client, adr = s.accept()
            print('Client connected:', client)

            #received data
            data = client.recv(_bytes)
            #if not data:
                #print('No data received')
                #break

            #analys request package
            requests = data.decode()

            #requests method (at this project we use only GET and POST method)
            req_method = requests.split(' ')[0]     

            #response path package
            res_path = os.path.join(cur_path, 'index.html')     #link to index.html file
            http_status, data = read_file(res_path)      #data: data in index.html file

            #check method
            if req_method == 'GET' or req_method == 'POST':
                if req_method == 'POST':
                    #analys requests package to find username and password to check
                    usname, psword = analysis_data(requests)

                    if usname == 'admin' and psword == 'admin':
                        #if true then path now is info.html
                        res_path = os.path.join(cur_path, 'info.html')
                        
                    else:
                        #if not true
                        http_status = 404
                        res_path = os.path.join(cur_path, '404.html')
                        
                elif req_method == 'GET':
                    stop += 1

                    #take file_path from requests package
                    file_path = get_filepath(requests)

                    if file_path.find('.html') == -1:
                        res_path = os.path.join(cur_path, file_path)

                #read file
                file_open = open(res_path, 'rb')
                data = file_open.read()
                
                #create respones package to send back
                res_header, res_body = create_response(http_status, data)
                
                #sended
                client.send(res_header.encode())
                client.send(res_body)
                client.close()

        except KeyboardInterrupt:
            s.close()
            sys.exit(0)

        if stop == 4 or http_status == 404:
            break

main()