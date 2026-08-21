import argparse
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import box

def extract_survey_data(minx: float, miny: float, maxx: float, maxy: float, catalog_path: str, output_path: str):
  """Extracts trackline data within a bounding box from a GeoParquet catalog."""
  bbox = (minx, miny, maxx, maxy)
  aoi_polygon = box(*bbox)

  abs_catalog_path = os.path.abspath(catalog_path)
  print(f"Loading catalog from: {catalog_path}")

  catalog = gpd.read_parquet(catalog_path)

  if "FILE_PATH" not in catalog.columns:
    print(f"Error: 'FILE_PATH' missing in catalog at '{abs_catalog_path}'. Please re-run catalog builder.")
    return

  intersecting = catalog.cx[minx:maxx, miny:maxy]

  if intersecting.empty:
    print("No surveys found in this area.")
    return

  survey_ids = intersecting["SURVEY_ID"].unique().tolist()
  print(f"Found {len(survey_ids)} matching surveys: {', '.join(survey_ids)}")

  if catalog_path.startswith("s3://"):
    base_dir = catalog_path.rsplit("/", 1)[0]
  else:
    base_dir = os.path.dirname(catalog_path) or "."

  data_frames = []

  for idx, row in intersecting.iterrows():
    file_path = f"{base_dir}/{row['FILE_PATH']}"
    print(f"Fetching data from {row['SURVEY_ID']} ({file_path})...")

    # Fallback to spatial index filtering if bbox pushdown isn't supported
    try:
      gdf = gpd.read_parquet(file_path, bbox=bbox)
    except ValueError:
      gdf = gpd.read_parquet(file_path)
      gdf = gdf.cx[minx:maxx, miny:maxy]

    if not gdf.empty:
      data_frames.append(gdf)

  if not data_frames:
    print("No matching data points found inside the bounding box.")
    return

  master_gdf = pd.concat(data_frames, ignore_index=True)
  master_gdf = master_gdf.clip(aoi_polygon)
  master_gdf.to_parquet(output_path, compression="zstd")
  print("Extraction complete!")

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

  extract_survey_data(args.bbox[0], args.bbox[1], args.bbox[2], args.bbox[3], args.catalog, output_path)

if __name__ == "__main__":
  main()