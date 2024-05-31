from mcstatus import JavaServer
import socket
import time
import docker

#https://pypi.org/project/mcstatus/

class Handler:
    def __init__(self, server_address, container_name, timeout):
        self.server_address=server_address
        self.container_name=container_name
        self.closed = False
        self.listening = False
        self.opening = False
        self.opened = False
        self.PORT = 25565
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.cycles_with_0_players=0

        self.CYCLE_TIME = 30

        div = float(timeout)/self.CYCLE_TIME
        print('div:',div)
        self.MAX_CICLES = int(div)
        if div - int(div) != 0:
            self.MAX_CICLES = int(div)+1

        print('A timeout of',timeout,'seconds was given. This is implemented by checking every',self.CYCLE_TIME,'seconds. The real timeout that will be used is',self.MAX_CICLES*self.CYCLE_TIME)      

    def get_server_players(self):
        players = 0
        try:
            server = JavaServer.lookup(self.server_address)
            status = server.status()
            players = status.players.online
            print('Querying the server for players...',players,'online')
        except (socket.gaierror, ConnectionRefusedError):
            print("Failed to connect to the Minecraft server.")
        except Exception as e:
            print(f"An error occurred while checking the player count of the server: {e}")
        return players
    
    def is_server_open(self):
        try:
            server = JavaServer.lookup(self.server_address)
            status = server.status() # This causes an exception if the server is not open
            return True
        except Exception as e:
            return False
        
    def run(self):

        self.closed = False
        self.listening = False
        self.opening = False
        self.opened = False
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.cycles_with_0_players=0

        while(True):
            if self.is_server_open():
                print('Server is open')
                if self.listening:
                    self.listening = False

                if self.opening:
                    self.opening = False

                if not self.opened:
                    self.opened = True
                    
                # Check if somebody is online
                online_players = self.get_server_players()
                if online_players > 0:
                    self.cycles_with_0_players = 0
                elif not self.closed:
                    self.cycles_with_0_players += 1
                    print('Cycle',self.cycles_with_0_players)
                    if self.cycles_with_0_players >= self.MAX_CICLES:
                        self.cycles_with_0_players = 0
                        self.opened = False
                        self.closed = True
                        self.listening = False
                        self.close_server()
            else:
                print('Server is NOT open')
                if self.closed:
                    self.closed = False

                if not self.listening:
                    try:
                        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.soc.bind(('0.0.0.0',self.PORT))
                        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #to free it immediately for use (the server will need it)
                        print('Socket successfully listening to port',self.PORT,'of',self.server_address)
                        self.listening = True
                        self.soc.listen(1)
                        while True:
                            conn, address = self.soc.accept()
                            with conn:
                                if self.is_server_open():
                                    self.opened = True
                                    self.opening = False

                                #print("Connection attempt detected from",address)
                                res = self.handle_connection(conn)

                                if not self.opening and not self.opened:
                                    if res:
                                        print('Message was requesting to join')
                                        # Open the server
                                        self.opening = True
                                        self.soc.close()
                                        self.open_server()
                                        break
                                    else:
                                        print('Message was a different thing, I guess')
                                else:
                                    conn.close()
                        self.soc.close()
                    except OSError:
                        pass

            if self.opened:
                time.sleep(self.CYCLE_TIME)
            else: #server is opening or something else happened
                time.sleep(1)
    
    # Returns true if at some point the sender sends a specific type of message
    # Returns false if the connection ends without that message type happening
    def handle_connection(self,conn):
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
    # b'$\x00\xf6\x05\x1d{A_HOST}c\xdd\x02\n\x00\x08{MC_USERNAME}'
    # b'\x13\x00\xf6\x05\x0c{A_HOST}c\xdd\x01\x01\x00'

    def open_server(self):
        client = docker.from_env()
        print('Opening server...')
        container = client.containers.get(self.container_name)
        container.start()
        print('Started container',container.id)

    def close_server(self):
        client = docker.from_env()
        print('Closing server...')
        container = client.containers.get(self.container_name)
        container.stop()
        print('Stopped container',container.id)

def main():
    handler = Handler('your sever address','docker container name',601)
    handler.run()

if __name__ == "__main__":
    main()