# Clean Air Council [![Circle CI](https://circleci.com/gh/hack4impact/clean-air-council.svg?style=svg)](https://circleci.com/gh/hack4impact/clean-air-council)

## Setting up

1. Clone the repo

    ```
    $ git clone https://github.com/hack4impact/clean-air-council.git
    $ cd clean-air-council
    ```

2. Initialize a virtualenv

    ```
    $ pip install virtualenv
    $ virtualenv env
    $ source env/bin/activate
    ```

3. Install the app dependencies

    ```
    $ pip install -r requirements/common.txt
    $ pip install -r requirements/dev.txt
    ```

4. Other dependencies for running locally

    ```
    $ gem install foreman
    $ brew install redis
    ```

5. Create a .env file in the project root for environment variables
    
    To start off, add:
    ```
    FLASK_CONFIG=development
    ```

6. Create the database

    ```
    $ python manage.py recreate_db
    ```

7. Other setup (e.g. creating roles in database)

    ```
    $ python manage.py setup_dev
    ```

8. [Optional] Add fake data to the database

    ```
    $ python manage.py add_fake_data
    ```

## Running the app locally

```
$ source env/bin/activate
$ redis-server &
$ foreman start
```

## License
[MIT License](LICENSE.md)
