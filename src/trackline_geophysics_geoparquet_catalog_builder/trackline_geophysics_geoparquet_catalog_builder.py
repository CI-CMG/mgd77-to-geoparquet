import argparse
from pathlib import Path


def build_spatial_catalog(parquet_dir: Path, output_dir: Path = None, catalog_filename: str = "_cruise_catalog.parquet"):
  return


def main():
  parser = argparse.ArgumentParser(description="Builds a spatial catalog from a directory of GeoParquet cruise files.")
  parser.add_argument("folder", type=Path, help="Directory containing the GeoParquet data files.")
  parser.add_argument("-o", "--output", type=Path, default=None, help="Destination folder for the catalog file.")
  parser.add_argument("--catalog-name", type=str, default="_cruise_catalog.parquet", help="Name of the output catalog file.")

  args = parser.parse_args()
  build_spatial_catalog(args.folder, args.output, args.catalog_name)

if __name__ == "__main__":
  main()