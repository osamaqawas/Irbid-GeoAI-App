import streamlit as st
import ee
import json
import geemap.foliumap as geemap
from google.oauth2 import service_account

# ============================================================
# 1. Google Earth Engine Authentication
# ============================================================
def authenticate_gee():
    if "GEE_JSON" in st.secrets:
        try:
            info = json.loads(st.secrets["GEE_JSON"])
            scopes = ["https://www.googleapis.com/auth/earthengine"]
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=scopes
            )
            ee.Initialize(credentials=credentials)
            return True
        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
            return False
    return False


# ============================================================
# 2. Page Configuration
# ============================================================
st.set_page_config(layout="wide", page_title="Irbid GeoAI Monitoring System")

st.title("🛰️ Irbid GeoAI Monitoring System")
st.markdown(
    """
    **Advanced GeoAI-based environmental & urban monitoring platform**  
    *Irbid, Jordan | Multi-sensor Remote Sensing & Machine Learning*
    """
)

# ============================================================
# 3. Sidebar – Tool Selector
# ============================================================
st.sidebar.title("🛠️ Analysis Modules")

tool = st.sidebar.selectbox(
    "Select Module",
    [
        "Historical Comparison",
        "ΔNDVI & ΔNDBI Change Detection",
        "Random Forest LULC Classification",
        "Urban Growth Prediction (GeoAI)",
        "SAR Validation (Sentinel-1)",
        "Zonal Statistics (AOI)",
        "Accuracy Assessment"
    ]
)

