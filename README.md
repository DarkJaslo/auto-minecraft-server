# auto-minecraft-server

### Disclaimer!
This is still **work in progress!!** Don't expect it to work and run well.

### Idea and purpose
This is a script that manages your Minecraft server efficiently. What does this exactly mean?

It closes the server when it has been empty for a few minutes, and opens it when people try to connect. It does this via listening to the Minecraft 25565 port when the server is closed.

It assumes you use Docker, and in the global variables at the beginning of the code you can change the name to your server's container. However, it is easily modifiable as it only interacts with docker in the open_server() and close_server() functions.

This is of course only useful if you can run at least the script 24/7.

### Disclaimer (part two)

This is just a script I made in less than an afternoon. It is bad, ugly, long, ultra-indented, inefficient, uses magic to work and probably violates international law.

It can be improved in many ways (starting by fitting everything into a class), which I intend to do at some point.
