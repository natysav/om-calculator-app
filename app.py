import streamlit as st
import pandas as pd
import math

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def norm_cdf(x, mu, sigma):
    """Standard normal cumulative distribution function (equivalent to Excel NORM.DIST(x, mu, sigma, TRUE))"""
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))

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
        "Week 5: Queuing Theory & Throughput Loss",
        "Week 6: Process Quality & Takt Time"
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
        st.markdown("**Flow Rate** is the number of flow units (e.g., customers, products) that pass through a process per unit of time. It measures the throughput of a process.")
        st.latex(r"\text{Flow Rate} = \frac{\text{Units Produced}}{\text{Time}}")
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
        st.markdown("**Cycle Time** is the average time between consecutive flow units completing the process. It is the inverse of the flow rate.")
        st.latex(r"\text{Cycle Time} = \frac{1}{\text{Flow Rate}}")
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
        st.markdown("**Process Capacity** is determined by the **bottleneck** — the step with the lowest capacity. The bottleneck limits the overall throughput of the entire process.")
        st.latex(r"\text{Process Capacity} = \min(\text{Capacity}_1,\; \text{Capacity}_2,\; \dots,\; \text{Capacity}_n)")
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
        st.markdown("**Little's Law** links the three fundamental process metrics. The average number of flow units in the system (Inventory) equals the flow rate multiplied by the average flow time. It holds for any stable process.")
        st.latex(r"I = R \times T")
        st.markdown("Where **I** = Inventory (units in process), **R** = Flow Rate (throughput), **T** = Flow Time (time a unit spends in the system).")
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
        st.markdown("**Inventory Turns** measures how many times a company's inventory is sold and replaced over a period. Higher turns indicate more efficient inventory management.")
        st.latex(r"\text{Inventory Turns} = \frac{\text{COGS}}{\text{Average Inventory Value}}")
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
    tab1, tab2, tab_util, tab3 = st.tabs(["Labor Cost", "Implied Utilization", "Utilization", "Labor Content"])

    with tab1:
        st.subheader("Cost of Direct Labor")
        st.markdown("**Cost of Direct Labor** is the labor expense incurred to produce one flow unit. It is calculated by dividing total wages by the flow rate.")
        st.latex(r"\text{Cost of Direct Labor} = \frac{\text{Total Wages per Hour}}{\text{Flow Rate (units/hour)}}")
        wages = st.number_input("Total Wages per Hour ($)", value=60.0)
        fr_hr = st.number_input("Flow Rate (Units/Hour)", value=2.0)
        if st.button("Calculate Cost"):
            if fr_hr > 0:
                st.metric("Direct Labor Cost", f"${wages/fr_hr:.2f} per unit")

    with tab2:
        st.subheader("Implied Utilization")
        st.markdown("**Implied Utilization** is the ratio of demand to capacity. If it exceeds 100%, the resource is a bottleneck and cannot meet demand.")
        st.latex(r"\text{Implied Utilization} = \frac{\text{Demand}}{\text{Capacity}}")
        demand = st.number_input("Demand Rate", value=15.0)
        cap = st.number_input("Capacity", value=20.0)
        if st.button("Calculate Implied Util"):
            if cap > 0:
                u = demand/cap
                st.metric("Implied Utilization", f"{u:.2%}")

    with tab_util:
        st.subheader("Utilization")
        st.markdown("**Utilization** is the fraction of capacity actually being used. Unlike implied utilization (which uses demand), this uses the **actual flow rate**.")
        st.latex(r"\text{Utilization} = \frac{\text{Flow Rate}}{\text{Capacity}}")
        flow_rate_u = st.number_input("Flow Rate", value=12.0, key="util_fr")
        capacity_u = st.number_input("Capacity", value=20.0, key="util_cap")
        if st.button("Calculate Utilization"):
            if capacity_u > 0:
                utilization = flow_rate_u / capacity_u
                st.metric("Utilization", f"{utilization:.2%}")
                if utilization > 1.0:
                    st.warning("Utilization exceeds 100% — flow rate cannot sustainably exceed capacity.")

    with tab3:
        st.subheader("Labor Content")
        st.markdown("**Labor Content** is the total amount of labor time required to produce one flow unit. It is the sum of all individual activity times across workers.")
        st.latex(r"\text{Labor Content} = \sum_{i=1}^{n} \text{Activity Time}_i")
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
    st.markdown("**Capacity with Batching** accounts for the setup time incurred each time a new batch is started. Larger batches spread the fixed setup cost over more units, increasing effective capacity.")
    st.latex(r"\text{Capacity} = \frac{\text{Batch Size}}{\text{Setup Time} + \text{Batch Size} \times \text{Processing Time per Unit}}")

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
    tab_queue, tab_loss, tab_abandon = st.tabs(["Waiting Time (Queue)", "Throughput Loss (Erlang Loss)", "Adjusted Wait (Willingness to Wait)"])

    # --- Standard Queue (G/G/m) ---
    with tab_queue:
        st.subheader("Standard Queue (G/G/m)")
        st.markdown("**Waiting Time in Queue** estimates how long a customer waits before being served, using the G/G/m approximation. Use when customers **wait in line** (e.g., call centers, checkout lines).")
        st.latex(r"T_q = \frac{p}{m} \;\times\; \frac{u^{\sqrt{2(m+1)}-1}}{1-u} \;\times\; \frac{CV_a^2 + CV_p^2}{2}")
        st.markdown("""
Where: **p** = processing time, **m** = number of servers, **u** = utilization (*p / (a × m)*),
**a** = interarrival time, **CV_a** = coefficient of variation of arrivals, **CV_p** = coefficient of variation of processing.
""")

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
                    st.error(
                        "⚠️ System Unstable (u ≥ 100%) — demand exceeds capacity. "
                        "The queue grows without bound, so waiting time → ∞. "
                        "Customers with finite patience will leave — use the **Throughput Loss (Erlang Loss)** tab to model this."
                    )
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
        st.markdown("**Erlang Loss Model** applies when there is **no waiting room** — arriving customers who find all servers busy are lost (e.g., ambulance diversion, hotel overbooking). It calculates the probability that an arriving customer is turned away.")
        st.latex(r"r = \lambda \times p \qquad \text{(Traffic Intensity)}")
        st.latex(r"B(m, r) = \frac{r \cdot B(m-1,\, r)}{m + r \cdot B(m-1,\, r)}, \quad B(0,r)=1")
        st.markdown("""
Where: **r** = traffic intensity, **λ** = arrival rate (1/a), **p** = processing time,
**m** = number of servers, **B(m, r)** = probability of loss (all servers busy).
""")
        st.caption("Use when there is **NO Waiting Room** (e.g., Ambulance diversion).")

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

    # --- Adjusted Wait (Willingness to Wait) ---
    with tab_abandon:
        st.subheader("Adjusted Wait Time (with Customer Abandonment)")
        st.markdown(
            "The **Waiting Time (Queue)** tab assumes all customers wait indefinitely. "
            "The **Erlang Loss** tab assumes no one waits at all. "
            "Reality is in between: customers wait up to a limit, then leave. "
            "When impatient customers leave, the queue shrinks, reducing wait for those who stay."
        )
        st.markdown(
            "This calculator iteratively adjusts the effective arrival rate to find the "
            "**equilibrium waiting time** — the point where the fraction of customers "
            "abandoning is consistent with the resulting queue length."
        )

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            m_adj = st.number_input("Number of Servers (m)", min_value=1, value=2, key="adj_m")
            a_adj_val = st.number_input("Interarrival Time (a)", value=5.0, key="adj_a")
            a_adj_unit = st.selectbox("Unit (a)", ["Seconds", "Minutes", "Hours"], index=1, key="adj_a_unit")

        with col_a2:
            p_adj_val = st.number_input("Processing Time (p)", value=6.0, key="adj_p")
            p_adj_unit = st.selectbox("Unit (p)", ["Seconds", "Minutes", "Hours"], index=1, key="adj_p_unit")

        with col_a3:
            cv_a_adj = st.number_input("CV of Arrivals (CVa)", value=1.0, key="adj_cva")
            cv_p_adj = st.number_input("CV of Process (CVp)", value=0.5, key="adj_cvp")

        st.divider()
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            w_val = st.number_input("Willingness to Wait (W)", value=5.0, min_value=0.01, key="adj_w")
        with col_w2:
            w_unit = st.selectbox("Unit (W)", ["Seconds", "Minutes", "Hours"], index=1, key="adj_w_unit")

        a_adj_min = to_minutes(a_adj_val, a_adj_unit)
        p_adj_min = to_minutes(p_adj_val, p_adj_unit)
        w_adj_min = to_minutes(w_val, w_unit)

        if st.button("Calculate Adjusted Wait"):
            if a_adj_min > 0 and m_adj > 0 and w_adj_min > 0:
                var_term = (cv_a_adj**2 + cv_p_adj**2) / 2
                exp_val = math.sqrt(2 * (m_adj + 1)) - 1

                # Step 1: Unadjusted Tq (full demand, everyone waits)
                util_full = p_adj_min / (a_adj_min * m_adj)

                if util_full <= 0:
                    st.info("No demand — waiting time is 0.")
                elif util_full >= 1.0:
                    st.error(
                        f"⚠️ System unstable at full demand (u = {util_full:.2%}). "
                        "Queue grows without bound — all customers with finite patience will leave."
                    )
                    st.markdown("Iterating to find the equilibrium with abandonment...")

                    # Even with u>=1, abandonment can stabilize the system
                    a_eff = a_adj_min
                    tq_adj = None
                    frac_abandon = 0.0
                    for i in range(200):
                        # Increase effective interarrival time (fewer customers)
                        # Start by assuming some leave, which lowers utilization
                        if i == 0:
                            # Initial guess: enough leave to bring util to 0.95
                            frac_abandon = max(0, 1 - (0.95 * a_adj_min * m_adj / p_adj_min))
                        a_eff = a_adj_min / (1 - frac_abandon) if frac_abandon < 1 else a_adj_min * 100
                        u_eff = p_adj_min / (a_eff * m_adj)
                        if u_eff >= 1.0:
                            frac_abandon = min(frac_abandon + 0.01, 0.99)
                            continue
                        t1 = p_adj_min / m_adj
                        t2 = (u_eff ** exp_val) / (1 - u_eff)
                        tq_iter = t1 * t2 * var_term
                        new_frac = math.exp(-w_adj_min / tq_iter) if tq_iter > 0 else 0
                        if abs(new_frac - frac_abandon) < 0.0001:
                            tq_adj = tq_iter
                            frac_abandon = new_frac
                            break
                        frac_abandon = frac_abandon * 0.7 + new_frac * 0.3
                    else:
                        # Use last values if didn't fully converge
                        tq_adj = tq_iter
                        frac_abandon = new_frac

                    if tq_adj is not None:
                        u_eff_final = p_adj_min / (a_eff * m_adj)
                        st.divider()
                        st.markdown("### Equilibrium Results")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Adjusted Waiting Time", f"{tq_adj:.2f} min")
                        c2.metric("Customers Abandoning", f"{frac_abandon:.2%}")
                        c3.metric("Effective Utilization", f"{u_eff_final:.2%}")

                        demand_per_min = 1 / a_adj_min
                        served_per_min = demand_per_min * (1 - frac_abandon)
                        lost_per_min = demand_per_min * frac_abandon
                        st.divider()
                        cr1, cr2 = st.columns(2)
                        cr1.metric("Customers Served", f"{served_per_min * 60:.2f} / hr")
                        cr2.metric("Customers Lost", f"{lost_per_min * 60:.2f} / hr")
                else:
                    # System is stable — compute unadjusted Tq first
                    t1_full = p_adj_min / m_adj
                    t2_full = (util_full ** exp_val) / (1 - util_full)
                    tq_full = t1_full * t2_full * var_term

                    st.markdown("### Unadjusted (all customers wait)")
                    c1, c2 = st.columns(2)
                    c1.metric("Utilization", f"{util_full:.2%}")
                    c2.metric("Avg Waiting Time (Tq)", f"{tq_full:.2f} min")

                    if tq_full <= w_adj_min:
                        st.success(
                            f"Avg wait ({tq_full:.2f} min) is already within patience ({w_adj_min:.2f} min). "
                            "Minimal abandonment expected — the standard G/G/m result applies."
                        )
                    else:
                        st.warning(f"Avg wait ({tq_full:.2f} min) exceeds patience ({w_adj_min:.2f} min). Iterating to find equilibrium...")

                        # Iterative adjustment
                        a_eff = a_adj_min
                        frac_abandon = 0.0
                        tq_adj = tq_full
                        for i in range(200):
                            new_frac = math.exp(-w_adj_min / tq_adj) if tq_adj > 0 else 0
                            if abs(new_frac - frac_abandon) < 0.0001:
                                frac_abandon = new_frac
                                break
                            frac_abandon = frac_abandon * 0.7 + new_frac * 0.3
                            a_eff = a_adj_min / (1 - frac_abandon) if frac_abandon < 1 else a_adj_min * 100
                            u_eff = p_adj_min / (a_eff * m_adj)
                            if u_eff >= 1.0:
                                continue
                            t1 = p_adj_min / m_adj
                            t2 = (u_eff ** exp_val) / (1 - u_eff)
                            tq_adj = t1 * t2 * var_term

                        u_eff_final = p_adj_min / (a_eff * m_adj)
                        st.divider()
                        st.markdown("### Equilibrium Results (after abandonment)")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Adjusted Waiting Time", f"{tq_adj:.2f} min")
                        c2.metric("Customers Abandoning", f"{frac_abandon:.2%}")
                        c3.metric("Effective Utilization", f"{u_eff_final:.2%}")

                        demand_per_min = 1 / a_adj_min
                        served_per_min = demand_per_min * (1 - frac_abandon)
                        lost_per_min = demand_per_min * frac_abandon
                        st.divider()
                        cr1, cr2 = st.columns(2)
                        cr1.metric("Customers Served", f"{served_per_min * 60:.2f} / hr")
                        cr2.metric("Customers Lost", f"{lost_per_min * 60:.2f} / hr")

