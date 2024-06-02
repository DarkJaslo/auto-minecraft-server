# minecraft-server-handler

### Disclaimer!

This program is most probably scuffed, and checks edge cases poorly/not at all. Consider this an idea (that should work most of the time in local, simple cases), but not a reliable service.

### Idea

This is a script meant to be run 24/7 on the server side, specifically on the same machine that runs the Minecraft server.

- If the Minecraft server is **open** with no players for some timeout, it is closed.
- If the Minecraft server is **closed**, this script listens to some port (other than the Minecraft one) and accepts requests that ask it to open the server. Possible implementations to send them include a web page or a Discord bot, to name a few.

The result is a Minecraft server that only runs when needed, with (hopefully) no interaction with the server admin/s. 

This is specially useful in low-power machines or machines that were already running other services 24/7.

### Build and run

This is intended to run with Docker (help in run.txt). First, don't forget to:

1. Specify the server address and Minecraft server Docker container name in the server script (_serverhandler.py_). Specify the port in the Handler's constructor (default is 12345)
2. In script.py, set the server address and port the same as in serverhandler.py. Remember that the default port is 12345.

To build the image:
```shell
docker build -t automcserver .
```

To run the container, change _port_ for the port number you want to use (same as in the script).
```shell
docker run -d \
  -it \
  -p port:port \
  --name automcserver \
  --restart=unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  automcserver
```

And done! You can test it with the simple Flask page-example I included here:

```shell
pip install flask mcstatus
python3 script.py
```
This will host it in localhost (see the terminal). Copy the link on your browser of choice and test it.

If you look at the code, the current message to open the server is just the string "Open the server". Change it if you want to, both in the server and the page/request sender of your choice.

### Sending requests

The server code is only half of the whole thing. We need to run this all the time, with another external agent being the one that sends requests.

#### Web page

You can host a simple web page that displays whether the server is open or not (FYI, it can be done with the Handler class provided in the Python script), and has a button that when clicked, sends a request to open the server.

#### Discord bot

A different approach could be a Discord bot that, given the appropriate commands, displays the server status or sends the request to open the server.

#### And many more
As long as you send the request...