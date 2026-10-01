import argparse
import os
from pathlib import Path


def extract_survey_data(catalog: Path, output: Path, bbox):
  return

def main():
  parser = argparse.ArgumentParser(description="Extract marine geophysical data by bounding box.")
  parser.add_argument("catalog", type=str, help="Path or S3 URI to _cruise_catalog.parquet")
  parser.add_argument("-o", "--output", type=str, required=True, help="Local output file path or directory")
  parser.add_argument("--bbox", type=float, nargs=4, required=True, metavar=('MINX', 'MINY', 'MAXX', 'MAXY'),
                      help="Bounding box: min_lon min_lat max_lon max_lat")

  args = parser.parse_args()
  output_path = args.output
  if os.path.isdir(output_path):
    output_path = os.path.join(output_path, "extracted_subset.parquet")

  extract_survey_data(args.catalog, output_path, args.bbox)

if __name__ == "__main__":
  main()