# IPK - Projekt 1 2019/2020

### Autor:
Tomáš Hrúz - <xhruzt00@stud.fit.vutbr.cz>

## Popis riešeného problému:
---

Úlohou bolo vytvoriť HTTP resolver doménových mien, ktorý komunikoval pomocou socketov a bude podporovať operácie **GET** a **POST**


## Moje riešenie:
---

Na vypracovanie som použil jazyk Python a jeho knižnice **socket** na prácu so socketmi, **re** na spracovanie regulárnych výrazov
a **sys** na spracovanie argumentov.

Server sa spustí na "localhost" s príslušným portom, ktorý je zadaný pri spustení. 

### Vytvorí sa socket a server bude čakať na spojenie:

```python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()
```

### Server príjme požiadavku pomocou:

```python
data = conn.recv(1024)
```

Následne dekóduje pomocou funkcie **decode()** správu, vyberie či má obsluhovať **GET** alebo **POST**.
Keď spracuje dáta prilepí k nim hlavičku ktorá sa oddeľuje od tela pomocou **\r\n\r\n** správu zakóduje pomocou funkcie **encode()** a pošle odpoveď klientovi funkciou **sendall()**.

###Server sa spúšťa pomocou:

```makefile
make run PORT=[číslo portu]
```

## Zdroje:
---

<https://realpython.com/python-sockets/#tcp-sockets>
<https://pymotw.com/3/socket/tcp.html>