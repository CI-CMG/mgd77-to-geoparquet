import argparse
from pathlib import Path

def process_directory(folder: Path, output: Path = None):
  """ Takes a source folder as input, returns new mgd77t geoparquet file into output folder specified."""
  # Check for type of source file and read the source .mgd77 or .m77t files into a raw Pandas DataFrame.
  # Parse the .h77t header file (where applicable) into a Python dictionary.

  # Iterate through your centralized schema dictionary from schema.py.
  # If a required column is missing from the raw data, inject it and fill it with nulls
    # Handle possible old formats / edge cases for nulls
  # For existing columns, force them into the required data type
  # Subset and reorder the DataFrame columns to match the order

  # Convert the Pandas DataFrame into a GeoPandas GeoDataFrame.
  # Generate the geometries using the validated longitude and latitude and set the coordinate ref system (EPSG:4326)

  # Use PyArrow to read the parquet data
  # Extract the PyArrow table's existing metadata dictionary
  # Serialize the parsed .h77t header dictionary to a JSON byte string and append
  # Write the finalized PyArrow Table to the destination
  return

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