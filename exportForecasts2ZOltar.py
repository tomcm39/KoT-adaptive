#mcandrew

from zoltpy import util
from zoltpy.connection import ZoltarConnection
import os

from glob import glob
import re

def connect2Zoltar:
    env_user='Z_USERNAME'
    env_pass='Z_PASSWORD'
    conn = ZoltarConnection()
    conn.authenticate(os.environ.get(env_user),os.environ.get(env_pass))
    return conn
    
def reformatDate(x):
    year,month,day = x.split('-')
    year  = int(year)
    month = int(month)
    day   = int(day)
    return "{:04d}-{:02d}-{:02d}".format(year,month,day)

def grabForecastWasSubmitted(fl):
    date = re.findall('\d{4}-\d{2}-\d+',fl)[0]
    date = reformatDate(date)
    return ''.join(date.split('-'))

def grabEW(fl):
    return re.findall('EW\d+',fl)[0]

def sortDateOfSubmissions():
    EW2SubmitDate = {}
    for fl in glob('./ensembleForecasts/*'):
        submitDate = grabForecastWasSubmitted(fl)
        EW = grabEW(fl)
        EW2SubmitDate[EW] = submitDate
    return EW2SubmitDate

def relateEW2SubmissionFiles():
    EW2submissionFile = {}
    for fl in glob('./submittedForecasts/*'):
        EW = grabEW(fl)
        EW2submissionFile[EW] = fl
    return EW2submissionFile

if __name__ == "__main__":

    conn = connect2Zoltar()
   
    project_name = 'CDC Real-time Forecasts'
    model_name   = 'KoT-adaptive'

    EW2submitDates    = sortDateOfSubmissions()
    EW2submissionFile = relateEW2SubmissionFiles()

    EW2submitDates = { 'EW42':'20191014'
                      ,'EW43':'20191021'
                      ,'EW44':'20191028'
                      ,'EW45':'20191104'
                      ,'EW46':'20191111'
                      ,'EW47':'20191118'}

    for EW in EW2submitDates:
        try:
            timezero_date      = EW2submitDates[EW]
            forecast_file_path = EW2submissionFile[EW]
            predx_json, forecast_filename = util.convert_cdc_csv_to_json_io_dict(forecast_file_path)
            conn = util.authenticate()
            util.upload_forecast(conn, predx_json, forecast_filename, project_name, model_name, timezero_date, overwrite=True)
            print('uploaded {:s}'.format(forecast_file_path))
        except Exception as e:
            print('error uploading {:s}'.format(forecast_file_path))
            print('{:s}'.format(str(e)))
