[Readme.txt](https://github.com/user-attachments/files/24402804/Readme.txt)
# 🛰️ Irbid GeoAI Monitoring System

### GeoAI Platform for Geographic Analysis in Irbid

## 📝 Project Description

A GeoAI-powered web application built with Streamlit and Google Earth Engine (GEE). This platform enables users to monitor environmental and climatic changes in the Irbid region, Jordan. It provides near real-time analysis of precipitation patterns (ERA5-Land), vegetation health (NDVI), and radar-based surface changes (Sentinel-1 SAR data).

---

## 🚀 Key Features

* **Climate Monitoring:** Interactive monthly rainfall maps using ERA5-Land data.
* **Vegetation Analysis:** Real-time NDVI calculation using Sentinel-2 imagery.
* **Radar Observation:** Surface change detection using Sentinel-1 (SAR) data.
* **Dynamic ROI:** Support for custom Areas of Interest (AOI) through uploaded GeoJSON files.
* **Interactive Dashboard:** User-friendly interface with synchronized maps and charts for intuitive exploration.

---

## 🛠️ Tech Stack

* **Programming Language:** Python 3.x
* **Cloud Platform:** Google Earth Engine (GEE)
* **Web Framework:** Streamlit
* **Geospatial Libraries:** `geemap`, `leafmap`, `geopandas`, `xarray`, `xee`

---

## 📂 Project Structure

```text
├── app.py              # Main application script
├── requirements.txt    # Python dependencies
├── roi.geojson         # Study area boundaries
└── README.md           # Project documentation
```
