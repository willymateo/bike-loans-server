from os import path
import pathlib

ADMISSIONS_DATASET_PATH = path.join(
    pathlib.Path().absolute(),
    "data",
    "Reporte Solicitudes ADMPROF20230621_143623.xls",
)

ESPOL_DATASET_PATH = path.join(
    pathlib.Path().absolute(), "data", "Reporte Solicitudes ESTUD20230621_143623.xls"
)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

BICIESPOL_WORK_START_TIME = "07:00:00"

BICIESPOL_WORK_END_TIME = "17:00:00"

START_CUT_DATE = "2022-05-17"

ALLOWED_STATIONS = [1, 2]

SEQUENCE_LENGTH = 10
