## MGD77T Data Record (Tab-Delimited)
The newer tab-delimited MGD77T data format contains variable-length records separated by tabs.

*   **SURVEY_ID** (`string`): Survey identifier assigned by the contributing organization or NGDC.
*   **TIMEZONE** (`float`): Time-zone correction in hours (-13 to +12).
*   **DATE** (`string` or `datetime64`): Date of the record (YYYYMMDD).
*   **TIME** (`string` or `datetime64`): Time of the record (HHMMSS.sss).
*   **LAT** (`float64`): Latitude in decimal degrees (negative for South).
*   **LON** (`float64`): Longitude in decimal degrees (negative for West, -180 to 180).
*   **POS_TYPE** (`Int64`): Position type code (1 = Observed fix, 3 = Interpolated).
*   **TWT** (`float64`): Two-way travel time for bathymetry in seconds.
*   **DEPTH** (`float64`): Corrected bathymetric depth in meters.
*   **BATH_TYP** (`Int64`): Bathymetry type code.
*   **MTF1** (`float64`): Magnetic total field 1 in nanoteslas (nT).
*   **MTF2** (`float64`): Magnetic total field 2 in nanoteslas (nT).
*   **MAG** (`float64`): Residual magnetic anomaly in nanoteslas (nT).
*   **DIUR** (`float64`): Magnetic diurnal correction in nanoteslas (nT).
*   **MSENS** (`float64`): Magnetic sensor depth (positive) or altitude (negative) in meters.
*   **GOBS** (`float64`): Observed gravity in milligals (mGal).
*   **EOT** (`float64`): Eötvös correction in milligals (mGal).
*   **FAA** (`float64`): Free-air gravity anomaly in milligals (mGal).
*   **SEIS_LINE** (`string`): Seismic line identifier.
*   **SEIS_SHOT** (`string` or `Int64`): Seismic shot-point number.

## Legacy MGD77 Data Record (Fixed-Width)
The legacy MGD77 data file uses a fixed 120-character record format.

*   **RECORD_TYPE** (`string`): Always "5" for data records [Col 1].
*   **SURVEY_ID** (`string`): Survey identifier [Cols 2-9].
*   **TIMEZONE** (`Int64` / `float64`): Correction to GMT in hours [Cols 10-12].
*   **DATE_YEAR** (`Int64`): 4-digit year [Cols 13-16].
*   **DATE_MONTH** (`Int64`): 2-digit month [Cols 17-18].
*   **DATE_DAY** (`Int64`): 2-digit day [Cols 19-20].
*   **TIME_HOUR** (`Int64`): 2-digit hour [Cols 21-22].
*   **TIME_MIN** (`float64`): Minutes [Cols 23-27].
*   **LAT** (`float64`): Latitude (implied decimal) [Cols 28-35].
*   **LON** (`float64`): Longitude (implied decimal) [Cols 36-44].
*   **POS_TYPE** (`Int64`): Fix type (1=Observed, 3=Interpolated) [Col 45].
*   **TWT** (`float64`): Two-way travel time [Cols 46-51].
*   **DEPTH** (`float64`): Corrected depth [Cols 52-57].
*   **BATH_TYP** (`Int64`): Bathymetry type [Col 58].
*   **MTF1** (`float64`): Magnetic total field 1 [Cols 59-64].
*   **MTF2** (`float64`): Magnetic total field 2 [Cols 65-70].
*   **MAG** (`float64`): Residual magnetic anomaly [Cols 71-76].
*   **MAG_SENS** (`Int64`): Sensor type [Col 77].
*   **DIUR** (`float64`): Diurnal correction [Cols 78-83].
*   **MSENS** (`float64`): Mag sensor depth/altitude [Cols 84-89].
*   **GOBS** (`float64`): Observed gravity [Cols 90-96].
*   **EOT** (`float64`): Eötvös correction [Cols 97-101].
*   **FAA** (`float64`): Free air anomaly [Cols 102-106].
*   **SEIS_LINE** (`string`): Seismic line ID [Cols 107-111].
*   **SEIS_SHOT** (`string`): Seismic shot point [Cols 112-117].
*   **QUALITY_CODE** (`string`): Quality indicator [Cols 118-120].

## MGD77T Header Record (Tab-Delimited)
The header contains exactly one tab-delimited record documenting the survey metadata. 

*   **SURVEY_ID** (`string`): Survey identifier.
*   **FORMAT_77** (`string`): Format acronym (set to "MGD77T").
*   **CENTER_ID** (`string`): Data center file number.
*   **PARAMS_CO** (`string`): Parameters surveyed code (e.g., bathymetry, gravity, magnetics).
*   **DATE_CREAT** (`Int64`): File creation date (YYYYMMDD).
*   **INST_SRC** (`string`): Source institution.
*   **COUNTRY** (`string`): Country of origin.
*   **PLATFORM** (`string`): Platform (vessel) name.
*   **PLAT_TYPCO** (`Int64`): Platform type code (1=Ship, 3=Aircraft, etc.).
*   **PLAT_TYP** (`string`): Platform type description.
*   **CHIEF** (`string`): Chief scientist(s).
*   **PROJECT** (`string`): Project, cruise, or leg name.
*   **FUNDING** (`string`): Funding agency or institution.
*   **DATE_DEP** (`Int64`): Departure date (YYYYMMDD).
*   **PORT_DEP** (`string`): Port of departure.
*   **DATE_ARR** (`Int64`): Arrival date (YYYYMMDD).
*   **PORT_ARR** (`string`): Port of arrival.
*   **NAV_INSTR** (`string`): Navigation instrumentation.
*   **POS_INFO** (`string`): Position determination method/datum.
*   **BATH_INSTR** (`string`): Bathymetry instrumentation.
*   **BATH_ADD** (`string`): Additional forms of bathymetry data.
*   **MAG_INSTR** (`string`): Magnetics instrumentation.
*   **MAG_ADD** (`string`): Additional forms of magnetics data.
*   **GRAV_INSTR** (`string`): Gravity instrumentation.
*   **GRAV_ADD** (`string`): Additional forms of gravity data.
*   **SEIS_INSTR** (`string`): Seismic instrumentation.
*   **SEIS_FRMTS** (`string`): Formats of seismic data.
*   **LAT_TOP** (`float64`): Northbound latitude of survey.
*   **LAT_BOTTOM** (`float64`): Southbound latitude.
*   **LON_LEFT** (`float64`): Westbound longitude.
*   **LON_RIGHT** (`float64`): Eastbound longitude.
*   **BATH_DRATE** (`float64`): General digitizing rate for bathymetry (mins).
*   **SOUND_VEL** (`float64`): Assumed sound velocity (e.g., 1500 m/s).
*   **VDATUM_CO** (`Int64`): Bathymetric vertical datum code.
*   **M_REFFL_CO** (`Int64`): Magnetic reference field code (e.g., IGRF versions).

## Legacy MGD77 Header Record (Fixed-Width)
The legacy header consists of 24 blocks of 80-character strings. 
It contains the exact same metadata described in the MGD77T header but is structured differently. 
No difference in terms of the actual fields between the two.