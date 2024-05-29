from mcstatus import JavaServer
import socket
import time
import docker

SERVER_ADDRESS = 'enter server address'
CONTAINER_NAME = 'enter container name'

#https://pypi.org/project/mcstatus/

def get_server_players():
    players = -1
    try:
        server = JavaServer.lookup(SERVER_ADDRESS)
        status = server.status()
        print(f"The server has {status.players.online} players online.")
        players = status.players.online
    except (socket.gaierror, ConnectionRefusedError):
        print("Failed to connect to the Minecraft server.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return players
    
def is_server_open():
    try:
        server = JavaServer.lookup(SERVER_ADDRESS)
        status = server.status()
        return True
    except Exception as e:
        return False

def main():

    closed = False
    listening = False
    opening = False
    opened = False
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    cycles_with_0_players = 0
    MAX_CICLES = 20
    CYCLE_TIME = 30

    while(True):
        if is_server_open():
            print('Server is open')
            if listening:
                listening = False

            if opening:
                opening = False

            if not opened:
                opened = True
                
            # Check if somebody is online
            online_players = get_server_players()
            if online_players > 0:
                cycles_with_0_players = 0
            elif not closed:
                cycles_with_0_players += 1
                print('Cycle',cycles_with_0_players)
                if cycles_with_0_players >= MAX_CICLES:
                    cycles_with_0_players = 0
                    opened = False
                    closed = True
                    listening = False
                    close_server()
        else:
            print('Server is NOT open')
            if closed:
                closed = False

            if not listening:
                try:
                    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    soc.bind(('0.0.0.0',25565))
                    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    print('Socket binding operation completed')
                    listening = True
                    soc.listen(1)
                    while True:
                        conn, address = soc.accept()
                        with conn:
                            if is_server_open():
                                opened = True
                                opening = False

                            #print("Connection attempt detected from",address)
                            res = handle_connection(conn)

                            if not opening and not opened:
                                if res:
                                    print('Message was requesting to join')
                                    # Open the server
                                    opening = True
                                    soc.close()
                                    open_server()
                                    break
                                else:
                                    print('Message was a different thing, I guess')
                            else:
                                conn.close()
                    soc.close()
                except OSError:
                    pass
                    #print('Connected with ' + address[0] + ':' + str(address[1]))
            # Listen to port 25565

        if opened:
            time.sleep(CYCLE_TIME)
        else:
            time.sleep(1)

def handle_connection(conn):
    got_join_req = False
    try:
        while True:
            data = conn.recv(1024)
            join_req = False
            if not data:
                break
            
            print('Received message')
            join_req = str(data).find('$')  # I literally don't understand why this works
            if join_req == -1:
                got_join_req = True
                break

            return join_req >= 0
            
    except Exception as e:
        print('Error handling connection:',e)
    finally:
        conn.close()
        return got_join_req
# b'$\x00\xf6\x05\x1d{A_HOST}c\xdd\x02\n\x00\x08{MC_USERNAME}' -> wants to join
# b'\x13\x00\xf6\x05\x0c{A_HOST}c\xdd\x01\x01\x00' -> useless

def open_server():
    client = docker.from_env()
    print('Opening server...')
    container = client.containers.get(CONTAINER_NAME)
    container.start()
    print('Started container',container.id)

def close_server():
    client = docker.from_env()
    print('Closing server...')
    container = client.containers.get(CONTAINER_NAME)
    container.stop()
    print('Stopped container',container.id)

if __name__ == "__main__":
    main()