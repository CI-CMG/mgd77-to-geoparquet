import argparse
import datetime
import io
import json
import os
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq
from shapely.geometry import Point

# The 26 MGD77T Field IDs from the format specification
MGD77T_COLUMNS = [
  "SURVEY_ID", "TIMEZONE", "DATE", "TIME", "LAT", "LON", "POS_TYPE",
  "NAV_QUALCO", "BAT_TTIME", "CORR_DEPTH", "BAT_CPCO", "BAT_TYPCO",
  "BAT_QUALCO", "MAG_TOT", "MAG_TOT2", "MAG_RES", "MAG_RESSEN",
  "MAG_DICORR", "MAG_SDEPTH", "MAG_QUALCO", "GRA_OBS", "EOTVOS",
  "FREEAIR", "GRA_QUALCO", "LINEID", "POINTID"
]

def parse_mgd77_datetime(time_str: str) -> datetime.datetime | None:
  """Converts a 15-character MGD77 time string into a UTC datetime object."""
  if not time_str or len(time_str) != 15 or time_str.startswith("9999"):
    return None

  try:
    year = int(time_str[0:4])
    month = int(time_str[4:6])
    day = int(time_str[6:8])
    hour = int(time_str[8:10])
    minute_raw = int(time_str[10:15])

    # Guard against MGD77 missing value flags (often 99)
    if month > 12 or month == 0 or day > 31 or day == 0 or hour > 24:
      return None

    minute_float = minute_raw / 1000.0

    base_dt = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
    final_dt = base_dt + datetime.timedelta(minutes=minute_float)

    return final_dt

  except ValueError:
    return None

