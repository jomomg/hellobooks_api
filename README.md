[![Build Status](https://travis-ci.org/jomomg/hellobooks_api.svg?branch=develop)](https://travis-ci.org/jomomg/hellobooks_api)
[![Coverage Status](https://coveralls.io/repos/github/jomomg/hellobooks_api/badge.svg?branch=master)](https://coveralls.io/github/jomomg/hellobooks_api?branch=master)

# Hellobooks API

Hellobooks API is a library management API. It keeps track of books in a library and users who interact with the library. 
It also facilitates the borrowing of books. Users also have the ability to create user accounts which accords them 
privileges. The complete functionality and with the respective endpoints is listed below.

## API Functionality

|Endpoint                  | Functionality              |HTTP method 
|--------------------------|----------------------------|-------------
|/api/books                |Add a book                  |POST        
|/api/books/*book_id*       |modify a book’s information |PUT
|/api/books/*book_id*      |Remove a book               |DELETE
|/api/books                |Retrieves all books         |GET
|/api/books/*book_id*       |Get a book                  |GET
|/api/users/books/*book_id* |Borrow a book               |POST
|/api/auth/register        |Creates a user account      |POST
|/api/auth/login           |Logs in a user              |POST
|/api/auth/logout          |Logs out a user             |POST
|/api/auth/reset-password  |Password reset              |POST

## How to run this application

 - Pre-requisites: Python 3.6
 - Clone this repository `git clone https://github.com/jomomg/hellobooks_api.git`
 - Set up a virtual environment. `virtualenv` is recommended
 - Install the apps dependencies by running `pip install -r requirements.txt`
 - Open a terminal and `cd` into the cloned repository
 - Run `python run.py`
 
## Usage

 - Postman can be used to send requests to the app.
 - The app takes requests in JSON and responds in JSON.
 - Authentication is needed to interact with the endpoints.
 - To authenticate, send a JSON request in the form `{"email":"email@example.com", "password":"my_password"}`
   to the `/api/auth/register` endpoint. To login send the same data to the `/api/auth/login` endpoint.
   You will then be issued with an access token that lasts 15 minutes.
 - For a password reset, make sure you are first logged in and then send the new password to the reset endpoint.
 - The app accepts the following book attributes: 
   `book_id, book_title, publisher, publication_year, edition, category, subcategory, description`
 - An example JSON request is: 
 ```json
   {
   "book_id": 101, 
   "book_title": "Ready Player One", 
   "publisher": "Random House",
   "publication_year": "2011",
   "edition": "1",
   "category": "fiction", 
   "subcategory": "science fiction",
   "description": "A book about virtual reality"
   }
   ```
 
## How to run the tests
 
 - Nose is recommended. Run `nosetests` in the apps main directory
 
## More info
 - API documentation: [https://hellobooksapi.docs.apiary.io](https://hellobooksapi.docs.apiary.io)
 - API on heroku: [hellobooksapi.herokuapp.com](hellobooksapi.herokuapp.com)
