import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import pyarrow.parquet as pq
from shapely.geometry import box

def build_spatial_catalog(parquet_dir: Path, output_dir: Path = None, catalog_filename: str = "_cruise_catalog.parquet"):
  """Scans a directory of GeoParquet files and builds a spatial bounding box catalog."""
  if not parquet_dir.is_dir():
    print(f"Error: Directory '{parquet_dir}' does not exist.", file=sys.stderr)
    return

  # If an output directory is specified, create it. Otherwise, save in the input folder.
  if output_dir:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_dir = output_dir
  else:
    out_dir = parquet_dir

  catalog_path = out_dir / catalog_filename
  catalog_records = []

  print(f"Scanning '{parquet_dir}' for GeoParquet files...")

  for pq_file in parquet_dir.glob("*.parquet"):
    # Skip the catalog file itself if it happens to be in the same folder
    if pq_file.name == catalog_filename:
      continue

    try:
      schema = pq.read_schema(pq_file)

      # Extract survey metadata
      meta_bytes = schema.metadata.get(b"h77t_metadata")
      if not meta_bytes:
        print(f"Skipping {pq_file.name}: No embedded h77t_metadata found.")
        continue

      survey_meta = json.loads(meta_bytes.decode("utf-8")).get("fields", {})

      # Extract the spatial bounding box from standard GeoParquet metadata
      geo_bytes = schema.metadata.get(b"geo")
      geometry = None
      if geo_bytes:
        geo_meta = json.loads(geo_bytes.decode("utf-8"))
        bbox = geo_meta.get("columns", {}).get("geometry", {}).get("bbox")
        if bbox and len(bbox) == 4:
          geometry = box(*bbox)

      date_dep = str(survey_meta.get("DATE_DEP", ""))
      year = date_dep[:4] if len(date_dep) >= 4 else None

      # Build the catalog row
      record = {
        "SURVEY_ID": str(survey_meta.get("SURVEY_ID", "UNKNOWN")),
        "PLATFORM": str(survey_meta.get("PLATFORM", "")),
        "INST_SRC": str(survey_meta.get("INST_SRC", "")),
        "CHIEF": str(survey_meta.get("CHIEF", "")),
        "PROJECT": str(survey_meta.get("PROJECT", "")),
        "YEAR": year,
        "FILE_PATH": pq_file.name,
        "geometry": geometry
      }
      catalog_records.append(record)

    except Exception as e:
      print(f"Error reading metadata from {pq_file.name}: {e}")

  if not catalog_records:
    print("No valid survey records found to build the catalog.")
    return

  # Convert to GeoDataFrame
  catalog_gdf = gpd.GeoDataFrame(catalog_records, crs="EPSG:4326")

  # Enforce strict data types for the catalog
  for col in ["SURVEY_ID", "PLATFORM", "INST_SRC", "CHIEF", "PROJECT", "YEAR", "FILE_PATH"]:
    catalog_gdf[col] = catalog_gdf[col].astype("string")

  catalog_gdf.to_parquet(catalog_path, compression="zstd")
  print("Catalog generation complete!")


def main():
  parser = argparse.ArgumentParser(description="Builds a spatial catalog from a directory of GeoParquet cruise files.")
  parser.add_argument("folder", type=Path, help="Directory containing the GeoParquet data files.")
  parser.add_argument("-o", "--output", type=Path, default=None, help="Destination folder for the catalog file.")
  parser.add_argument("--catalog-name", type=str, default="_cruise_catalog.parquet", help="Name of the output catalog file.")

  args = parser.parse_args()
  build_spatial_catalog(args.folder, args.output, args.catalog_name)

if __name__ == "__main__":
  main()