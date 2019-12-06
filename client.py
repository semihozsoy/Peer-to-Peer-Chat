import socket, sys, threading, json, time, datetime

# Connect to server(service) by given IP and Port
udpConnectionSettings = ('localhost', 5000)

# Storage for online list on client side.
onlineList = {}

# Client username (self)
clientUsername = ''


# Login to server and send "show me on online list" request immediately
# [Req #2.1.0-C]
def loginToServer(udpConnection, clientUsername):
    request = {}
    request['type'] = 'login'
    request['username'] = clientUsername
    data = json.dumps(request)
    response = sendMessageToServer(udpConnection, data)
    return response

def saveMessageIntoTextFile(message):
    now = datetime.datetime.now()
    timeValue = str(now.hour) + ":" + str(now.minute)
    with open("messages.txt", "a") as log:
        log.writelines(["[",timeValue,"]", message, "\n"])

# Logout from the server (delete my username and IP from the list)
def logoutFromServer(udpConnection, clientUsername):
    request = {}
    request['type'] = 'logout'
    request['username'] = clientUsername
    data = json.dumps(request)
    response = sendMessageToServer(udpConnection, data)
    print("\n")
    print("------[LOGGED OUT!]-----")
    print("\n")
    sys.exit()
    tcpConnection.close()

# Send message to server (e.g. show me on online list) by UDP
def sendMessageToServer(udpConnection, data):
    udpConnection.send(data.encode())
    response, t = udpConnection.recvfrom(1000)
    return response.decode()

# Connect to destination peer and communicate by TCP
def connectToPeer(peerHost, udpConnection, clientUsername):
    tcpConnection.connect((onlineList[peerHost][0], 5001))
    threading.Thread(target=readMessage, args=(tcpConnection, udpConnection, clientUsername)).start()
    threading.Thread(target=writeMessage, args=(tcpConnection, udpConnection, clientUsername)).start()

# Listen and connect if there is any connection request
# Listen for TCP connections on port 5001.
def waitForPeer(udpConnection, clientUsername):
    tcpConnection.bind(('localhost', 5001))
    tcpConnection.listen(2)
    print("Waiting for P2P connection...")
    while True:
        c, addr = tcpConnection.accept()
        threading.Thread(target=readMessage, args=(c, udpConnection, clientUsername)).start()
        threading.Thread(target=writeMessage, args=(c, udpConnection, clientUsername)).start()

# Receive message
def readMessage(s, udpConnection, clientUsername):
    global isClosed
    while True:
        if isClosed:
            receivedMessage = s.recv(100).decode()
            if not receivedMessage: break
            print("\r"+ receivedMessage + "\n"+clientUsername+': ', end="", flush=True)
            saveMessageIntoTextFile(receivedMessage)
            if receivedMessage == "/back":
                isClosed = 0;
                chatInsideMenu()
                init(udpConnection, clientUsername)

# Send message
def writeMessage(s, udpConnection, clientUsername):
    global isClosed
    while True:
        if isClosed:
            sentMessage = input(clientUsername+': ')
            s.send((clientUsername+': '+sentMessage).encode())
            saveMessageIntoTextFile(clientUsername+': '+sentMessage)
            if sentMessage == "/back":
                isClosed = 0;
                chatInsideMenu()
                init(udpConnection, clientUsername)

# Show initial online list
def showOnlineList(udpConnection, clientUsername):
    global onlineList
    refreshedList = loginToServer(udpConnection, clientUsername)
    refreshedList = json.loads(refreshedList)
    onlineList = refreshedList
    print('\n')
    print('------[ONLINE USERS]------')
    for name,ip in refreshedList.items():
        print('| '+ name + ' : ' + ip[0])
    print('--------------------------')

# Command list
def commandList():
    print('\n')
    print('------[COMMANDS]------')
    print('- Enter [1] to connect to peer')
    print('- Enter [2] to wait P2P connection')
    print('- Enter [3] to logout')
    print('- Enter [4] to refresh online user list')
    print('- /back command is closing the active chat session and enabling the menu')
    print('**** Your messages automatically saved into [messages.txt] file')
    print('--------------------------')
    print('\n')

# /back command triggering the list
def chatInsideMenu():
    print('\n')
    print('------[COMMANDS]------')
    print('Enter [1] to connect to another peer')
    print('Enter [3] to logout')
    print('Enter [4] to refresh online user list and get commands list')
    print('--------------------------')
    print('\n')

# Initial commands
def init(udpConnection, clientUsername):
    while True:
        ch = input("Enter choice:")
        if ch == "1":
            peerHost = input("Enter username to chat: ")
            connectToPeer(peerHost, udpConnection, clientUsername)
            break
        elif ch == "2":
            waitForPeer(udpConnection, clientUsername)
            break
        elif ch == "3":
            logoutFromServer(udpConnection, clientUsername)
        elif ch == "4":
            showOnlineList(udpConnection, clientUsername)
            continue
        else:
            print("Option is not exist")
            continue

if __name__ == '__main__':
    udpConnection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpConnection.connect(udpConnectionSettings)
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientUsername = input("Enter your username: ")
    isClosed = 1;

    showOnlineList(udpConnection, clientUsername)
    commandList()
    init(udpConnection, clientUsername)
