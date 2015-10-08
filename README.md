# Clean Air Council

## Running the app

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
    $ python manage.py shell
    ```

    ```python
    >>> db.create_all()
    >>> db.commit()
    ```

5. Run the server

    ```bash
    $ python manage.py runserver
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
    ```