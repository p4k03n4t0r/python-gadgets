# python-gadgets

Diving into the Atelier challenge of LINECTF2021 using Python gadgets (similar to ROP gadgets)

## Setup

```bash
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt

python3 server.py
python3 exploit1.py 0.0.0.0 8081
python3 exploit2.py 0.0.0.0 8081
```

## ROP chain exploit in binaries

In C binaries a way to create exploits in binary is abusing Return Oriented Programming (ROP). When in a C binary a function is called, a new area on top of the stack is allocated dedicated for this function. This area contains all the instructions of this function with at the end an address which points to place from where the function is called. This means when the function is finished, the address at the end allows the program to return to place it was before which could be another function. This can be abused by overwritting this return address with an address to another place in memory, allowing the program to execute in a different way than expected. Often the overridden address points to a libc function, which is the basic library used in binaries containing a lot of common functions used, for example methods for: string manipulation, file I/O, mathematics and [many more](https://www.gnu.org/software/libc/manual/html_mono/libc.html). In exploits often the way to go is using the [execve](https://man7.org/linux/man-pages/man2/execve.2.html) method with `/bin/sh` as an argument, allowing the user to escape the program and to execute shell commands on the machine.

There are a few challenges for this type of exploit, where an important one is the parameters of a function, for example `execve`. When a function is called, the parameters are put in the right registry. There is always a specific order for this depending on the CPU architecture. So when for example `strlen` is called to calculate the length of a string, a pointer to the string is expected in the first registry. So for a function to be called it's important that the right amount of arguments is there and they have the right type (long, char pointer, etc).

When trying to write an exploit this is often a problem, since the registries at the moment of returning to our wanted method for the exploit is different for every program. A way to solve this is using ROP gadgets to create a chain of returns. Libc has a lot of functions available, which can be used to move the values in registries around in such a way that the registries are in the right order for our wanted method. Such functions are called ROP gadgets and can be found with tools like [this one](https://github.com/JonathanSalwan/ROPgadget).

Although Python also follows the principle of return oriented programming, it's not easy to create a similar exploit. When programming in Python we don't write directly to memory addresses in comparison to C, so overwriting the return pointer is not possible. But there are other ways to create exploits in Python, which suprising to me had an interesting familiarity with a ROP chain exploit.

# Atelier
