import streamlit as st
import pandas as pd
import math

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def to_minutes(value, unit):
    """Converts any time unit to Minutes"""
    if unit == "Seconds": return value / 60
    elif unit == "Minutes": return value
    elif unit == "Hours": return value * 60
    elif unit == "Days": return value * 60 * 24
    return value

def calculate_erlang_table(m_servers, r_intensity):
    """
    Returns a dataframe showing the probability of loss for every server count 
    from 1 up to m_servers.
    """
    data = []
    # Base case: for 0 servers, probability of loss is 1 (100%)
    p_loss = 1.0
    
    for i in range(1, int(m_servers) + 1):
        # Recursive Erlang B formula: B(m, r) = (r * B(m-1, r)) / (m + r * B(m-1, r))
        if r_intensity > 0:
            numerator = r_intensity * p_loss
            denominator = i + (r_intensity * p_loss)
            p_loss = numerator / denominator
        else:
            p_loss = 0
            
        data.append({
            "Servers (m)": i,
            "Traffic Intensity (r)": r_intensity,
            "P(Loss) %": p_loss * 100,
            "P(Loss) Factor": p_loss
        })
    
    return pd.DataFrame(data), p_loss

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Operations Management Toolkit", layout="wide", page_icon="🏭")

st.title("🏭 Operations Management Toolkit")
st.markdown("""
Select a **Week** from the sidebar. Time units are **automatically converted** to ensure accuracy.
""")

# --- Sidebar Navigation ---
week_selection = st.sidebar.selectbox(
    "Select Module",
    [
        "Week 1: Process Fundamentals",
        "Week 2: Inventory & Little's Law",
        "Week 3: Capacity & Labor",
        "Week 4: Batches & Setup",
        "Week 5: Queuing Theory & Throughput Loss"
    ]
)

# ==========================================
# WEEK 1: PROCESS FUNDAMENTALS
# ==========================================
if week_selection == "Week 1: Process Fundamentals":
    st.header("Week 1: Process Fundamentals")
    
    tab1, tab2, tab3 = st.tabs(["Flow Rate", "Cycle Time", "Process Capacity"])

    # --- Flow Rate ---
    with tab1:
        st.subheader("Flow Rate Calculator")
        c1, c2 = st.columns(2)
        units = c1.number_input("Units Produced", value=100.0)
        time_val = c2.number_input("Time Taken", value=1.0)
        time_unit = c2.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=1)
        
        if st.button("Calculate Flow Rate"):
            t_mins = to_minutes(time_val, time_unit)
            if t_mins > 0:
                fr_min = units / t_mins
                st.success(f"Flow Rate: **{fr_min:.2f} units/min**")
                st.info(f"Equivalent to: **{fr_min*60:.2f} units/hour**")
            else:
                st.error("Time must be > 0")

    # --- Cycle Time ---
    with tab2:
        st.subheader("Cycle Time Calculator")
        c1, c2 = st.columns(2)
        fr_val = c1.number_input("Flow Rate", value=5.0)
        fr_unit = c1.selectbox("Rate Unit", ["Units/Minute", "Units/Hour", "Units/Day"], index=1)
        
        if st.button("Calculate Cycle Time"):
            if fr_unit == "Units/Hour": fr_min = fr_val / 60
            elif fr_unit == "Units/Day": fr_min = fr_val / 1440
            else: fr_min = fr_val
            
            if fr_min > 0:
                ct_min = 1 / fr_min
                st.success(f"Cycle Time: **{ct_min:.2f} minutes/unit**")
            else:
                st.error("Flow Rate must be > 0")

    # --- Process Capacity ---
    with tab3:
        st.subheader("Process Capacity (Bottleneck)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Enter capacities for up to 3 steps:**")
            s1 = st.number_input("Step 1 Capacity", value=100.0)
            s2 = st.number_input("Step 2 Capacity", value=80.0)
            s3 = st.number_input("Step 3 Capacity", value=120.0)
            
        if st.button("Find Bottleneck"):
            b_neck = min(s1, s2, s3)
            st.success(f"Process Capacity: **{b_neck}** (Limited by the lowest step)")

