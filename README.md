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

## Install pip dependencies on local virtual environment (optional)
% ./update-venv.sh
```
Create a superuser in order to log into the django admin portal
```
% docker-compose run --rm app sh -c 'python manage.py createsuperuser'
```

### How to run tests
```
% docker-compose run --rm app sh -c 'python manage.py test'
```
### How to run linting
```
% docker-compose run --rm app sh -c 'flake8'
```

### Running the API locally
```
## Start the server ##
% docker-compose up

## Stop the server ##
% docker-compose down
```

### Running the API using deployment configuration
Use the steps below to deploy the app as it would be configured when deployed to the server
```
## Copy the sample .env file
## Modify the .env to your own custom values (Optional)
% cp ./.env.sample ./.env
```
```

## Build the required images
% docker-compose -f docker-compose-deploy.yml build

## Run DB, API, and NGINX
% docker-compose -f docker-compose-deploy.yml up
```

Once running, open the browser to:
`http://127.0.0.1/api/docs/`

### View API Docs (Swagger):
`http://127.0.0.1:8000/api/docs/`

You must be authenticated in order to use the recipe endpoints.
1. Create an authentication token using the `/api/user/token` endpoint
2. Copy the returned token string
3. Click the 'Authorize' button at the top of the page
4. Under 'TokenAuth' section, enter into the value field `token TOKEN_VALUE` where TOKEN_VALUE is the value you copied in step #2
5. You should now be able to access all the protected endpoints

### Manage resources through admin portal
`http://localhost:8000/admin`

(You will need to register a user to log in)