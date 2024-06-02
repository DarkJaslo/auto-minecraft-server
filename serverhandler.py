from mcstatus import JavaServer #https://pypi.org/project/mcstatus/
import socket
import time
import docker

class Handler:
    def __init__(self, server_address, container_name, timeout):
        self.server_address=server_address
        self.container_name=container_name
        self.PORT = 12345 #some 16-bit number
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

    def open_server(self):
        client = docker.from_env()
        print('Opening server...')
        container = client.containers.get(self.container_name)
        container.start()
        while not self.is_server_open():
            pass

    def close_server(self):
        client = docker.from_env()
        print('Closing server...')
        container = client.containers.get(self.container_name)
        container.stop()
        print('Stopped container',container.id)

    def run(self):
        while True:
            if self.is_server_open():
                self.track_open()
            else:
                self.listen()

    # Pre: server is open
    def track_open(self):
        print('tracking if the server is open...')
        while self.is_server_open():
            players = self.get_server_players()
            if players == 0:
                self.cycles_with_0_players +=1
                if self.cycles_with_0_players >= self.MAX_CICLES:
                    self.close_server()
                    break
            else:
                self.cycles_with_0_players = 0
            time.sleep(self.CYCLE_TIME)
        self.cycles_with_0_players = 0

    def listen(self):
        print('Listening to port',self.PORT,'...')
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.soc.bind(('0.0.0.0',self.PORT))
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #to free it immediately after use
        self.soc.listen(1)
        while True:
            conn, _ = self.soc.accept()
            print('Accepted a connection')
            with conn:
                if self.is_server_open():
                    self.soc.close()
                    break

                print('Handling a connection')
                result = self.handle(conn)
                if result:
                    print('The message requested to open the server')
                    self.open_server()
                    self.soc.close()
                    break

    def handle(self, conn):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    return False
                
                msg = data.decode('utf-8')
                print('Message:',msg)
                if msg == "Open the server":
                    return True
        except Exception as e:
            print('Error handling connection:',e)
            return False


def main():
    handler = Handler('your server address','your Minecraft server Docker container name',600) # 600 is the timeout in seconds
    handler.run()

if __name__ == "__main__":
    main()