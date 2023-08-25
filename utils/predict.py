from sklearn.preprocessing import RobustScaler
from keras.models import load_model
from datetime import datetime, timedelta
from math import ceil, floor
import pandas as pd
import numpy as np
import os

from constants import DATETIME_FORMAT, SEQUENCE_LENGTH

scaler = RobustScaler()

# Load models
station_1_model = load_model(os.path.join("models", "station_1.h5"))
station_2_model = load_model(os.path.join("models", "station_2.h5"))
# Load the Testing data
data_station_1 = pd.read_csv(os.path.join("data", 'data_station_1.csv'))
data_station_2 = pd.read_csv(os.path.join("data", 'data_station_2.csv'))

def get_previous_loan_values(dataframe, start_date, n_hours):
  if not isinstance(dataframe['loan_datetime'], pd.DatetimeIndex):            # Convertir la columna loan_datetime a tipo datetime si no lo está
    dataframe['loan_datetime'] = pd.to_datetime(dataframe['loan_datetime'])
  
  start_index = dataframe[dataframe['loan_datetime'] == start_date].index[0]  # Encontrar el índice correspondiente a la fecha de inicio
  start_index = start_index - 1                                               # Empezar uno hacia atras
  
  # Obtener los valores de loans n horas hacia atrás desde el índice de inicio
  loan_values = []
  for i in range(n_hours):
    if start_index - i >= 0:
      loan_values.append([dataframe.loc[start_index - i, 'loans']])

  loan_values = loan_values[::-1]                                             # Invertir la lista de valores antes de devolverla
  return np.array(loan_values)


def predict_loan(station_id, str_datetime_inicio, str_datetime_fin):
  df_result = pd.DataFrame(columns=["loans", "loan_datetime"])
  scaler = RobustScaler()
  if(station_id == 1):
    loan_values = get_previous_loan_values(data_station_1, str_datetime_inicio, 10)
  else:
    loan_values = get_previous_loan_values(data_station_2, str_datetime_inicio, 10)

  datetime_inicio = datetime.strptime(str_datetime_inicio, '%Y-%m-%d %H:%M:%S')
  datetime_fin = datetime.strptime(str_datetime_fin, '%Y-%m-%d %H:%M:%S')

  n_horas = int((datetime_fin - datetime_inicio).total_seconds() / 3600)  # Convertir a entero

  if pd.DataFrame(loan_values).empty:
    print('No hay records...')
  else:
    loan_values_scaled = scaler.fit_transform(loan_values)
    loan_values_to_predict = np.array([loan_values_scaled])

    for i in range(n_horas):
      if(station_id == 1):
        prediction = scaler.inverse_transform(station_1_model.predict(loan_values_to_predict))[0][0]
      else:
        prediction = scaler.inverse_transform(station_2_model.predict(loan_values_to_predict))[0][0]

      if(prediction < 0.25):
        prediction = floor(prediction)
      else:
        prediction = ceil(prediction)

      # Allocating the result into the result DataFrame
      df_result.loc[len(df_result)] = {
          "loans": prediction,
          "loan_datetime": datetime_inicio + timedelta(hours=i),  # Usar timedelta para sumar horas
      }

      # Updating the new loan_values content to predict again with the new prediction
      print(loan_values_to_predict)
      print(loan_values)
      print(station_2_model.predict(loan_values_to_predict)[0][0])
      new_loan_values = loan_values[1:]
      new_loan_values = np.append(new_loan_values, prediction)
      loan_values = np.array(new_loan_values)

      loan_values = loan_values.reshape(10, 1)
      loan_values_scaled = scaler.fit_transform(loan_values)
      loan_values_to_predict = np.array([loan_values_scaled])
      print(loan_values_to_predict)
      print(loan_values)

  return df_result
