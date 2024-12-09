# Rock-Paper-Scissors Game

This is a simple Rock-Paper-Scissors game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Players take turns entering their pick between rock, paper, or scissors. The game waits until both players have picked and then decides a win/loss/draw for each player depending on the scenario!

**What you can do so far:**
1. **Start the server:** Run the `server.py` script using `python3 server.py -p PORT_NUMBER`.
2. **Provide a port number:** The server will ask you to provide a port number.
3. **Connect clients:** Run the `client.py` script on two different machines or terminals using `python3 client.py -i SERVER_IP -p PORT_NUMBER`.
4. **Provide an IP address and port number for each client:** The client program will prompt you to provide an IP address and a port number to connect to.
5. **Send messages to the server:** The client program will prompt you to send a message to the server. You can now send messages to the server!
6. **Send moves to the server:** The client program will prompt you to send a move if you select the move option. You can choose from Rock, Paper, or Scissors and the server will receive your move. The server will wait till both players have inputted a move before telling the players who picked which move.

**What went well:**
We had many things go well for us over the course of this project. One of these was our socket mechanism that worked well right away without much hassle. Another aspect of our project that went well was the GUI development. Our GUI came along nicely, and it functioned just the way we wanted it to. We had anticipated needing a lot more work towards our GUI but it was rather simple and quick in the end.

**What we could improve on:**
Throughout the project, we did very well. Up until sprint 3, we had a lot of errors show up. Every time a message was sent over to the other client it wouldn’t be able to understand what was being sent. This was a problem because chat messages wouldn't show up and game logic like winning and losing would get lost. Thankfully, we were able to fix it in the last sprint. We had a couple of things that we needed to improve on towards the end. Starting when the first client joined, it would print to the terminal something along the lines of “Waiting for other player to join to start the game”. Once the other player would join it would say, “Player has joined the game will start” and then it would say “waiting for other player to make their move”. That's what was intended. For some reason, none of that stuff would show in the UI for the first client, but everything would show up on the second client. Another thing that didn’t go well was we forgot to make it so that a third player couldn't join. This obviously messed up the logic. When two players would play, the results would come out, even if the third player wasn't doing anything.

**A brief roadmap of where we would like to take our project:**
Ultimately we would fix the known errors that showed up during our demo. Our TA found the bugs mentioned in our what could be improved section. We also would like to add more to the UI. So maybe when both players enter their moves, display a rock, paper, scissors and then display what both people choose with images. We would also add encryption to our code like the xtra credit asked we just didn’t have the time.

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client
* https://docs.python.org/3/howto/sockets.html