# ============================================================
# 4. Initialize GEE
# ============================================================
if authenticate_gee():

    # Study area
    irbid_center = [32.55, 35.85]
    point = ee.Geometry.Point(irbid_center[::-1])

    # ========================================================
    # DATASETS
    # ========================================================
    sentinel2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point)
        .filterDate("2024-01-01", "2025-01-01")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 5))
        .median()
    )

    landsat5 = (
        ee.ImageCollection("LANDSAT/LT05/C02/T1_L2")
        .filterBounds(point)
        .filterDate("1985-01-01", "1987-12-31")
        .sort("CLOUD_COVER")
        .first()
    )

    # Indices
    ndvi_2024 = sentinel2.normalizedDifference(["B8", "B4"]).rename("NDVI_2024")
    ndbi_2024 = sentinel2.normalizedDifference(["B11", "B8"]).rename("NDBI_2024")

    ndvi_1985 = landsat5.normalizedDifference(["SR_B4", "SR_B3"]).rename("NDVI_1985")
    ndbi_1985 = landsat5.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDBI_1985")

    # ========================================================
    # A. Historical Comparison
    # ========================================================
    if tool == "Historical Comparison":
        st.subheader("🕰️ Time-Travel: Urban Growth Comparison")
        m = geemap.Map(center=irbid_center, zoom=12)

        left = geemap.ee_tile_layer(
            landsat5,
            {"bands": ["SR_B3", "SR_B2", "SR_B1"], "min": 7000, "max": 12000},
            "Irbid 1985"
        )

        right = geemap.ee_tile_layer(
            sentinel2,
            {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000},
            "Irbid 2024"
        )

        m.split_map(left, right)
        m.to_streamlit(height=650)

    # ========================================================
    # B. ΔNDVI & ΔNDBI
    # ========================================================
    if tool == "ΔNDVI & ΔNDBI Change Detection":
        st.subheader("🌿 Vegetation & Urban Change")

        delta_ndvi = ndvi_2024.subtract(ndvi_1985)
        delta_ndbi = ndbi_2024.subtract(ndbi_1985)

        m = geemap.Map(center=irbid_center, zoom=12)

        # NDVI Legend
        ndvi_vis = {"min": -0.5, "max": 0.5, "palette": ["red", "white", "green"]}
        m.addLayer(delta_ndvi, ndvi_vis, "ΔNDVI")
        m.add_colorbar(vis_params=ndvi_vis, label="ΔNDVI")

        # NDBI Legend
        ndbi_vis = {"min": -0.5, "max": 0.5, "palette": ["green", "white", "red"]}
        m.addLayer(delta_ndbi, ndbi_vis, "ΔNDBI")
        m.add_colorbar(vis_params=ndbi_vis, label="ΔNDBI")

        m.to_streamlit(height=650)

    # ========================================================
    # C. Random Forest LULC
    # ========================================================
    if tool == "Random Forest LULC Classification":
        st.subheader("🗺️ AI-Powered Dynamic World Classification")
        st.info("Using Google & WRI Dynamic World V1 (Near Real-Time AI Classification)")

        # جلب بيانات التصنيف الآلي
        dw = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
            .filterBounds(point) \
            .filterDate("2024-01-01", "2024-12-31") \
            .mosaic() \
            .select('label')

        m = geemap.Map(center=irbid_center, zoom=13)
        
        # الألوان القياسية لـ Dynamic World
        dw_vis = {
            "min": 0, "max": 8,
            "palette": [
                '#419BDF', '#397D49', '#88B053', '#7A87C6', '#E49635', 
                '#DFC351', '#C4281B', '#A59B8F', '#B39FE1'
            ]
        }
        
        m.addLayer(dw, dw_vis, 'Dynamic World LULC')
        
        # إضافة وسيلة الإيضاح
        legend_dict = {
            "Water": "#419BDF", "Trees": "#397D49", "Grass": "#88B053",
            "Flooded Veg": "#7A87C6", "Crops": "#E49635", "Shrub": "#DFC351",
            "Urban": "#C4281B", "Bare Soil": "#A59B8F", "Snow/Ice": "#B39FE1"
        }
        m.add_legend(title="Land Cover Classes", legend_dict=legend_dict)
        m.to_streamlit(height=650)

    # ========================================================
    # D. Urban Growth Prediction
    # ========================================================
    if tool == "Urban Growth Prediction (GeoAI)":
        st.subheader("📈 Urban Growth Prediction (GeoAI)")

        rainfall = (
            ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY")
            .filterDate("2024-01-01", "2025-01-01")
            .select("total_precipitation")
            .sum()
        )

        lights = (
            ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
            .filterDate("2024-01-01", "2025-01-01")
            .median()
            .select("avg_rad")
        )

        predictors = ee.Image.cat([ndvi_2024, ndbi_2024, rainfall, lights])
        model = ee.Classifier.smileRandomForest(300).setOutputMode("PROBABILITY")
        prediction = predictors.classify(model)

        m = geemap.Map(center=irbid_center, zoom=11)
        pred_vis = {"min": 0, "max": 1, "palette": ["green", "yellow", "red"]}
        m.addLayer(prediction, pred_vis, "Urban Growth Probability")
        m.add_colorbar(vis_params=pred_vis, label="Growth Probability")
        m.to_streamlit(height=650)

    # ========================================================
    # E. SAR Validation
    # ========================================================
    if tool == "SAR Validation (Sentinel-1)":
        st.subheader("📡 Sentinel-1 SAR Validation")

        sar = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(point)
            .filterDate("2020-01-01", "2024-12-31")
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .select("VH")
            .median()
        )

        m = geemap.Map(center=irbid_center, zoom=11)
        sar_vis = {"min": -25, "max": -5, "palette": ["black", "white"]}
        m.addLayer(sar, sar_vis, "Sentinel-1 VH")
        m.add_colorbar(vis_params=sar_vis, label="SAR Backscatter (dB)")
        m.to_streamlit(height=650)

    # ========================================================
    # F. Zonal Statistics
    # ========================================================
    if tool == "Zonal Statistics (AOI)":
        st.subheader("📊 Zonal Statistics")

        uploaded = st.file_uploader("Upload AOI (GeoJSON)", type=["geojson"])
        if uploaded:
            aoi = geemap.geojson_to_ee(json.load(uploaded))
            stats = ndvi_2024.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=aoi,
                scale=10,
                maxPixels=1e9
            )
            st.success("Mean NDVI for AOI:")
            st.write(stats.get("NDVI_2024").getInfo())

    # ========================================================
    # G. Accuracy Assessment
    # ========================================================
    if tool == "Accuracy Assessment":
        st.subheader("✅ Accuracy Assessment")
        validated = training.classify(classifier)
        cm = validated.errorMatrix("class", "classification")
        st.write("Confusion Matrix:", cm.getInfo())
        st.write("Overall Accuracy:", cm.accuracy().getInfo())
        st.write("Kappa Coefficient:", cm.kappa().getInfo())

else:
    st.warning("⚠️ Google Earth Engine authentication is required.")