# ==========================================
# WEEK 6: PROCESS QUALITY & TAKT TIME
# ==========================================
elif week_selection == "Week 6: Process Quality & Takt Time":
    st.header("Week 6: Process Quality & Takt Time")
    tab_cap, tab_takt, tab_lost = st.tabs(["Process Capability (k-sigma)", "Takt Time", "Customer Lost Rate"])

    # --- Process Capability (k-sigma) ---
    with tab_cap:
        st.subheader("Process Capability (k-sigma)")
        st.markdown(
            "A process is **capable** if it delivers the quality demanded by the customer. "
            "A process is said to be **k-sigma** if the distance between the distribution mean "
            "and both specification limits (USL and LSL) is at least *k* times the process standard deviation."
        )
        st.latex(r"k = \min\!\left(\frac{\text{USL} - \mu}{\sigma},\; \frac{\mu - \text{LSL}}{\sigma}\right)")
        st.markdown(
            "Where: **μ** = process mean, **σ** = process standard deviation, "
            "**USL** / **LSL** = upper / lower specification limits. "
            "A k-sigma process means **both** spec limits are at least *k* standard deviations from the mean."
        )
        st.markdown(
            "A higher *k* means the process is more capable. "
            "Reference: **1σ** ≈ 68.27%, **2σ** ≈ 95.45%, **3σ** ≈ 99.73%, **6σ** ≈ 99.9999998%."
        )

        col1, col2 = st.columns(2)
        with col1:
            mean_val = st.number_input("Process Mean (μ)", value=50.0, key="cap_mean")
            sigma_val = st.number_input("Standard Deviation (σ)", value=2.0, min_value=0.001, key="cap_sigma")
        with col2:
            usl = st.number_input("Upper Specification Limit (USL)", value=56.0, key="cap_usl")
            lsl = st.number_input("Lower Specification Limit (LSL)", value=44.0, key="cap_lsl")

        if st.button("Calculate Process Capability"):
            if sigma_val > 0 and usl > lsl:
                # Process Capability = P(LSL < X < USL)
                # = NORM.DIST(USL, Mean, Sigma, TRUE) - NORM.DIST(LSL, Mean, Sigma, TRUE)
                capability = norm_cdf(usl, mean_val, sigma_val) - norm_cdf(lsl, mean_val, sigma_val)
                defect_rate = 1 - capability

                st.divider()
                st.markdown("### Process Capability")
                st.latex(r"\text{Capability} = \Phi\!\left(\frac{\text{USL} - \mu}{\sigma}\right) - \Phi\!\left(\frac{\text{LSL} - \mu}{\sigma}\right)")
                c1, c2 = st.columns(2)
                c1.metric("Process Capability", f"{capability:.3%}")
                c2.metric("Defect Rate", f"{defect_rate:.3%}")

                # k-sigma: distance from mean to nearest spec limit, in standard deviations
                k_upper = (usl - mean_val) / sigma_val
                k_lower = (mean_val - lsl) / sigma_val
                k_value = min(k_upper, k_lower)

                st.divider()
                st.markdown("### k-sigma Analysis")
                c1, c2, c3 = st.columns(3)
                c1.metric("k (sigma level)", f"{k_value:.2f}")
                c2.metric("Distance to USL", f"{k_upper:.2f}σ")
                c3.metric("Distance to LSL", f"{k_lower:.2f}σ")

                if k_value >= 6:
                    st.success(f"Process is **{k_value:.1f}-sigma** — Six Sigma level. Near-zero defects.")
                elif k_value >= 3:
                    st.success(f"Process is **{k_value:.1f}-sigma** — capable (≈ {capability:.2%} within limits).")
                elif k_value >= 2:
                    st.warning(f"Process is **{k_value:.1f}-sigma** — marginally capable. ~{defect_rate:.2%} defect rate.")
                elif k_value >= 0:
                    st.error(f"Process is **{k_value:.1f}-sigma** — NOT capable. ~{defect_rate:.2%} defect rate.")
                else:
                    st.error(f"Process mean is outside the specification limits!")
            elif usl <= lsl:
                st.error("USL must be greater than LSL.")
            else:
                st.error("Standard deviation must be greater than 0.")

    # --- Takt Time ---
    with tab_takt:
        st.subheader("Takt Time Calculator")
        st.markdown(
            "**Takt Time** is the rate at which you need to complete a product to meet customer demand. "
            "It is the total available production time divided by the quantity of product demanded. "
            "Takt time sets the pace of a **pull system** — production is driven by actual demand rather than forecasts."
        )
        st.latex(r"\text{Takt Time} = \frac{\text{Available Production Time}}{\text{Customer Demand}}")
        st.markdown(
            "Where: **Available Production Time** = total working time in a period (e.g., minutes per day), "
            "**Customer Demand** = number of units required in the same period."
        )

        col1, col2 = st.columns(2)
        with col1:
            avail_time = st.number_input("Available Production Time", value=480.0, key="takt_time")
            time_unit_takt = st.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=0, key="takt_time_unit")
        with col2:
            demand_takt = st.number_input("Customer Demand (units in same period)", value=240.0, min_value=0.01, key="takt_demand")

        n_workers = st.number_input("Number of Workers (optional, for cycle time comparison)", value=1, min_value=1, key="takt_workers")

        if st.button("Calculate Takt Time"):
            avail_min = to_minutes(avail_time, time_unit_takt)
            if avail_min > 0 and demand_takt > 0:
                takt = avail_min / demand_takt
                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("Takt Time", f"{takt:.4f} min/unit")
                c2.metric("Takt Time", f"{takt * 60:.2f} sec/unit")

                st.info(
                    f"To meet demand, one unit must be completed every **{takt:.2f} minutes** "
                    f"({takt * 60:.1f} seconds)."
                )

                if n_workers > 1:
                    effective_takt = takt * n_workers
                    st.metric("Effective Time per Worker", f"{effective_takt:.4f} min/unit",
                              help="Each worker has this much time per unit if work is balanced across workers")
            else:
                st.error("Both available time and demand must be greater than 0.")

    # --- Customer Lost Rate ---
    with tab_lost:
        st.subheader("Customer Lost Rate & Output Flow Rate")
        st.markdown(
            "The **Output Flow Rate** is the rate at which customers actually receive service. "
            "When a process cannot handle all incoming demand (due to capacity limits or lost customers), "
            "the **Customer Lost Rate** measures how many potential customers are turned away per unit of time."
        )
        st.latex(r"\text{Output Flow Rate} = \text{Demand Rate} \times (1 - P_{\text{loss}})")
        st.latex(r"\text{Customer Lost Rate} = \text{Demand Rate} \times P_{\text{loss}}")
        st.markdown(
            "Where: **Demand Rate** = incoming customer rate, "
            "**P_loss** = probability that a customer is lost (e.g., from Erlang Loss model or observed data)."
        )

        col1, col2 = st.columns(2)
        with col1:
            demand_rate_lr = st.number_input("Demand Rate", value=10.0, key="lr_demand")
            demand_unit_lr = st.selectbox("Rate Unit", ["Per Minute", "Per Hour", "Per Day"], index=1, key="lr_demand_unit")
        with col2:
            p_loss_input = st.number_input("Probability of Loss (P_loss)", value=0.05, min_value=0.0, max_value=1.0, step=0.01, key="lr_ploss")

        sample_size = st.number_input("Sample Size (N) — for reference only", value=100, min_value=1, key="lr_n")

        if st.button("Calculate Lost Rate"):
            # Normalize demand to per-hour
            if demand_unit_lr == "Per Minute":
                demand_hr = demand_rate_lr * 60
            elif demand_unit_lr == "Per Day":
                demand_hr = demand_rate_lr / 24
            else:
                demand_hr = demand_rate_lr

            output_flow = demand_hr * (1 - p_loss_input)
            lost_rate = demand_hr * p_loss_input

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Demand Rate", f"{demand_hr:.2f} / hr")
            c2.metric("Output Flow Rate", f"{output_flow:.2f} / hr")
            c3.metric("Customer Lost Rate", f"{lost_rate:.2f} / hr")

            st.divider()
            st.markdown("### Daily Projections")
            d1, d2 = st.columns(2)
            d1.metric("Customers Served / Day", f"{output_flow * 24:.0f}")
            d2.metric("Customers Lost / Day", f"{lost_rate * 24:.0f}")

            if p_loss_input > 0.10:
                st.warning(f"Loss rate is {p_loss_input:.0%} — consider adding capacity or reducing processing time.")
            elif p_loss_input > 0:
                st.info(f"Loss rate of {p_loss_input:.0%} is within typical ranges for many service systems.")