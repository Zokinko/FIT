import socket
import sys
import re

HOST = '127.0.0.1'  # localhost adresa
PORT = int(sys.argv[1])    # nacitanie PORT z argumentu

def getIP(d):
    try:
        data = socket.gethostbyname(d)
        ip = str(data)
        return ip
    except Exception:
        return False

def getHost(ip):
    try:
        data = socket.gethostbyaddr(ip)
        host = str(data[0])
        return host
    except Exception:
        return False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
while True:
    conn, addr = s.accept()
    while True:
        data = conn.recv(1024) #prijatie spravy
        if not data:
            wrong = "HTTP/1.1 404 Not Found\r\n\r\n"
            wrong = wrong.encode()
            conn.sendall(wrong)
            break
        txt = data.decode("utf-8") #prisiel socket
        get_chooser = re.search("^GET ",txt) #ma sa vykonavat GET 
        post_chooser = re.search("^POST ",txt)#ma sa vykonat POST

        if (get_chooser): #vykonavanie GET
            resolver = re.search("^GET /resolve\?",txt)
            if not resolver: #kontrola ci je spravny request
                wrong = "HTTP/1.1 400 Bad request\r\n\r\n"
                wrong = wrong.encode()
                conn.sendall(wrong)
                break
                
            txt = txt.split(" ") #rozdelenie socketu na casti
            txt = txt[1].split("=")
            typ = txt[2] #typ

            pomocna = re.search("\\\\&", txt[1])
            if pomocna:
                add = txt[1].split("\\")
            else:
                add = txt[1].split("&")
            add = add[0] #adresa

            if typ == 'A':#spracovanie name to ip
                x = re.search("^([a-z]+\.)+[a-z]+$", add)#kontrola spravnosti adresy
                if (x):
                    a = getIP(add)
                    a = str(a)
                    if a != "False":
                        socketout1 ="HTTP/1.1 200 OK\r\n\r\n"+add+":"+typ+"="+a+"\r\n"
                        socketout1 = socketout1.encode()	#bytes
                        conn.sendall(socketout1) #zaslanie spat na vystup
                        break
                    else:
                        wrong = "HTTP/1.1 404 not found\r\n\r\n"
                        wrong = wrong.encode()
                        conn.sendall(wrong)
                        break
                else:
                    wrong = "HTTP/1.1 400 Bad request\r\n\r\n"
                    wrong = wrong.encode()
                    conn.sendall(wrong)
                    break
            elif typ == 'PTR':#spracovanie ip to name
                y = re.search("^[0-9]+.[0-9]+.[0-9]+.[0-9]+$", add)
                if (y):
                    b = getHost(add)
                    b = str(b)
                    if b != "False":
                        socketout2 ="HTTP/1.1 200 OK\r\n\r\n"+add+":"+typ+"="+b+"\r\n"
                        socketout2 = socketout2.encode()
                        conn.sendall(socketout2) #zaslanie spat na vystup
                        break
                    else:
                        wrong = "HTTP/1.1 404 not found\r\n\r\n"
                        wrong = wrong.encode()
                        conn.sendall(wrong)
                        break
                else:
                    wrong = "HTTP/1.1 400 Bad request\r\n\r\n"
                    wrong = wrong.encode()
                    conn.sendall(wrong)
                    break
        elif  post_chooser: #spracovanie POST
            querer = re.search("^POST /dns-query\s",txt)
            if not querer:
                wrong = "HTTP/1.1 400 Bad request\r\n\r\n"
                wrong = wrong.encode()
                conn.sendall(wrong)
                break
            txt = txt.split("\r\n")
            top = len(txt) #pocet prvkov pola
            i= 7 #tu zacinaju adresy
            socketout3 = ""
            notFoundFound = True
            while i < top-1: #prehladavanie adries
                txt[i].replace(" ", "")
                address = txt[i].split(":")
                print (txt[i])
                z = re.search("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:PTR$", txt[i])
                q = re.search("^([a-z]+\.)+[a-z]+:A$", txt[i])
                if (q):# name to ip
                    finalIp = getIP(address[0])
                    if finalIp:
                        socketout3 += address[0]+":A="+finalIp+"\r\n"
                        notFoundFound = False
                    else:
                        notFound = True
                    i+= 1
                elif (z):#ip to name
                    finalHost = getHost(address[0])
                    if finalHost:
                        socketout3 += address[0]+":PTR="+finalHost+"\r\n"
                        notFoundFound = False
                    else:
                        notFound = True
                    i+= 1
                else:
                    notFoundBR = True
                    i+= 1
            if notFoundFound and notFound:
                wrong = "HTTP/1.1 404 not found\r\n\r\n"
                wrong = wrong.encode()
                conn.sendall(wrong)
                break
            elif i == top-1: #v pripade ze to prejdeme cele moze byt OK
                socketout3 = "HTTP/1.1 200 OK\r\n\r\n" + socketout3
                socketout3 = socketout3.encode()
                conn.sendall(socketout3)
                break
        else:
            wrong = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            wrong = wrong.encode()
            conn.sendall(wrong)
            break

    conn.close()
conn.close()