# ==========================================
# WEEK 2: INVENTORY & LITTLE'S LAW
# ==========================================
elif week_selection == "Week 2: Inventory & Little's Law":
    st.header("Week 2: Inventory & Little's Law")
    tab1, tab2 = st.tabs(["Little's Law Calculator", "Inventory Turns"])

    with tab1:
        st.subheader("Little's Law")
        st.latex(r"I = R \times T")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            r_val = st.number_input("Flow Rate (R)", value=10.0)
            r_unit = st.selectbox("Unit (R)", ["Units/Minute", "Units/Hour", "Units/Day"], index=1)
        with col2:
            t_val = st.number_input("Flow Time (T)", value=2.0)
            t_unit = st.selectbox("Unit (T)", ["Minutes", "Hours", "Days"], index=1)
        with col3:
            st.markdown("#### Result")
            if st.button("Calculate Inventory"):
                if r_unit == "Units/Hour": r_norm = r_val / 60
                elif r_unit == "Units/Day": r_norm = r_val / 1440
                else: r_norm = r_val
                
                t_norm = to_minutes(t_val, t_unit)
                st.metric("Inventory (I)", f"{r_norm * t_norm:.2f} units")

    with tab2:
        st.subheader("Inventory Turns")
        cogs = st.number_input("Cost of Goods Sold (COGS)", value=1000000.0)
        inv_val = st.number_input("Average Inventory Value", value=100000.0)
        if st.button("Calculate Turns"):
            if inv_val > 0:
                st.metric("Inventory Turns", f"{cogs/inv_val:.2f}")

# ==========================================
# WEEK 3: CAPACITY & LABOR
# ==========================================
elif week_selection == "Week 3: Capacity & Labor":
    st.header("Week 3: Capacity & Labor")
    tab1, tab2, tab3 = st.tabs(["Labor Cost", "Implied Utilization", "Labor Content"])

    with tab1:
        st.subheader("Cost of Direct Labor")
        wages = st.number_input("Total Wages per Hour ($)", value=60.0)
        fr_hr = st.number_input("Flow Rate (Units/Hour)", value=2.0)
        if st.button("Calculate Cost"):
            if fr_hr > 0:
                st.metric("Direct Labor Cost", f"${wages/fr_hr:.2f} per unit")

    with tab2:
        st.subheader("Implied Utilization")
        demand = st.number_input("Demand Rate", value=15.0)
        cap = st.number_input("Capacity", value=20.0)
        if st.button("Calculate Implied Util"):
            if cap > 0:
                u = demand/cap
                st.metric("Implied Utilization", f"{u:.2%}")

    with tab3:
        st.subheader("Labor Content")
        times = st.text_input("Task Times (Minutes, comma separated)", "1.0, 0.5, 2.5")
        if st.button("Sum Labor Content"):
            try:
                t_list = [float(x.strip()) for x in times.split(',')]
                st.success(f"Total Labor Content: **{sum(t_list):.2f} minutes**")
            except:
                st.error("Invalid format.")

# ==========================================
# WEEK 4: BATCHES & SETUP
# ==========================================
elif week_selection == "Week 4: Batches & Setup":
    st.header("Week 4: Batches & Setup")
    st.subheader("Capacity with Batching")
    
    c1, c2 = st.columns(2)
    b_size = c1.number_input("Batch Size", value=10.0)
    s_time = c1.number_input("Setup Time (per batch)", value=10.0)
    s_unit = c1.selectbox("Setup Unit", ["Minutes", "Hours"], index=0)
    
    p_time = c2.number_input("Processing Time (per unit)", value=1.0)
    p_unit = c2.selectbox("Processing Unit", ["Minutes", "Hours"], index=0)
    
    if st.button("Calculate Batch Capacity"):
        s_min = to_minutes(s_time, s_unit)
        p_min = to_minutes(p_time, p_unit)
        denom = s_min + (b_size * p_min)
        if denom > 0:
            cap_min = b_size / denom
            st.success(f"Capacity: **{cap_min:.4f} units/minute**")
            st.info(f"({cap_min*60:.2f} units/hour)")

