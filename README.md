This file contains the details about the script 'connman.py' and the instructions to use it.

The file defines the class `Connection` that can be imported as:
```python
from connman import Connection
```
The file `connman.py` will have to be in the same directory as the script that imports the class.

An object of type `Connection` can be then defined as follows:
1. Without any arguments
```python
C = Connection()
```
3. Host ip as the only argument
```python
C = Connection("ip")
```
2. Host ip and port as arguments:
```python
C = Connection("ip", port)
```
The following fields have a default value associated with them and are utilized when no argument is supplied to the constructor.
<ul>
	<li>ip: 172.24.0.75</li>
	<li>port: 23</li>
</ul>
<strong>Note: The ip will have to be a string whereas the port will have to be an integer.</strong>


The object of type Connection will have the following functions available to it:

1. send(cmd)
2. justSend(cmd)
3. setup()
4. status(rsp)
5. powerOffPort(port)
6. powerOnPort(port)
7. togglePort(port)
8. refresh()
9. cyclePower(port, t)
10. On1()
11. On2()
12. On3()
13. On4()
14. On5()
15. On6()
16. On7()
17. On8()
18. Off1()
19. Off2()
20. Off3()
21. Off4()
22. Off5()
23. Off6()
24. Off7()
25. Off8()

1. send(cmd)
This function will send the contents of the variable cmd as a string over Telnet to the connected host.
Note that the command does not have to be a string.
The function justSend(cmd) is functionally the same thing as send(cmd), except that it does not monitor
the PSU output to analyze which ports are on and which are off.

2. setup()
This function will take the PSU in the mode from which the ports can be controlled.
This function is designed for internal use rather than being called on an object.

3. status(rsp)
This function takes the PSU output as its input and analyses which ports are on and off.
This function is designed for internal use rather than being called on an object.

4. powerOffPort(port)
This function takes an integer between 0 and 8, inclusive, as input. For an input between 1 and 8, the function, as aptly named, will power the port off.
If 0 is supplied, then all of the ports from 1 to 8 will be turned off.

5. powerOnPort(port)
This function takes an integer between 0 and 8, inclusive, as input. For an input between 1 and 8, the function, as aptly named, will power the port on.
If 0 is supplied, then all of the ports from 1 to 8 will be turned on.

6. togglePort(port)
This function takes an integer between 1 and 8, inclusive, as input. For an input between 1 and 8, the function, as aptly named, will toggle the port.

7. refresh()
This function will restablish the telnet connection with the PSU if more than 120 seconds have passed since the last interaction.
Essentialy, it revives a timed out connection.

8. cyclePower(port, t)
This function will toggle the supplied port, wait for t seconds, and then toggle the port again.

The functions from 9 to 24 behave exactly as their name would suggest.
The ony thing to note is that calling `on` on a port that is already on will not turn the port off and vice versa.
