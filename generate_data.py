"""Generate synthetic healthcare procurement spend data."""
import random
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

FACILITIES = {
    "Memorial Regional Medical Center": 1.35,
    "St. Joseph's University Hospital": 1.15,
    "Valley Health System — Main Campus": 1.0,
    "Northside Community Hospital": 0.65,
    "Riverside General Hospital": 0.85,
}

CATEGORY_TARGET_SPEND = {
    "Orthopedics": 12_500_000,
    "Biomedical Equipment": 10_000_000,
    "Surgical Supplies": 7_500_000,
    "Biologics & Wound Care": 6_000_000,
    "Radiology": 5_000_000,
    "Clinical Engineering Services": 4_000_000,
    "Vascular": 3_000_000,
    "Other/Miscellaneous": 2_000_000,
}

CATEGORY_TARGET_TXNS = {
    "Orthopedics": 1100,
    "Biomedical Equipment": 550,
    "Surgical Supplies": 1400,
    "Biologics & Wound Care": 700,
    "Radiology": 450,
    "Clinical Engineering Services": 400,
    "Vascular": 500,
    "Other/Miscellaneous": 500,
}

CATEGORY_VENDORS: dict[str, list[tuple[str, float]]] = {
    "Orthopedics": [
        ("Stryker", 0.22),
        ("DePuy Synthes", 0.20),
        ("Zimmer Biomet", 0.18),
        ("Smith+Nephew", 0.15),
        ("Medtronic", 0.10),
        ("Arthrex", 0.08),
        ("Globus Medical", 0.04),
        ("NuVasive", 0.03),
    ],
    "Biomedical Equipment": [
        ("GE Healthcare", 0.25),
        ("Philips", 0.22),
        ("Siemens Healthineers", 0.20),
        ("Agiliti", 0.15),
        ("Medtronic", 0.10),
        ("BD", 0.08),
    ],
    "Surgical Supplies": [
        ("Cardinal Health", 0.25),
        ("BD", 0.20),
        ("Teleflex", 0.15),
        ("B.Braun", 0.15),
        ("Baxter", 0.12),
        ("Medtronic", 0.08),
        ("Boston Scientific", 0.05),
    ],
    "Biologics & Wound Care": [
        ("Integra LifeSciences", 0.22),
        ("Smith+Nephew", 0.18),
        ("ConvaTec", 0.16),
        ("Molnlycke", 0.15),
        ("KCI (3M+KCI)", 0.14),
        ("Medtronic", 0.08),
        ("Baxter", 0.07),
    ],
    "Radiology": [
        ("GE Healthcare", 0.28),
        ("Philips", 0.25),
        ("Siemens Healthineers", 0.22),
        ("Hologic", 0.15),
        ("Canon Medical", 0.10),
    ],
    "Clinical Engineering Services": [
        ("Sodexo", 0.30),
        ("Agiliti", 0.25),
        ("GE Healthcare", 0.20),
        ("Philips", 0.15),
        ("Siemens Healthineers", 0.10),
    ],
    "Vascular": [
        ("Boston Scientific", 0.25),
        ("Medtronic", 0.22),
        ("Abbott", 0.20),
        ("Teleflex", 0.15),
        ("BD", 0.10),
        ("B.Braun", 0.08),
    ],
    "Other/Miscellaneous": [
        ("Cardinal Health", 0.30),
        ("BD", 0.20),
        ("Baxter", 0.15),
        ("B.Braun", 0.15),
        ("Teleflex", 0.10),
        ("Sodexo", 0.10),
    ],
}

