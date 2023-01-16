# recipe-app-api
Recipe API Project built using Django and Django Rest Framework (DRF)



### How to build the project
```sh
## Create the container image with required dependencies
% docker-compose build
```

### Local setup steps
The following steps are nice to haves for a local setup using vscode and will allow for autocompletes in the editor.
```sh
## Create a virtual environment (venv)
% python3.9 -m venv ./venv && /venv/bin/pip install --upgrade pip

## Install pip dependencies on local virtual environment
## (for )
% ./update-venv.sh
```

### How to run tests
```
% docker-compose run --rm app sh -c 'python manage.py test'
```

### Running the API
```
## Start the server ##
% docker-compose up

## Stop the server ##
% docker-compose down
```

### View API Docs (Swagger):
`http://localhost:8000/api/docs/`

You must be authenticated in order to use the recipe endpoints.
1. Create an authentication token using the `/api/user/token` endpoint
2. Copy the returned token string
3. Click the 'Authorize' button at the top of the page
4. Under 'TokenAuth' field enter `token {TOKEN_VALUE}` where TOKEN_VALUE is the value you copied in step #2
5. You should now be able to access all the protected endpoints

### Manage resources through admin portal
`http://localhost:8000/admin`

(You will need to register a user)