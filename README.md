[![Build Status](https://travis-ci.org/jomomg/hellobooks_api.svg?branch=develop)](https://travis-ci.org/jomomg/hellobooks_api)
[![Coverage Status](https://coveralls.io/repos/github/jomomg/hellobooks_api/badge.svg?branch=develop)](https://coveralls.io/github/jomomg/hellobooks_api?branch=develop)

# Hellobooks API

Hellobooks API is a library management API. It keeps track of books in a library and users who interact with the library. 
It also facilitates the borrowing of books. Users also have the ability to create user accounts which accords them certain 
privileges. The complete functionality and with the respective endpoints is listed below.

## API Functionality

|Endpoint                  | Functionality              |HTTP method 
|--------------------------|----------------------------|-------------
|/api/books                |Add a book                  |POST        
|/api/books/<bookId>       |modify a book’s information |POST
|/api//books/<bookId>      |Remove a book               |DELETE
|/api/books                |Retrieves all books         |GET
|/api/books/<bookId>       |Get a book                  |GET
|/api/users/books/<bookId> |Borrow a book               |POST
|/api/auth/register        |Creates a user account      |POST
|/api/auth/login           |Logs in a user              |POST
|/api/auth/logout          |Logs out a user             |POST
|/api/auth/reset-password  |Password reset              |POST

## How to run this application

 - Clone this repository
 - Set up a virtual environment
 - Install the apps dependencies by running `pip install -r requirements.txt`
 - Open a terminal and `cd` into the app's main directory
 - Run `python run.py`
 
 ## How to run the tests
 
 - Nosetests is recommended. Run `nosetests` in the apps main directory