PRODUCTS: dict[str, list[tuple[str, float, float]]] = {
    "Orthopedics": [
        ("Primary Total Hip System", 4500, 8500),
        ("Revision Hip Stem Component", 5500, 10000),
        ("Acetabular Cup w/ Liner", 2800, 5200),
        ("Primary Total Knee System", 4200, 7800),
        ("Revision Knee Tibial Baseplate", 3500, 6500),
        ("Partial Knee Unicompartmental System", 3200, 5800),
        ("Cervical Interbody Fusion Cage", 2200, 4500),
        ("Thoracolumbar Pedicle Screw Set", 1800, 3800),
        ("Spinal Rod System (Titanium)", 1200, 2800),
        ("Intramedullary Nail — Femoral", 1500, 3200),
        ("Intramedullary Nail — Tibial", 1200, 2800),
        ("Locking Plate System — Distal Radius", 800, 1800),
        ("Locking Plate System — Proximal Humerus", 900, 2200),
        ("Cannulated Screw Set (6.5mm)", 350, 850),
        ("Shoulder Arthroplasty System", 4800, 9200),
        ("Reverse Shoulder System", 5200, 9800),
        ("ACL Reconstruction Graft System", 1800, 3500),
        ("Meniscal Repair Device", 600, 1400),
        ("Bone Cement (40g)", 120, 350),
        ("Surgical Power Drill — Ortho", 2500, 5500),
    ],
    "Biomedical Equipment": [
        ("Patient Monitor — Bedside", 3500, 8500),
        ("Infusion Pump — Dual Channel", 2800, 6200),
        ("Ventilator — ICU", 18000, 35000),
        ("Defibrillator — Biphasic", 8000, 16000),
        ("Surgical Table — Powered", 25000, 55000),
        ("Electrosurgical Unit", 4500, 9500),
        ("Pulse Oximeter — Portable", 450, 1200),
        ("ECG Machine — 12-Lead", 3200, 7500),
        ("Suction Unit — Portable", 800, 2200),
        ("Sequential Compression Device", 1200, 3000),
        ("Fluid Warmer System", 2500, 5500),
        ("Surgical Headlight — LED", 1800, 4200),
        ("Transport Monitor", 5500, 12000),
        ("Bed — Med-Surg Electric", 6000, 14000),
        ("Stretcher — Emergency", 3500, 8000),
    ],
    "Surgical Supplies": [
        ("Surgical Stapler — Linear", 180, 450),
        ("Stapler Reload Cartridge (6-pack)", 250, 550),
        ("Hemostatic Agent — Topical", 120, 380),
        ("Surgical Suture — Absorbable (box)", 85, 220),
        ("Surgical Suture — Non-Absorbable (box)", 75, 195),
        ("Laparoscopic Trocar Set", 280, 650),
        ("Energy Device — Ultrasonic Shears", 350, 850),
        ("Surgical Drain — Closed Suction", 45, 120),
        ("Wound Closure Strip (box)", 35, 85),
        ("Irrigation Solution — 3L", 25, 65),
        ("Surgical Gloves — Sterile (case)", 85, 180),
        ("Surgical Gown — Sterile (case)", 120, 280),
        ("Drape — Surgical (case)", 95, 240),
        ("Scalpel — Disposable (box)", 40, 95),
        ("Specimen Container — Sterile (case)", 55, 130),
    ],
    "Biologics & Wound Care": [
        ("Skin Substitute — Bioengineered (per cm²)", 350, 1200),
        ("Bone Graft Substitute — DBM Putty", 800, 2200),
        ("Negative Pressure Wound Therapy Kit", 450, 1100),
        ("NPWT Canister/Dressing Change Kit", 120, 350),
        ("Collagen Wound Dressing (box)", 180, 450),
        ("Antimicrobial Silver Dressing (box)", 150, 380),
        ("Foam Dressing — Adhesive (box)", 65, 180),
        ("Alginate Dressing (box)", 75, 200),
        ("Platelet-Rich Plasma Prep Kit", 350, 850),
        ("Tissue Sealant — Fibrin (5mL)", 280, 650),
        ("Hemostatic Matrix (5mL)", 320, 750),
        ("Bone Morphogenetic Protein Kit", 3500, 7500),
        ("Amniotic Membrane Allograft", 800, 2500),
    ],
    "Radiology": [
        ("CT Contrast Agent — Iodinated (case)", 450, 1200),
        ("MRI Contrast Agent — Gadolinium (case)", 550, 1400),
        ("X-Ray Cassette — Digital DR Panel", 8000, 18000),
        ("Ultrasound Probe — Linear", 5500, 14000),
        ("Ultrasound Probe — Convex", 4800, 12000),
        ("Biopsy Needle — CT-Guided (box)", 280, 650),
        ("Mammography QC Phantom", 1200, 3500),
        ("Radiation Dosimeter Badge (quarterly)", 35, 85),
        ("Lead Apron — Lightweight", 250, 650),
        ("CR Imaging Plate", 1500, 4000),
        ("PACS Storage License — Annual", 8000, 22000),
        ("Fluoroscopy Drape (case)", 180, 450),
    ],
    "Clinical Engineering Services": [
        ("PM Service — Patient Monitors (quarterly)", 800, 2200),
        ("PM Service — Infusion Pumps (quarterly)", 600, 1600),
        ("PM Service — Ventilators (quarterly)", 1200, 3200),
        ("Calibration Service — Defibrillators", 350, 850),
        ("Repair Parts — Electrosurgical Unit", 400, 1200),
        ("Biomedical Equipment Inspection", 250, 700),
        ("Annual Safety Testing — OR Suite", 1500, 4000),
        ("Equipment Lifecycle Assessment", 2000, 5500),
        ("On-Call Service Contract — Monthly", 3500, 8500),
        ("Firmware Update Service — Monitors", 450, 1200),
    ],
    "Vascular": [
        ("Drug-Eluting Stent", 2200, 5500),
        ("Bare Metal Stent", 1200, 3000),
        ("PTA Balloon Catheter", 800, 2200),
        ("Peripheral Atherectomy Device", 2500, 5800),
        ("Vascular Graft — PTFE", 1500, 3800),
        ("Central Venous Catheter Kit", 85, 250),
        ("PICC Line Kit", 120, 350),
        ("Dialysis Catheter Kit", 150, 400),
        ("Embolization Coil (each)", 450, 1200),
        ("Vascular Closure Device", 280, 650),
        ("Guidewire — Hydrophilic", 120, 350),
        ("Introducer Sheath Set", 95, 280),
    ],
    "Other/Miscellaneous": [
        ("Hand Sanitizer — Wall Mount (case)", 45, 120),
        ("Sharps Container (case)", 65, 160),
        ("Exam Gloves — Nitrile (case)", 35, 95),
        ("Face Mask — Surgical (case)", 25, 75),
        ("Isolation Gown (case)", 55, 150),
        ("Linen — Disposable Underpads (case)", 40, 110),
        ("Thermometer — Digital (each)", 15, 45),
        ("Blood Pressure Cuff — Disposable (box)", 60, 160),
        ("Wheelchair — Standard", 350, 850),
        ("Walker — Folding", 80, 220),
        ("Crutches — Aluminum (pair)", 25, 65),
        ("IV Pole — Rolling", 120, 320),
    ],
}

