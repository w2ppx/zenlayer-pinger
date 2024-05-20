# zenlayer-pinger

## Description
A cli-tool to ping any host you want, using 49 (as of repo creation) of zenlayer instances, located in 20+ countries.

## Installation
To install zenlayer-pinger, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/w2ppx/zenlayer-pinger.git
    ```
2. Install requirements
    ```bash
    python3 -m pip install -r requirements.txt
    ```
3. Run the project!
    ```bash
    python3 ping.py --host eepy.today --country TR, US
    ```

## Usage
This project uses [Zenlayer](https://www.zenlayer.com/global-network/performance/) to ping. You can find avaliable locations here, or use --list argument with ping.py, to list all avaliable locations.

If country argument not specified, then the program will ping from all locations.


## Bug reports
This is my first project, so i may have left some bugs.. If you find any, report them to [Issues](https://github.com/w2ppx/zenlayer-pinger/issues)
If you have fixed a bug, or want to add something new to the project, you can send this to [Pull Requests](https://github.com/w2ppx/zenlayer-pinger/pulls)
