# fastapi-sso-example
FastAPI Single Sign On example with various providers and minimal home page that presents counters for users from each provider 

## Installation

* Create a python virtual environment: `python3.11 -m venv venv`
* Activate the virtual environment: `source venv/bin/activate`
* Install dependencies: `python3.11 -m pip install -r requirements.txt`

## Setup and Configuration

* Create a `.env` file in the project root directory.
* Add the following environment variable key-value pairs to the `.env` file:<br>
    * `SECRET_KEY=your_secret_key_value`<br>
    * `SESSION_COOKIE_NAME=your_cookie_name_value`

## Use the project
* While in activated virtual environment, run with: `python3.11 main.py`

## To sign up a local user
Use the swagger documentation at `localhost:9999/v1/documentation`, example:
* ![img.png](img.png)

## Browse in the app
* Visit the user interface in the browser at: `localhost:9999`
* Use form to sign-in with local users
* Use sign-in buttons to sign-in via a provider