# Cowrie on this machine only

Cowrie is the scripted baseline (BSD-3-Clause, https://github.com/cowrie/cowrie). Install it from that repository when you are ready this week. This project does not start Cowrie for you.

1. Create a virtual environment and install Cowrie's own requirements, following Cowrie's README, on this computer.
2. Copy the keys in `configs/cowrie.cfg.example` into `etc/cowrie.cfg`.
3. Leave SSH enabled and Telnet disabled. Both listen addresses in the example are `127.0.0.1`.
4. If you run Cowrie in Docker, publish the port as `127.0.0.1:2222:2222`. Do not publish it on every interface, and do not add a router forward for port 2222.
5. Put the simulator account from Cowrie's own `etc/userdb.txt` into `.env` as `COWRIE_USER` and `COWRIE_PASSWORD`.
6. Start Cowrie only after the config file shows `127.0.0.1`.
7. Keep Cowrie's JSON log on this machine. Do not point an output plugin at an external service.

The replay client in this repository dials `127.0.0.1` only. If Cowrie is not installed yet, `scripts/04_replay.py` records a skip for the Cowrie row and continues with the other systems.
