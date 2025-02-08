Kyle's Datasette

## Local Developer Install
```cmd
python -m pip install -e .'[dev]'
```
To run the test kit
```cmd
python -m pytest tests.py
```

## Usage
To build the SQLite database after installing the project use the CLI command
```cmd
load-data
```

To run the app locally
```cmd
python -m datasette -m metadata.yml -o data.db
```