# Peer to Peer Chat
# CMP2204 Term Project
# Mert Gonul - Semih Ozsoy
# Tested and running on OS X

import socket, json, sys, time

# [Req. # 2.1.0-A] P2PC Service Listener shall listen for UDP broadcast messages on port 5000.*
server_addr = ('localhost', 5000)

onlineList = {}

def loginRequest(udpConnection, receivedJsonData):
    name = receivedJsonData['username']
    addr = receivedJsonData['addr']
    onlineList[name] = addr
    udpConnection.sendto(json.dumps(onlineList).encode(), addr)
    print('[%s] logged in and IP is %s' % (name, addr))

# [Req. # 2.1.0-F]
def logoutRequest(udpConnection, receivedJsonData):
    name = receivedJsonData['username']
    addr = receivedJsonData['addr']
    del onlineList[name]
    udpConnection.sendto(b'logout success', addr)
    print('[%s] logged out and IP is %s' % (name, addr))

# Route given type to correct function
Router = {
    'login' : loginRequest,
    'logout': logoutRequest,
}

# [Req. # 2.1.0-B]
if __name__ == '__main__':
    udpConnection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpConnection.bind(server_addr)
    print('Server listening!')
    try:
        while True:
            data, addr = udpConnection.recvfrom(1000)
            data = data.decode()
            receivedJsonData = json.loads(data)
            receivedJsonData['addr'] = addr
            Router[receivedJsonData['type']](udpConnection, receivedJsonData)
    except Exception as e:
        print(e)
    except KeyboardInterrupt as e:
        print('Server closed!')
    finally:
        udpConnection.close()