def standardize_dtypes(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
  """Forces strict data types on the GeoDataFrame to ensure Parquet schema consistency."""
  type_mapping = {
    "SURVEY_ID": "string",
    "TIMEZONE": "Int64",
    "datetime_utc": "datetime64[ns, UTC]",
    "LAT": "float64",
    "LON": "float64",
    "POS_TYPE": "string",
    "NAV_QUALCO": "string",
    "BAT_TTIME": "float64",
    "CORR_DEPTH": "float64",
    "BAT_CPCO": "string",
    "BAT_TYPCO": "string",
    "BAT_QUALCO": "string",
    "MAG_TOT": "float64",
    "MAG_TOT2": "float64",
    "MAG_RES": "float64",
    "MAG_RESSEN": "string",
    "MAG_DICORR": "float64",
    "MAG_SDEPTH": "float64",
    "MAG_QUALCO": "string",
    "GRA_OBS": "float64",
    "EOTVOS": "float64",
    "FREEAIR": "float64",
    "GRA_QUALCO": "string",
    "LINEID": "string",
    "POINTID": "string"
  }

  for col, dtype in type_mapping.items():
    if col in gdf.columns:
      if dtype == "string":
        gdf[col] = gdf[col].astype("string")
      elif dtype == "Int64":
        gdf[col] = pd.to_numeric(gdf[col], errors='coerce').astype("Int64")
      elif dtype == "float64":
        gdf[col] = pd.to_numeric(gdf[col], errors='coerce').astype("float64")
      elif dtype.startswith("datetime"):
        gdf[col] = pd.to_datetime(gdf[col], utc=True, errors='coerce')

  return gdf

def parse_h77t_header_fixed(h77t_path: str) -> dict:
  """Parses an older, fixed-width/colon-separated .h77t header file."""
  header_data = {"filename": os.path.basename(h77t_path), "fields": {}}
  with open(h77t_path, "r", encoding="ascii", errors="ignore") as f:
    raw_text = f.read()
    header_data["raw_header"] = raw_text
    for line in raw_text.splitlines():
      if ":" in line:
        key, val = line.split(":", 1)
        header_data["fields"][key.strip()] = val.strip()
  return header_data

def parse_h77t_header_tabular(h77t_path: str) -> dict:
  """Parses a newer, tab-separated .h77t (MGD77T) header file."""
  header_data = {"filename": os.path.basename(h77t_path), "fields": {}}
  try:
    df_header = pd.read_csv(h77t_path, sep='\t', nrows=1)
    if not df_header.empty:
      header_data["fields"] = df_header.iloc[0].dropna().to_dict()

    with open(h77t_path, "r", encoding="utf-8", errors="ignore") as f:
      header_data["raw_header"] = f.read()
  except Exception as e:
    print(f"Warning: Could not parse tabular header {h77t_path}: {e}")
  return header_data

def parse_header(h77t_path: str) -> dict:
  """Detects header format (MGD77 vs MGD77T) and parses accordingly."""
  if not os.path.exists(h77t_path):
    return {}

  with open(h77t_path, "r", encoding="utf-8", errors="ignore") as f:
    first_line = f.readline()

  if '\t' in first_line:
    return parse_h77t_header_tabular(h77t_path)
  else:
    return parse_h77t_header_fixed(h77t_path)

def parse_mgd77_record(line: str) -> dict | None:
  """Parses a complete 120-character legacy MGD77 data record."""
  if len(line) < 120 or line[0] != "5":
    return None

  try:
    def _parse_float(val_str, multiplier, null_val):
      val = val_str.strip()
      return float(val) * multiplier if val and val != null_val else None

    def _parse_str(val_str, null_val):
      val = val_str.strip()
      return val if val and val != null_val else None

    # Survey ID & Time (Chars 2-27)
    survey_id = line[1:9].strip()
    tz_raw = line[9:12].strip()
    timezone = int(tz_raw) if tz_raw and tz_raw != "999" else None
    time_str = line[12:27].strip()

    # Spatial (Chars 28-44)
    lat_raw = int(line[27:35].strip())
    lon_raw = int(line[35:44].strip())
    if lat_raw == 9999999 or lon_raw == 99999999:
      return None
    latitude = lat_raw / 100000.0
    longitude = lon_raw / 100000.0

    # Position and depth data (Chars 45-60)
    pos_type = _parse_str(line[44:45], "9")
    bat_ttime = _parse_float(line[45:51], 0.0001, "999999")
    corr_depth = _parse_float(line[51:57], 0.1, "999999")
    bat_cpco = _parse_str(line[57:59], "99")
    bat_typco = _parse_str(line[59:60], "9")

    # Magnetics (Chars 61-90)
    mag_tot = _parse_float(line[60:66], 0.1, "999999")
    mag_tot2 = _parse_float(line[66:72], 0.1, "999999")
    mag_res = _parse_float(line[72:78], 0.1, "999999")
    mag_ressen = _parse_str(line[78:79], "9")
    mag_dicorr = _parse_float(line[79:84], 0.1, "99999")
    mag_sdepth = _parse_float(line[84:90], 1.0, "999999")

    # Gravity & Eotvos (Chars 91-108)
    gra_obs = _parse_float(line[90:97], 0.1, "9999999")
    eotvos = _parse_float(line[97:103], 0.1, "999999")
    freeair = _parse_float(line[103:108], 0.1, "99999")

    # Seismic IDs & Nav Quality (Chars 109-120)
    lineid = _parse_str(line[108:113], "99999")
    pointid = _parse_str(line[113:119], "999999")
    nav_qualco = _parse_str(line[119:120], "9")

    return {
      "SURVEY_ID": survey_id,
      "TIMEZONE": timezone,
      "datetime_utc": parse_mgd77_datetime(time_str),
      "LAT": latitude,
      "LON": longitude,
      "POS_TYPE": pos_type,
      "BAT_TTIME": bat_ttime,
      "CORR_DEPTH": corr_depth,
      "BAT_CPCO": bat_cpco,
      "BAT_TYPCO": bat_typco,
      "MAG_TOT": mag_tot,
      "MAG_TOT2": mag_tot2,
      "MAG_RES": mag_res,
      "MAG_RESSEN": mag_ressen,
      "MAG_DICORR": mag_dicorr,
      "MAG_SDEPTH": mag_sdepth,
      "GRA_OBS": gra_obs,
      "EOTVOS": eotvos,
      "FREEAIR": freeair,
      "LINEID": lineid,
      "POINTID": pointid,
      "NAV_QUALCO": nav_qualco,
      "geometry": Point(longitude, latitude),
    }
  except ValueError:
    return None

def parse_mgd77_fixed_data(data_path: str) -> gpd.GeoDataFrame | None:
  """Parses older fixed-width MGD77 files line by line."""
  records = []
  with open(data_path, "r", encoding="ascii", errors="ignore") as f:
    for line in f:
      parsed = parse_mgd77_record(line)
      if parsed:
        records.append(parsed)

  if not records:
    return None
  return gpd.GeoDataFrame(records, crs="EPSG:4326")

def parse_mgd77t_tabular_data(data_path: str) -> gpd.GeoDataFrame | None:
  """Parses newer MGD77T tab-separated files, handling missing headers."""
  try:
    df = pd.read_csv(data_path, sep='\t', low_memory=False)

    if 'LAT' not in df.columns or 'LON' not in df.columns:
      print(f"Header row missing in {data_path}. Applying standard MGD77T schema.")
      num_cols = len(df.columns)
      df = pd.read_csv(data_path, sep='\t', header=None, names=MGD77T_COLUMNS[:num_cols], low_memory=False)

  except Exception as e:
    print(f"Error reading TSV {data_path}: {e}")
    return None

  # Drop records missing spatial coordinates
  # TODO - revisit whether to do this?
  df = df.dropna(subset=['LAT', 'LON'])
  if df.empty:
    return None

  if 'DATE' in df.columns and 'TIME' in df.columns:
    time_mask = df['DATE'].notna() & df['TIME'].notna()

    hours = (df.loc[time_mask, 'TIME'] // 100).astype(int)
    minutes = df.loc[time_mask, 'TIME'] % 100

    base_dates = pd.to_datetime(
      df.loc[time_mask, 'DATE'].astype(int).astype(str),
      format='%Y%m%d',
      errors='coerce'
    )
    df.loc[time_mask, 'datetime_utc'] = base_dates + pd.to_timedelta(hours, unit='h') + pd.to_timedelta(minutes, unit='m')

  # Convert to GeoDataFrame
  gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['LON'], df['LAT']),
    crs="EPSG:4326"
  )

  return gdf

