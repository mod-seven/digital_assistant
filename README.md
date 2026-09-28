# Digital assistant

## Run the app

Run app:

```
flet run main.py
```

Create app for windowed

```
pyinstaller --onedir --windowed --name digital_assistant --add-data "assets;assets" --add-data "venv\Lib\site-packages\shevchenko;shevchenko" --add-data "venv\Lib\site-packages\shevchenko_ext_military;shevchenko_ext_military" main.py
```