PPI_CATEGORIES = {
    "Orthopedics": 0.95,
    "Biologics & Wound Care": 0.65,
    "Vascular": 0.55,
    "Biomedical Equipment": 0.10,
    "Surgical Supplies": 0.05,
    "Radiology": 0.05,
    "Clinical Engineering Services": 0.02,
    "Other/Miscellaneous": 0.02,
}

CONTRACT_WEIGHTS = {
    "Orthopedics": {"GPO": 0.45, "Local": 0.35, "Off-Contract": 0.20},
    "Biomedical Equipment": {
        "GPO": 0.50, "Local": 0.35, "Off-Contract": 0.15,
    },
    "Surgical Supplies": {
        "GPO": 0.70, "Local": 0.20, "Off-Contract": 0.10,
    },
    "Biologics & Wound Care": {
        "GPO": 0.45, "Local": 0.35, "Off-Contract": 0.20,
    },
    "Radiology": {"GPO": 0.55, "Local": 0.30, "Off-Contract": 0.15},
    "Clinical Engineering Services": {
        "GPO": 0.40, "Local": 0.45, "Off-Contract": 0.15,
    },
    "Vascular": {"GPO": 0.50, "Local": 0.30, "Off-Contract": 0.20},
    "Other/Miscellaneous": {
        "GPO": 0.65, "Local": 0.25, "Off-Contract": 0.10,
    },
}

MONTHLY_SEASONALITY = {
    1: 1.08, 2: 1.05, 3: 1.06, 4: 1.02, 5: 1.00, 6: 0.98,
    7: 0.90, 8: 0.92, 9: 1.00, 10: 1.03, 11: 1.01, 12: 0.95,
}


def _pick_quantity(category: str) -> int:
    """Pick a realistic quantity based on category."""
    if category in ("Surgical Supplies", "Other/Miscellaneous"):
        return random.choices(
            range(1, 25),
            weights=[
                20, 15, 12, 10, 8, 6, 5, 4, 3, 3,
                2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            ],
        )[0]
    if category in (
        "Biomedical Equipment", "Clinical Engineering Services",
    ):
        return random.choices(
            [1, 2, 3, 4, 5], weights=[60, 20, 10, 5, 5],
        )[0]
    return random.choices(
        range(1, 10),
        weights=[40, 20, 15, 10, 5, 4, 3, 2, 1],
    )[0]


