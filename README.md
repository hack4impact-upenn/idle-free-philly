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

3. Install the dependencies

    ```
    $ pip install -r requirements/common.txt
    $ pip install -r requirements/dev.txt
    ```

4. Create the database

    ```
    $ python manage.py recreate_db
    ```

5. Other setup (e.g. creating roles in database)

    ```
    $ python manage.py setup_dev
    ```

6. [Optional] Import a dump of real data

    ```
    $ python manage.py parse_csv -f poll244.csv
    ```

7. [Optional] Add fake data to the database

    ```
    $ python manage.py add_fake_data
    ```

## Running the app

```
$ source env/bin/activate
$ python manage.py runserver
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
```
