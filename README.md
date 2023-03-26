# Movies - Backend

## Setting Up Local Environment

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/manthan2205man/backend_movies_apis.git
$ cd backend_movies_apis
```

Create a virtual environment to install dependencies in and activate it:
```sh
python -m venv venv
```
For windows to activate ENV:
```sh
venv\scripts\activate
```
For Mac/Ubuntu to activate ENV:
```sh
source venv/bin/activate
```
Then install the dependencies:
```sh
(venv)$ pip install -r requirements.txt
```

Once `pip` has finished downloading the dependencies:
```sh
(venv)$ python manage.py migrate
(venv)$ python manage.py runserver
```

Here is a postman collection to check APIs
```sh
https://api.postman.com/collections/12941465-b1354b29-c23d-49e3-b12a-8c13ded1b4f2?access_key=PMAT-01GWEHQ7VDXG4C2Y9DVBP0122Q
```