# ==========================================
# WEEK 5: QUEUING & THROUGHPUT LOSS
# ==========================================
elif week_selection == "Week 5: Queuing Theory & Throughput Loss":
    st.header("Week 5: Queuing & Capacity")
    tab_queue, tab_loss = st.tabs(["Waiting Time (Queue)", "Throughput Loss (Erlang Loss)"])

    # --- Standard Queue (G/G/m) ---
    with tab_queue:
        st.subheader("Standard Queue (G/G/m)")
        st.caption("Use when customers WAIT in line (e.g., Call center).")
        
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            m = st.number_input("Number of Servers (m)", min_value=1, value=2)
            a_val = st.number_input("Interarrival Time (a)", value=5.0)
            a_unit = st.selectbox("Unit (a)", ["Seconds", "Minutes", "Hours"], index=1, key="q_a")
            
        with col_in2:
            p_val = st.number_input("Processing Time (p)", value=6.0)
            p_unit = st.selectbox("Unit (p)", ["Seconds", "Minutes", "Hours"], index=1, key="q_p")
            
        with col_in3:
            cv_a = st.number_input("CV of Arrivals (CVa)", value=1.0)
            cv_p = st.number_input("CV of Process (CVp)", value=0.5)
            
        # Normalize to Minutes
        a_min = to_minutes(a_val, a_unit)
        p_min = to_minutes(p_val, p_unit)
            
        if st.button("Calculate Waiting Time (Tq)"):
            if a_min > 0 and m > 0:
                util = p_min / (a_min * m)
                st.metric("Utilization", f"{util:.2%}")
                
                if util >= 1.0:
                    st.error("⚠️ System Unstable (u ≥ 100%)")
                elif util > 0:
                    term1 = p_min / m
                    exponent = math.sqrt(2 * (m + 1)) - 1
                    term2 = (util ** exponent) / (1 - util)
                    term3 = (cv_a**2 + cv_p**2) / 2
                    tq = term1 * term2 * term3
                    st.success(f"Avg Waiting Time: **{tq:.2f} mins**")

    # --- Throughput Loss (Erlang Loss) ---
    with tab_loss:
        st.subheader("Throughput Loss (Erlang Loss)")
        st.caption("Use when there is **NO Waiting Room** (e.g., Ambulance diversion). Matches 'Calculator.csv'.")

        # Input Method Selection
        input_method = st.radio("Select Input Method:", ["Interarrival Time (a)", "Demand Rate (1/a)"], horizontal=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if input_method == "Interarrival Time (a)":
                val_a = st.number_input("Average Interarrival Time", value=3.0)
                unit_a = st.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=1, key="loss_a")
                # Calculate Lambda (per hour for reference)
                a_hours = to_minutes(val_a, unit_a) / 60
                lam = 1/a_hours if a_hours > 0 else 0
            else:
                val_d = st.number_input("Demand Rate", value=8.0)
                unit_d = st.selectbox("Rate Unit", ["Per Minute", "Per Hour", "Per Day"], index=2, key="loss_d")
                # Calculate Lambda (per hour)
                if unit_d == "Per Minute": lam = val_d * 60
                elif unit_d == "Per Day": lam = val_d / 24
                else: lam = val_d

        with col2:
            proc_time = st.number_input("Average Processing Time", value=2.0)
            proc_unit = st.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=1, key="loss_p")
            # Calculate P (in hours)
            p_hours = to_minutes(proc_time, proc_unit) / 60

        with col3:
            m_loss = st.number_input("Number of Servers (m)", value=3, min_value=1, key="loss_m")

        if st.button("Calculate Loss Metrics"):
            # 1. Calculate Traffic Intensity (r) = Demand/Hour * ProcessTime/Hour
            # (unitless)
            r = lam * p_hours
            
            # 2. Calculate Erlang Loss Table
            df_table, p_loss_final = calculate_erlang_table(m_loss, r)
            
            # 3. Key Metrics
            # Implied Util (if no loss)
            implied_util = r / m_loss
            
            # Actual Util (accounting for loss) -> This matches your spreadsheet (0.216)
            actual_util = (r * (1 - p_loss_final)) / m_loss
            
            # Flow Rates
            demand_rate_display = lam  # In units/hour
            loss_rate = demand_rate_display * p_loss_final
            flow_rate = demand_rate_display * (1 - p_loss_final)
            
            # Display
            st.divider()
            c_res1, c_res2, c_res3, c_res4 = st.columns(4)
            c_res1.metric("Traffic Intensity (r)", f"{r:.3f}")
            c_res2.metric("Prob. of Loss", f"{p_loss_final:.2%}")
            c_res3.metric("Throughput Loss", f"{loss_rate:.2f} / hr")
            c_res4.metric("Actual Flow Rate", f"{flow_rate:.2f} / hr")
            
            st.divider()
            
            # The specific metric requested
            st.markdown("### Utilization Metrics")
            cu1, cu2 = st.columns(2)
            cu1.metric("Implied Utilization", f"{implied_util:.2%}", help="Demand / Capacity")
            cu2.metric("Average Utilisation", f"{actual_util:.6f}", help="Matches your worksheet: (Flow Rate / Capacity)")
            
            if abs(actual_util - 0.216561) < 0.001:
                st.caption("✅ Matches the '0.216561' from your example file.")

            # Table
            st.subheader("Calculation Table")
            st.dataframe(df_table.style.format({
                "P(Loss) %": "{:.2f}%", 
                "P(Loss) Factor": "{:.6f}", 
                "Traffic Intensity (r)": "{:.4f}"
            }))