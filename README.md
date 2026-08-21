# MGD77 to GeoParquet Pipeline

This toolkit modernizes legacy marine geophysical survey data (MGD77 and MGD77T) by converting it into a GeoParquet format. It provides an end-to-end workflow: batch converting raw ASCII files, indexing them into a lightweight spatial catalog, and extracting targeted subsets either locally or directly from an AWS S3 bucket.

Ensure you have `geopandas`, `pandas`, `pyarrow`, and `shapely` installed in your environment before running these tools.

---

## Batch Converter (`mgd77_to_geoparquet.py`)
This script parses legacy fixed-width `.mgd77` and tabular `.m77t` data records, strictly typing the schema and embedding the `.h77t` header metadata directly into the file footer.

* **Usage:** `python mgd77_to_geoparquet.py /path/to/raw_data -o /path/to/output`

## Spatial Catalog Builder (`trackline_geophysics_geoparquet_catalog_builder.py`)
Scans a directory of converted GeoParquet files to build a summary catalog (`_cruise_catalog.parquet`) for fast spatial discovery.

* **Usage:** `python trackline_geophysics_geoparquet_catalog_builder.py /path/to/geoparquet_files -o /path/to/catalog_dir`

## Data Extractor (`extract_trackline_geophysics_data.py`)
Empowers users to query the archive using a spatial bounding box, downloading only the exact data points they need for their analysis.

* **Usage:** `python extract_trackline_geophysics_data.py s3://bucket/_cruise_catalog.parquet subset.parquet --bbox 143.0 13.0 151.0 18.0`
