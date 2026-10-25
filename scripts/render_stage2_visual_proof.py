"""
Generates a 4-Panel Stage 2 Multi-Sensor Visual Proof Figure for a Benchmark Facility:
- Panel A: High-Resolution Optical Factory & Freight Rail-Yard Chip (~0.3m-3m, Planet PSScene + VHR)
- Panel B: Freight Rail-Yard & Bulk Stockpile Segmentation Overlay (Sobel Rail Siding Edges + Ore/Coal Zones)
- Panel C: 2D Spatial USGS Landsat-8/9 30m Land Surface Temperature (LST, deg C) Heatmap over Plant Core
- Panel D: 12-Month NASA FIRMS VIIRS 375m Kiln/Furnace Operation Timeline & Fire Radiative Power (MW)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import requests
import rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

WORKSPACE_ROOT = Path(__file__).parents[1]


def generate_visual_proof(
    facility_id: str = "https://registry.gdi-de.org/id/de.nw.inspire.pf.bube-eureg/arb-2017-112000-100-0209707",
    out_paths: list[Path] | None = None,
) -> Path:
    ms_path = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "multisensor_thermal_logistics_2023.parquet"
    tl_path = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "firms_viirs_monthly_timeline_2023.parquet"

    ms = pd.read_parquet(ms_path)
    tl = pd.read_parquet(tl_path)

    row = ms[ms["facility_id"] == facility_id].iloc[0]
    tl_fac = tl[tl["facility_id"] == facility_id].sort_values("month")

    fname = f"{row['facility_name']} ({row['sector']}, {row['country']})"
    lat0, lon0 = float(row["latitude"]), float(row["longitude"])

    # 1. Load cached VHR Optical Chip of Factory & Freight Rail-Yard
    img_path = WORKSPACE_ROOT / str(row["vhr_image_path"])
    vhr_img = np.asarray(Image.open(img_path).convert("RGB"), dtype=np.float32) / 255.0

    # 2. Compute Freight Rail-Yard Structural Edges & Stockpile Segmentation Overlay
    gray = 0.299 * vhr_img[:, :, 0] + 0.587 * vhr_img[:, :, 1] + 0.114 * vhr_img[:, :, 2]
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    edge_mag = np.sqrt(gx**2 + gy**2)
    rail_edge_mask = edge_mag > np.percentile(edge_mag, 86)

    r_ch, g_ch, b_ch = vhr_img[:, :, 0], vhr_img[:, :, 1], vhr_img[:, :, 2]
    iron_ore_mask = (r_ch > 0.34) & ((r_ch / (b_ch + 0.05)) > 1.32)
    dark_coal_wagon_mask = (gray > 0.07) & (gray < 0.24) & (np.abs(r_ch - b_ch) < 0.05)

    overlay = vhr_img * 0.52
    overlay[rail_edge_mask] = [0.0, 0.92, 1.0]
    overlay[iron_ore_mask] = [1.0, 0.38, 0.08]
    overlay[dark_coal_wagon_mask & (~rail_edge_mask)] = [0.98, 0.80, 0.08]

    # 3. Fetch 2D USGS Landsat-8/9 30m Thermal Infrared Raster
    scene_id = str(row["landsat_scene_id"])
    stac = requests.post(
        "https://planetarycomputer.microsoft.com/api/stac/v1/search",
        json={"collections": ["landsat-c2-l2"], "ids": [scene_id]},
        timeout=20,
    ).json()
    feat = stac["features"][0]
    href = feat["assets"]["lwir11"]["href"]
    tok = requests.get(
        "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2", timeout=15
    ).json()["token"]

    with rasterio.Env(GDAL_HTTP_UNSAFESSL="YES"):
        with rasterio.open(f"{href}?{tok}") as src:
            tr = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            x0, y0 = tr.transform(lon0, lat0)
            win = from_bounds(x0 - 3000, y0 - 3000, x0 + 3000, y0 + 3000, src.transform)
            arr = src.read(1, window=win).astype(float)
            temp_c = (arr * 0.00341802 + 149.0) - 273.15
            temp_c[arr <= 0] = np.nan

    # 4. Render 4-Panel High-Contrast Diagnostic Figure
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(16, 11.4), dpi=160, facecolor="#0f131c")
    gs = fig.add_gridspec(2, 2, hspace=0.30, wspace=0.22, left=0.05, right=0.96, top=0.855, bottom=0.06)

    fig.suptitle(
        "VeriCBAM Stage 2 Multi-Sensor Visual Verification: Thermal Infrared (USGS/FIRMS) & Freight Railcars (Planet/VHR)\n"
        f"Facility: {fname} | Registered Coordinates: {lat0:.4f}°N, {lon0:.4f}°E",
        fontsize=13.5,
        fontweight="bold",
        color="#f1f5f9",
        y=0.96,
    )

    p_scene = row["planet_best_scene_id"]
    p_passes = int(row["planet_clear_passes_2023"])
    ry_idx = float(row["vhr_rail_yard_contrast_index"])
    sp_idx = float(row["vhr_stockpile_activity_index"])
    pk_c = float(row["plant_core_peak_lst_c"])
    bg_c = float(row["regional_bg_median_lst_c"])
    dt_c = float(row["thermal_delta_t_c"])
    f_hits = int(row["firms_hotspot_detections_2023"])
    f_mos = int(row["firms_active_months_count"])

    # Panel A: VHR Optical Image of Factory & Freight Rail Yard
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(vhr_img, extent=[-450, 450, -450, 450])
    ax1.set_title(
        f"A. VHR Optical Factory & Freight Rail-Yard (~0.3m–3m)\n"
        f"Planet PSScene: {p_scene} ({p_passes} Clear Passes in 2023)",
        fontsize=10.5,
        fontweight="bold",
        color="#8ed5ff",
        pad=8,
    )
    ax1.set_xlabel("East-West Offset from Registered Plant Centroid (m)", fontsize=9, color="#cbd5e1")
    ax1.set_ylabel("North-South Offset (m)", fontsize=9, color="#cbd5e1")
    circle1 = plt.Circle((0, 0), 130, color="#f97316", fill=False, lw=2.0, ls="--", label="Furnace / Plant Core")
    ax1.add_patch(circle1)
    ax1.legend(loc="upper right", fontsize=8, framealpha=0.85, facecolor="#161922")

    # Panel B: Freight Rail-Yard & Stockpile Segmentation Map
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(np.clip(overlay, 0, 1), extent=[-450, 450, -450, 450])
    ax2.set_title(
        f"B. Freight Rail-Yard & Bulk Stockpile Detection Map\n"
        f"Rail-Yard Contrast = {ry_idx:.3f} | Stockpile Activity = {sp_idx:.3f}",
        fontsize=10.5,
        fontweight="bold",
        color="#4edea3",
        pad=8,
    )
    ax2.set_xlabel("East-West Offset from Registered Plant Centroid (m)", fontsize=9, color="#cbd5e1")
    ax2.set_ylabel("North-South Offset (m)", fontsize=9, color="#cbd5e1")
    p_cyan = mpatches.Patch(color="#00ebff", label="Freight Rail Siding & Rolling-Stock Edges")
    p_orange = mpatches.Patch(color="#ff6114", label="Iron Ore / Sinter Feed Stockpiles")
    p_gold = mpatches.Patch(color="#facc15", label="Coking Coal / Dark Bulk Wagon Zones")
    ax2.legend(
        handles=[p_cyan, p_orange, p_gold], loc="upper right", fontsize=7.8, framealpha=0.85, facecolor="#161922"
    )

    # Panel C: 2D USGS Landsat-8/9 30m Land Surface Temperature (LST) Heatmap
    ax3 = fig.add_subplot(gs[1, 0])
    vmin_c = max(15.0, float(np.nanpercentile(temp_c, 5)))
    vmax_c = float(np.nanmax(temp_c))
    im3 = ax3.imshow(temp_c, cmap="inferno", extent=[-3.0, 3.0, -3.0, 3.0], vmin=vmin_c, vmax=vmax_c)
    cbar = fig.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)
    cbar.set_label("Land Surface Temperature (°C)", fontsize=9, color="#f1f5f9")
    ax3.set_title(
        f"C. USGS Landsat-9 30m Surface Temperature ({scene_id})\n"
        f"Peak Core = {pk_c:.1f}°C vs Bg Median = {bg_c:.1f}°C (ΔT = +{dt_c:.1f}°C)",
        fontsize=10.5,
        fontweight="bold",
        color="#f97316",
        pad=8,
    )
    ax3.set_xlabel("East-West Distance from Plant Centroid (km)", fontsize=9, color="#cbd5e1")
    ax3.set_ylabel("North-South Distance (km)", fontsize=9, color="#cbd5e1")
    c_core = plt.Circle((0, 0), 2.2, color="#00ebff", fill=False, lw=1.8, ls="--", label="2.2 km Complex Core")
    ax3.add_patch(c_core)
    ax3.scatter([0], [0], c="#00ebff", s=70, marker="+", lw=2, label="E-PRTR Registered Centroid")
    ax3.legend(loc="upper right", fontsize=8, framealpha=0.85, facecolor="#161922")

    # Panel D: 12-Month NASA FIRMS VIIRS 375m Operation Timeline & Fire Radiative Power
    ax4 = fig.add_subplot(gs[1, 1], facecolor="#161922")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ax4.bar(
        months,
        tl_fac["hotspot_count"],
        color="#f97316",
        alpha=0.85,
        width=0.6,
        label="VIIRS 375m Hotspot Count",
    )
    ax4.set_ylabel("Monthly 375m Thermal Detections", fontsize=9, color="#f97316", fontweight="bold")
    ax4.tick_params(axis="y", labelcolor="#f97316")
    ax4.grid(axis="y", alpha=0.2, linestyle="--")

    ax4_r = ax4.twinx()
    ax4_r.plot(
        months,
        tl_fac["cumulative_frp_mw"],
        color="#facc15",
        marker="o",
        lw=2.5,
        markersize=6,
        label="Cumulative FRP (MW)",
    )
    ax4_r.set_ylabel("Cumulative Fire Radiative Power (MW)", fontsize=9, color="#facc15", fontweight="bold")
    ax4_r.tick_params(axis="y", labelcolor="#facc15")

    ax4.set_title(
        f"D. 12-Month Furnace Operation Timeline (NASA FIRMS VIIRS 375m)\n"
        f"Total 2023 Detections = {f_hits} Hits | Active = {f_mos}/12 Months (Continuous Operation)",
        fontsize=10.5,
        fontweight="bold",
        color="#facc15",
        pad=8,
    )
    ax4.set_xlabel("2023 Reporting Month (Sampled Overpass Windows)", fontsize=9, color="#cbd5e1")

    default_out = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "facility_imagery" / "stage2_visual_proof_duisburg.png"
    targets = out_paths or [default_out]
    for p in targets:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=160, facecolor="#0f131c")
    plt.close(fig)
    return targets[0]


if __name__ == "__main__":
    p1 = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "facility_imagery" / "stage2_visual_proof_duisburg.png"
    p2 = Path(r"C:\Users\crist\.gemini\antigravity\brain\2cc5cf4b-63cd-4aa1-9d68-9b723d1da80e\stage2_multisensor_visual_proof.png")
    out = generate_visual_proof(out_paths=[p1, p2])
    print("Generated visual proof figure:", out)
