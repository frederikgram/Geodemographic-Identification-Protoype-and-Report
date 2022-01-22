# Innovation Project

📌: It is highly recommended to read the `innovation.pdf` file, as this contains a detailed description of both the problem and the prototype itself.

## About
web-service based data analysis platform, showing and highligting Danish municipalities by comparing them using any permutation of the available metrics.

## Prerequisites
To run this service, it is necessary to have Python 3.8 or higher, and the pip package manager for Python 3 installed on your machine.
## Installation

### Clone the repo

```
$ git clone https://github.com/frederikgram/innovation.git
$ cd innovation
```

### Create a virtual environment


```
$ python3 -m venv env
```

---
### Activate the environment
##### For Linux Machines

```
$ source ./env/bin/activate
```

##### For Windows Machines

```
$ env\Scripts\activate.bat
```

#### Install dependencies
---

```
$ pip3 install -r requirements.txt
```

## Usage
To initialize the web-service, change directory into `webservice`
```
$ cd webservice
```


#### Setup the FLASK environment

##### For Linux Machines

```
$ set FLASK_APP=app.py
```

##### For Windows Machines

```
$ export FLASK_APP=app.py
```
From here the webservice can be started using:
```
$ flask run
```
and is now accessible at `localhost:5000`
