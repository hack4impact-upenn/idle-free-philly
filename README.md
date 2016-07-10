# IdleFreePhilly [![Circle CI](https://circleci.com/gh/hack4impact/idle-free-philly.svg?style=svg)](https://circleci.com/gh/hack4impact/idle-free-philly)

IdleFreePhilly allows anyone to report illegal vehicle idling.

## Setting up

#####  Clone the repo

```
$ git clone https://github.com/hack4impact/idle-free-philly.git
$ cd idle-free-philly
```

##### Initialize a virtualenv

```
$ pip install virtualenv
$ virtualenv env
$ source env/bin/activate
```

##### Install the app dependencies

```
$ pip install -r requirements/common.txt
$ pip install -r requirements/dev.txt
```

##### Other dependencies for running locally

You need to install [Foreman](https://ddollar.github.io/foreman/) and [Redis](http://redis.io/). Chances are, these commands will work:

```
$ gem install foreman
```

Mac (using [homebrew](http://brew.sh/)):

```
$ brew install redis
```

Linux:

```
$ sudo apt-get install redis-server
```


##### Create the database

```
$ python manage.py recreate_db
```

##### Other setup (initialize database)

```
$ python manage.py setup_dev
```

##### [Optional] Add fake data to the database

```
$ python manage.py add_fake_data
```

##### [Optional] Import some actual data

```
$ python manage.py parse_csv -f poll244.csv
```

## Running the app

```
$ source env/bin/activate
$ foreman start -f Local
```

## License
[MIT License](LICENSE.md)
