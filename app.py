import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="TRS-398 Worksheet 6.9 Calculator",
    page_icon="⚛️",
    layout="wide"
)

# Application Header
st.title("⚛️ TRS-398 Worksheet 6.9 Calculator")
st.caption("Determination of the absorbed dose to water in a high-energy photon beam")
st.markdown("---")

# Layout: Two columns for parameters input
col1, col2 = st.columns(2)

with col1:
    st.header("1. Radiation Unit & Reference Conditions")
    accelerator = st.text_input("Accelerator Model / ID", "Elekta / Varian")
    nominal_mv = st.number_input("Nominal Accelerator Potential (MV)", value=6.0, step=1.0)
    beam_quality = st.number_input("Beam Quality Q (TPR20,10)", value=0.680, format="%.3f")
    setup_mode = st.selectbox("Set-up Technique", ["SSD", "SAD"])
    
    st.header("2. Ionization Chamber & Calibration Data")
    chamber_model = st.text_input("Ionization Chamber Model", "Farmer FC65-G")
    n_dw_q0 = st.number_input("Calibration Factor N_D,w,Q0 (Gy/nC)", value=0.05210, format="%.5f")
    k_q = st.number_input("Beam Quality Correction Factor k_Q,Q0", value=0.9850, format="%.4f")
    
    st.header("3. Ambient Reference & Measurement Conditions")
    temp = st.number_input("Current Temperature T (°C)", value=22.0, step=0.1)
    pressure = st.number_input("Current Pressure P (kPa)", value=101.3, step=0.1)

with col2:
    st.header("4. Dosimeter Readings & Influence Corrections")
    mu = st.number_input("Monitor Units (MU)", value=100.0, step=10.0)
    m1_raw = st.number_input("Uncorrected Reading M1 at V1 (nC)", value=15.420, format="%.3f")
    
    st.subheader("Polarity Effect Correction (k_pol)")
    m_plus = st.number_input("Reading at +V1 (nC)", value=15.420, format="%.3f")
    m_minus = st.number_input("Reading at -V1 (nC)", value=-15.380, format="%.3f")
    
    st.subheader("Recombination Correction (k_s)")
    k_s = st.number_input("Recombination Factor k_s", value=1.0020, format="%.4f")
    
    st.subheader("Additional Correction Factors")
    k_elec = st.number_input("Electrometer Calibration Factor k_elec", value=1.0000, format="%.4f")
    k_vol = st.number_input("Volume Averaging Factor k_vol (FFF beams)", value=1.0000, format="%.4f")
    
    st.header("5. Depth Dose Conversion to z_max")
    pdd_or_tmr = st.number_input(f"{'PDD' if setup_mode == 'SSD' else 'TMR'} at Reference Depth z_ref (%)", value=66.80, format="%.2f")

# --- Calculations ---
# 1. Temperature and Pressure Correction Factor (k_TP)
# Reference conditions: T0 = 20 °C, P0 = 101.325 kPa
k_tp = ((273.15 + temp) / (273.15 + 20.0)) * (101.325 / pressure)

# 2. Polarity Correction Factor (k_pol)
if m1_raw != 0:
    k_pol = (abs(m_plus) + abs(m_minus)) / (2 * abs(m1_raw))
else:
    k_pol = 1.0

# 3. Corrected Dosimeter Reading per MU (M_Q)
m_raw_per_mu = m1_raw / mu
m_q = m_raw_per_mu * k_tp * k_elec * k_pol * k_s * k_vol

# 4. Absorbed Dose to Water at Reference Depth z_ref (Gy/MU)
d_w_q_zref = m_q * n_dw_q0 * k_q

# 5. Absorbed Dose to Water at Maximum Dose Depth z_max (Gy/MU)
if setup_mode == "SSD":
    d_w_q_zmax = d_w_q_zref / (pdd_or_tmr / 100.0)
else:  # SAD mode
    d_w_q_zmax = d_w_q_zref / pdd_or_tmr

# Output in cGy per 100 MU
cgy_per_100mu = d_w_q_zmax * 100 * 100

# --- Display Results ---
st.markdown("---")
st.header("📊 Final Dosimetry Calculations")

res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.metric("Pressure & Temp Correction (k_TP)", f"{k_tp:.4f}")
    st.metric("Polarity Correction (k_pol)", f"{k_pol:.4f}")

with res_col2:
    st.metric("Corrected Reading (M_Q)", f"{m_q:.5f} nC/MU")
    st.metric("Dose at z_ref (D_w,Q)", f"{d_w_q_zref:.5f} Gy/MU")

with res_col3:
    st.metric("Dose at z_max (D_w,Q)", f"{d_w_q_zmax:.5f} Gy/MU")
    st.metric("Final Output", f"{cgy_per_100mu:.2f} cGy / 100 MU")

# QA Verification Alert
st.markdown("---")
if 99.0 <= cgy_per_100mu <= 101.0:
    st.success(f"✅ Calibration within tolerance: {cgy_per_100mu:.2f} cGy / 100 MU (Target: 100.0 cGy / 100 MU)")
else:
    st.warning(f"⚠️ Warning: Calculated output ({cgy_per_100mu:.2f} cGy / 100 MU) deviates from standard reference setup (100 cGy). Please verify input parameters.")