def generate_data() -> pd.DataFrame:
    """Generate synthetic healthcare procurement spend data.

    Generates transactions per category to approximate target spend
    distributions, then scales to hit ~$50M total.
    """
    records: list[dict] = []
    transaction_id = 100001
    date_range = pd.date_range("2024-01-01", "2025-12-31", freq="D")

    facility_names = list(FACILITIES.keys())
    facility_weights_raw = list(FACILITIES.values())
    total_fw = sum(facility_weights_raw)
    facility_weights = [w / total_fw for w in facility_weights_raw]

    for category, n_txns in CATEGORY_TARGET_TXNS.items():
        target_spend = CATEGORY_TARGET_SPEND[category]
        vendor_options = CATEGORY_VENDORS[category]
        v_names = [v[0] for v in vendor_options]
        v_weights_raw = [v[1] for v in vendor_options]
        total_vw = sum(v_weights_raw)
        v_weights = [w / total_vw for w in v_weights_raw]
        products = PRODUCTS[category]

        cat_records: list[dict] = []
        cat_spend = 0.0

        for _ in range(n_txns):
            date = np.random.choice(date_range)
            date = pd.Timestamp(date)
            month = date.month
            seasonality = MONTHLY_SEASONALITY[month]

            facility = np.random.choice(
                facility_names, p=facility_weights
            )

            vendor = np.random.choice(v_names, p=v_weights)

            product_name, price_low, price_high = random.choice(
                products
            )
            unit_price = round(
                random.uniform(price_low, price_high) * seasonality, 2
            )
            quantity = _pick_quantity(category)
            total_amount = round(unit_price * quantity, 2)

            contract_dist = CONTRACT_WEIGHTS[category]
            contract_type = np.random.choice(
                list(contract_dist.keys()),
                p=list(contract_dist.values()),
            )

            if contract_type == "Off-Contract":
                premium = random.uniform(1.15, 1.30)
                unit_price = round(unit_price * premium, 2)
                total_amount = round(unit_price * quantity, 2)

            ppi_rate = PPI_CATEGORIES[category]
            ppi_flag = random.random() < ppi_rate

            record = {
                "transaction_id": f"TXN-{transaction_id}",
                "transaction_date": date.strftime("%Y-%m-%d"),
                "facility_name": facility,
                "department": category,
                "spend_category": category,
                "vendor_name": vendor,
                "product_description": product_name,
                "unit_price": unit_price,
                "quantity": quantity,
                "total_amount": total_amount,
                "contract_type": contract_type,
                "ppi_flag": ppi_flag,
            }
            cat_records.append(record)
            cat_spend += total_amount
            transaction_id += 1

        # Scale transactions to hit target spend
        if cat_spend > 0:
            scale_factor = target_spend / cat_spend
            for rec in cat_records:
                rec["unit_price"] = round(
                    rec["unit_price"] * scale_factor, 2
                )
                rec["total_amount"] = round(
                    rec["unit_price"] * rec["quantity"], 2
                )

        records.extend(cat_records)

    df = pd.DataFrame(records)
    df = df.sort_values("transaction_date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_data()
    output_path = (
        Path(__file__).parent / "data" / "synthetic_spend_data.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows")
    print(f"Total spend: ${df['total_amount'].sum():,.2f}")
    print(
        f"Date range: {df['transaction_date'].min()} to "
        f"{df['transaction_date'].max()}"
    )
    print(f"Facilities: {df['facility_name'].nunique()}")
    print(f"Vendors: {df['vendor_name'].nunique()}")
    print(f"Categories: {df['spend_category'].nunique()}")
    print(f"PPI %: {df['ppi_flag'].mean():.1%}")
    print("\nSpend by category:")
    cat_spend = (
        df.groupby("spend_category")["total_amount"]
        .sum()
        .sort_values(ascending=False)
    )
    for cat, spend in cat_spend.items():
        pct = spend / df["total_amount"].sum() * 100
        print(f"  {cat}: ${spend:,.0f} ({pct:.1f}%)")
    print("\nContract type distribution:")
    for ct, count in df["contract_type"].value_counts().items():
        print(f"  {ct}: {count} ({count / len(df):.1%})")
    print("\nTop 10 vendors by spend:")
    vendor_spend = (
        df.groupby("vendor_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    for v, spend in vendor_spend.items():
        pct = spend / df["total_amount"].sum() * 100
        print(f"  {v}: ${spend:,.0f} ({pct:.1f}%)")
