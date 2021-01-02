# Naive-FTP

A simple FTP server and client, written in Python, using pure `socket` module.

## Table of Contents

- [Naive-FTP](#naive-ftp)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [0. Prerequisities](#0-prerequisities)
    - [1. Installation](#1-installation)
      - [1.1 GUI support](#11-gui-support)
    - [2. Usage](#2-usage)
      - [2.1 server](#21-server)
      - [2.2 client CLI](#22-client-cli)
      - [2.3 client GUI](#23-client-gui)
  - [TODOs](#todos)
  - [Contributors](#contributors)
  - [License](#license)

## Getting Started

### 0. Prerequisities

To set up the environment, you need to have the following dependencies installed.

- [Python](https://www.python.org/downloads) 3.7 or later
- [Node.js](https://nodejs.org/en/download) 14 or later (for GUI)
- [Yarn](https://classic.yarnpkg.com/en/docs/install) (for GUI)

### 1. Installation

First, you need to obtain the Naive-FTP package.

```bash
git clone https://github.com/hakula139/Naive-FTP.git
cd Naive-FTP
```

Make sure you have the latest versions of `setuptools` and `wheel` installed.

```bash
python -m pip install --user --upgrade setuptools wheel
```

Then you can build the project using `setup.py`.

```bash
python setup.py install --user
```

#### 1.1 GUI support

If you prefer to use a GUI for client, use the following command to set up the GUI.

```bash
cd app && yarn && yarn build
```

### 2. Usage

#### 2.1 server

Start the Naive-FTP server using the command below, and the server will listen to port `2121` by default.

```bash
python ./naive_ftp/server/server.py
```

You should see the following welcome message:

```text
Welcome to Naive-FTP server! Press q to exit.
```

Press `q` to exit.

#### 2.2 client CLI

Start the Naive-FTP client CLI using the command below. The client will try to connect to `localhost:2121` by default.

```bash
python ./naive_ftp/client/client.py
```

To get started, use the command `help` to show all available commands.

```text
> help
```

#### 2.3 client GUI

Start the Naive-FTP client GUI using the command below.

```bash
yarn build
```

## TODOs

- [ ] Implement a GUI using Flask and Vue.js
  - [ ] Set up Vue.js
  - [ ] Set up Flask

## Contributors

- [**Hakula Chen**](https://github.com/hakula139)<[i@hakula.xyz](mailto:i@hakula.xyz)> - Fudan University

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](./LICENSE) file for details.
