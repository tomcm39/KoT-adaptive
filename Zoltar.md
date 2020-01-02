# Zoltar

## Uploading PAST Forecasts to Zoltar using Python 3

The python package [zoltpy](https://pypi.org/project/zoltpy/) is used to upload forecasts to the Zoltar database.
Uploading a forecast follows 4 steps:

* [Step 1: Connect to the Zoltar Server](#Step-1-Connect-to-the-Zoltar-Server)
* [Step 2: Create list of model and project identifying information](#Step-2-Create-list-of-model-and-project-identifying-information)
* [Step 3: Create dictionary of Epidemic weeks with forecasts and "timezero" dates](#Step-3-Create-dictionary-of-Epidemic-weeks-with-forecasts-and-"timezero"-dates)
* [Step 4: Submit forecast files](#Step-4-Submit-forecast-files)

### Step 1: Connect to the Zoltar Server

To use Zoltar you need to obtain a username and password by contacting Professor Nicholas Reich (nick@schoolph.umass.edu), director of the Reich Lab.
Details on how to install zoltpy and securely store your username/password on your local machine can be found [here](https://github.com/reichlab/zoltpy) under the header **One-time Environment Variable Configuration**.

Your python code will need to import two functions from Zoltpy:
```
from zoltpy import util
from zoltpy.connection import ZoltarConnection
```

You can then connect to the Zoltar server by using the following helper function. 
```
def connect2Zoltar():
	import os
    env_user='Z_USERNAME'
    env_pass='Z_PASSWORD'
    conn = ZoltarConnection()
    conn.authenticate(os.environ.get(env_user),os.environ.get(env_pass))
    return conn
	
conn = connect2Zoltar()
```

### Step 2: Create list of model and project identifying information

Two variables are needed to submit a forecast: The name of the project (from the Zoltar Website) and name of your model. It is important that these names match the names that are displayed on the Zoltar Website, else the upload will result in error. An example can be found below for the "KoT-adaptive" model within the "CDC Real-time Forecasts" project.
```
project_name = 'CDC Real-time Forecasts'
model_name   = 'KoT-adaptive'
```

### Step 3: Create dictionary of Epidemic weeks with forecasts and "timezero" dates

To submit past forecasts, a dictionary can be created of Epidemic Weeks (key) and time_zeroes (value).
Every epidemic week has a Time\_Zero.
We define the Monday (YYYY-MM-DD) corresponding to an epidemic week as **Time\_Zero**.

An example dictionary is shown below
```
EW2timeZeroes =   {'EW42':'20191014'
                  ,'EW43':'20191021'
                  ,'EW44':'20191028'
                  ,'EW45':'20191104'
                  ,'EW46':'20191111'
                  ,'EW47':'20191118'}
```

We also recommend creating a dictionary of Epidemic Week (key) and CSV file (value) that contains the file location for your model's forecast.
```
EW2submissionFile =   {'EW42':'FilePATH'
                      ,'EW43':'FilePATH'
                      ,'EW44':'FilePATH'
                      ,'EW45':'FilePATH'
                      ,'EW46':'FilePATH'
                      ,'EW47':'FilePATH'}
```

### Step 4: Submit forecast files

There are two methods in zoltpy that are always needed for uploading forecasts. The first is the helper function `util.convert_cdc_csv_to_json_io_dict` which will convert your csv file into a JSON that is compatible with Zoltar. This helper function takes the path to your csv file and return the JSON `predx_json` and the csv file name `forecast_filename`.

The second method is the main upload function which is `util.upload_forecast`.
The upload_forecast function takes these as input: an authenticated connection to Zoltar, a JSON format of your forecast, the name of the project, the name of your model, the timezero.
An example of submitting forecasts to the CDC's FluSight Project is below.

```
project_name = 'CDC Real-time Forecasts'
model_name   = 'KoT-adaptive'

for EW in EW2submitDates:
    try:
		timezero_date      = EW2timeZeroes[EW]
		forecast_file_path = EW2submissionFile[EW]
		predx_json, forecast_filename = util.convert_cdc_csv_to_json_io_dict(forecast_file_path)
		conn = util.authenticate()
		util.upload_forecast(conn, predx_json, forecast_filename, project_name, model_name, timezero_date, overwrite=True)
		print('uploaded {:s}'.format(forecast_file_path))
	except Exception as e:
		print('error uploading {:s}'.format(forecast_file_path))
		print('{:s}'.format(str(e)))
```