def parse_data(data_path: str) -> gpd.GeoDataFrame | None:
  """Detects data format (MGD77 vs MGD77T) and parses accordingly."""
  with open(data_path, "r", encoding="utf-8", errors="ignore") as f:
    first_line = f.readline()

  if '\t' in first_line:
    print(f"Detected MGD77T (Tabular) format for {os.path.basename(data_path)}")
    return parse_mgd77t_tabular_data(data_path)
  else:
    print(f"Detected MGD77 (Fixed-Width) format for {os.path.basename(data_path)}")
    return parse_mgd77_fixed_data(data_path)

def process_file_pair(data_path: str, header_path: str, output_parquet_path: str):
  """Converts a paired survey file and header into GeoParquet."""
  print(f"Reading data from {data_path}...")
  gdf = parse_data(data_path)

  if gdf is None or gdf.empty:
    print(f"No valid spatial records found in {data_path}.")
    return

  # Standardize data types before writing to Parquet
  gdf = standardize_dtypes(gdf)

  h77t_metadata = parse_header(header_path)

  buffer = io.BytesIO()
  gdf.to_parquet(buffer, compression="zstd")
  buffer.seek(0)

  table = pq.read_table(buffer)

  existing_metadata = dict(table.schema.metadata or {})
  existing_metadata[b"h77t_metadata"] = json.dumps(h77t_metadata).encode("utf-8")
  table = table.replace_schema_metadata(existing_metadata)

  pq.write_table(table, output_parquet_path, compression="zstd")

def read_parquet_footer_metadata(parquet_path: str) -> dict:
  """Extracts custom .h77t footer metadata from a Parquet file."""
  schema = pq.read_schema(parquet_path)
  metadata_bytes = schema.metadata.get(b"h77t_metadata")
  if metadata_bytes:
    return json.loads(metadata_bytes.decode("utf-8"))
  return {}

def process_directory(input_dir: Path, output_dir: Path) -> None:
  """Finds paired MGD77/MGD77T and .h77t files in a directory and converts them."""
  if not input_dir.is_dir():
    print(f"Error: Directory '{input_dir}' does not exist.", file=sys.stderr)
    sys.exit(1)

  data_files = list(input_dir.glob("*.m77t")) + list(input_dir.glob("*.mgd77"))

  if not data_files:
    print(f"No .m77t or .mgd77 data files found in '{input_dir}'.")
    return

  if output_dir:
    output_dir.mkdir(parents=True, exist_ok=True)

  out_dir = output_dir if output_dir else input_dir

  for data_file in data_files:
    base_name = data_file.stem
    h77t_file = input_dir / f"{base_name}.h77t"
    if not h77t_file.exists():
      h77t_file = input_dir / f"{base_name}.h77"
      if not h77t_file.exists():
        print(f"Skipping {data_file.name}: Matching header file not found.")
        continue

    parquet_file = out_dir / f"{base_name}.parquet"

    process_file_pair(str(data_file), str(h77t_file), str(parquet_file))

    if parquet_file.exists():
      footer_meta = read_parquet_footer_metadata(str(parquet_file))
      print(json.dumps(footer_meta, indent=2)[:500] + "\n...")

def main():
  parser = argparse.ArgumentParser(
    description="Version-agnostic batch converter for MGD77 and MGD77T files to GeoParquet."
  )
  parser.add_argument("folder", type=Path, help="Directory containing survey data and header files.")
  parser.add_argument("-o", "--output", type=Path, default=None, help="Destination folder for .parquet files.")

  args = parser.parse_args()
  process_directory(args.folder, args.output)

if __name__ == "__main__":
  main()