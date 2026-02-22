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
# FORMULA-STYLE INPUT HELPERS
# ==========================================

def formula_op(text):
    """Render a centered operator symbol vertically aligned with number inputs."""
    st.markdown(
        f'<div style="text-align:center; font-size:1.5em; font-weight:bold; '
        f'color:#555; padding-top:32px; line-height:1;">{text}</div>',
        unsafe_allow_html=True
    )

def formula_label(text):
    """Render a result label aligned with number inputs."""
    st.markdown(
        f'<div style="text-align:right; font-size:1.15em; font-weight:600; '
        f'color:#333; padding-top:34px; line-height:1;">{text}</div>',
        unsafe_allow_html=True
    )

def formula_text(text):
    """Render inline formula text aligned with number inputs."""
    st.markdown(
        f'<div style="text-align:center; font-size:1.05em; '
        f'color:#444; padding-top:34px; line-height:1;">{text}</div>',
        unsafe_allow_html=True
    )

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
        "Week 6: Process Quality & Takt Time",
        "Week 7: Manish & Adele Wedding"
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

        # Formula-style input
        c_lbl, c_eq, c_num, c_div, c_den = st.columns([1.5, 0.3, 2, 0.3, 2])
        with c_lbl:
            formula_label("Flow Rate")
        with c_eq:
            formula_op("=")
        with c_num:
            units = st.number_input("Units Produced", value=100.0)
        with c_div:
            formula_op("÷")
        with c_den:
            time_val = st.number_input("Time Taken", value=1.0)
            time_unit = st.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=1)

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

        # Formula-style input
        c_lbl, c_eq, c_one, c_div, c_fr = st.columns([1.5, 0.3, 0.8, 0.3, 2])
        with c_lbl:
            formula_label("Cycle Time")
        with c_eq:
            formula_op("=")
        with c_one:
            formula_text("1")
        with c_div:
            formula_op("÷")
        with c_fr:
            fr_val = st.number_input("Flow Rate", value=5.0)
            fr_unit = st.selectbox("Rate Unit", ["Units/Minute", "Units/Hour", "Units/Day"], index=1)

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

        # Formula-style input: Capacity = min( S1 , S2 , S3 )
        c_lbl, c_eq, c_min, c_s1, c_c1, c_s2, c_c2, c_s3, c_par = st.columns([1.5, 0.3, 0.6, 1.5, 0.3, 1.5, 0.3, 1.5, 0.3])
        with c_lbl:
            formula_label("Capacity")
        with c_eq:
            formula_op("=")
        with c_min:
            formula_text("min (")
        with c_s1:
            s1 = st.number_input("Step 1 Capacity", value=100.0)
        with c_c1:
            formula_op(",")
        with c_s2:
            s2 = st.number_input("Step 2 Capacity", value=80.0)
        with c_c2:
            formula_op(",")
        with c_s3:
            s3 = st.number_input("Step 3 Capacity", value=120.0)
        with c_par:
            formula_text(")")

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

        # Formula-style input: I = R × T
        c_lbl, c_eq, c_r, c_mul, c_t = st.columns([1, 0.3, 2.5, 0.3, 2.5])
        with c_lbl:
            formula_label("I")
        with c_eq:
            formula_op("=")
        with c_r:
            r_val = st.number_input("Flow Rate (R)", value=10.0)
            r_unit = st.selectbox("Unit (R)", ["Units/Minute", "Units/Hour", "Units/Day"], index=1)
        with c_mul:
            formula_op("×")
        with c_t:
            t_val = st.number_input("Flow Time (T)", value=2.0)
            t_unit = st.selectbox("Unit (T)", ["Minutes", "Hours", "Days"], index=1)

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

        # Formula-style input: Turns = COGS ÷ Avg Inventory
        c_lbl, c_eq, c_cogs, c_div, c_inv = st.columns([1.5, 0.3, 2, 0.3, 2])
        with c_lbl:
            formula_label("Turns")
        with c_eq:
            formula_op("=")
        with c_cogs:
            cogs = st.number_input("Cost of Goods Sold (COGS)", value=1000000.0)
        with c_div:
            formula_op("÷")
        with c_inv:
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

        # Formula-style input: Cost = Wages ÷ Flow Rate
        c_lbl, c_eq, c_w, c_div, c_fr = st.columns([1.5, 0.3, 2, 0.3, 2])
        with c_lbl:
            formula_label("Cost")
        with c_eq:
            formula_op("=")
        with c_w:
            wages = st.number_input("Total Wages per Hour ($)", value=60.0)
        with c_div:
            formula_op("÷")
        with c_fr:
            fr_hr = st.number_input("Flow Rate (Units/Hour)", value=2.0)

        if st.button("Calculate Cost"):
            if fr_hr > 0:
                st.metric("Direct Labor Cost", f"${wages/fr_hr:.2f} per unit")

    with tab2:
        st.subheader("Implied Utilization")
        st.markdown("**Implied Utilization** is the ratio of demand to capacity. If it exceeds 100%, the resource is a bottleneck and cannot meet demand.")
        st.latex(r"\text{Implied Utilization} = \frac{\text{Demand}}{\text{Capacity}}")

        # Formula-style input: u = Demand ÷ Capacity
        c_lbl, c_eq, c_d, c_div, c_cap = st.columns([1.5, 0.3, 2, 0.3, 2])
        with c_lbl:
            formula_label("u")
        with c_eq:
            formula_op("=")
        with c_d:
            demand = st.number_input("Demand Rate", value=15.0)
        with c_div:
            formula_op("÷")
        with c_cap:
            cap = st.number_input("Capacity", value=20.0)

        if st.button("Calculate Implied Util"):
            if cap > 0:
                u = demand/cap
                st.metric("Implied Utilization", f"{u:.2%}")

    with tab_util:
        st.subheader("Utilization")
        st.markdown("**Utilization** is the fraction of capacity actually being used. Unlike implied utilization (which uses demand), this uses the **actual flow rate**.")
        st.latex(r"\text{Utilization} = \frac{\text{Flow Rate}}{\text{Capacity}}")

        # Formula-style input: u = Flow Rate ÷ Capacity
        c_lbl, c_eq, c_fr, c_div, c_cap = st.columns([1.5, 0.3, 2, 0.3, 2])
        with c_lbl:
            formula_label("u")
        with c_eq:
            formula_op("=")
        with c_fr:
            flow_rate_u = st.number_input("Flow Rate", value=12.0, key="util_fr")
        with c_div:
            formula_op("÷")
        with c_cap:
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

        # Formula-style input: Total = Σ ( task times )
        c_lbl, c_eq, c_sig, c_inp = st.columns([1.5, 0.3, 0.5, 4])
        with c_lbl:
            formula_label("Total")
        with c_eq:
            formula_op("=")
        with c_sig:
            formula_op("Σ")
        with c_inp:
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
    tab_batch_cap, tab_batch_size, tab_eoq = st.tabs(["Capacity with Batching", "Recommended Batch Size", "Economic Order Quantity (EOQ)"])

    # --- Capacity with Batching ---
    with tab_batch_cap:
        st.subheader("Capacity with Batching")
        st.markdown("**Capacity with Batching** accounts for the setup time incurred each time a new batch is started. Larger batches spread the fixed setup cost over more units, increasing effective capacity.")
        st.latex(r"\text{Capacity} = \frac{\text{Batch Size}}{\text{Setup Time} + \text{Batch Size} \times \text{Processing Time per Unit}}")

        # Formula-style input — fraction layout
        # Numerator row
        c_left, c_right = st.columns([1.5, 5])
        with c_left:
            st.markdown("")
            st.markdown("")
            st.markdown(
                '<div style="text-align:right; font-size:1.15em; font-weight:600; '
                'color:#333; padding-top:20px; line-height:1;">Capacity &nbsp;=</div>',
                unsafe_allow_html=True
            )
        with c_right:
            b_size = st.number_input("Batch Size (B)", value=10.0)
            # Fraction bar
            st.markdown(
                '<hr style="margin: 2px 0; border: none; border-top: 2px solid #555;">',
                unsafe_allow_html=True
            )
            # Denominator: Setup + B × Processing
            d1, d_op1, d2, d_op2, d3 = st.columns([2, 0.5, 2, 0.5, 2])
            with d1:
                s_time = st.number_input("Setup Time (per batch)", value=10.0)
                s_unit = st.selectbox("Setup Unit", ["Minutes", "Hours"], index=0)
            with d_op1:
                formula_op("+ B ×")
            with d2:
                p_time = st.number_input("Processing Time (per unit)", value=1.0)
                p_unit = st.selectbox("Processing Unit", ["Minutes", "Hours"], index=0)

        if st.button("Calculate Batch Capacity"):
            s_min = to_minutes(s_time, s_unit)
            p_min = to_minutes(p_time, p_unit)
            denom = s_min + (b_size * p_min)
            if denom > 0:
                cap_min = b_size / denom
                st.success(f"Capacity: **{cap_min:.4f} units/minute**")
                st.info(f"({cap_min*60:.2f} units/hour)")

    # --- Recommended Batch Size ---
    with tab_batch_size:
        st.subheader("Recommended Batch Size")
        st.markdown(
            "**Recommended Batch Size** finds the minimum batch size needed to achieve a desired flow rate. "
            "This is the batch size that matches the process capacity to the desired throughput — "
            "large enough to avoid being the bottleneck, but no larger (to minimize inventory)."
        )
        st.latex(r"\text{Recommended Batch Size} = \frac{\text{Flow Rate} \times \text{Setup Time}}{1 - \text{Flow Rate} \times \text{Time per Unit}}")

        # Formula-style input — fraction layout
        c_left, c_right = st.columns([1.5, 5])
        with c_left:
            st.markdown("")
            st.markdown("")
            st.markdown(
                '<div style="text-align:right; font-size:1.15em; font-weight:600; '
                'color:#333; padding-top:20px; line-height:1;">B &nbsp;=</div>',
                unsafe_allow_html=True
            )
        with c_right:
            # Numerator: Flow Rate × Setup Time
            n1, n_op, n2 = st.columns([2, 0.5, 2])
            with n1:
                desired_fr = st.number_input("Desired Flow Rate", value=0.4, key="bs_fr")
                fr_unit_bs = st.selectbox("Rate Unit", ["Units/Minute", "Units/Hour"], index=0, key="bs_fr_unit")
            with n_op:
                formula_op("×")
            with n2:
                setup_bs = st.number_input("Setup Time", value=120.0, key="bs_setup")
                setup_unit_bs = st.selectbox("Setup Unit", ["Minutes", "Hours"], index=0, key="bs_setup_unit")
            # Fraction bar
            st.markdown(
                '<hr style="margin: 2px 0; border: none; border-top: 2px solid #555;">',
                unsafe_allow_html=True
            )
            # Denominator: 1 - Flow Rate × Time per unit
            d_one, d_minus, d_fr, d_mul, d_p = st.columns([0.4, 0.3, 1.5, 0.3, 2])
            with d_one:
                formula_text("1")
            with d_minus:
                formula_op("−")
            with d_fr:
                formula_text("Flow Rate")
            with d_mul:
                formula_op("×")
            with d_p:
                proc_bs = st.number_input("Processing Time per Unit", value=2.0, key="bs_proc")
                proc_unit_bs = st.selectbox("Processing Unit", ["Minutes", "Hours"], index=0, key="bs_proc_unit")

        if st.button("Calculate Recommended Batch Size"):
            # Normalize to minutes
            setup_min = to_minutes(setup_bs, setup_unit_bs)
            proc_min = to_minutes(proc_bs, proc_unit_bs)

            # Normalize flow rate to units/minute
            if fr_unit_bs == "Units/Hour":
                fr_per_min = desired_fr / 60
            else:
                fr_per_min = desired_fr

            denominator = 1 - (fr_per_min * proc_min)

            if denominator <= 0:
                st.error(
                    "The desired flow rate exceeds the maximum possible capacity of "
                    f"**{1/proc_min:.4f} units/min** ({60/proc_min:.2f} units/hr). "
                    "Even with an infinitely large batch, this flow rate cannot be achieved."
                )
            elif fr_per_min <= 0:
                st.error("Flow rate must be greater than 0.")
            else:
                numerator = fr_per_min * setup_min
                batch = numerator / denominator

                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("Recommended Batch Size", f"{batch:.1f} units")
                c2.metric("Rounded Up", f"{math.ceil(batch)} units")

                # Verify: show the capacity at this batch size
                verify_cap = batch / (setup_min + batch * proc_min)
                st.info(
                    f"Verification — Capacity at batch size {batch:.1f}: "
                    f"**{verify_cap:.4f} units/min** ({verify_cap*60:.2f} units/hr)"
                )

    # --- Economic Order Quantity (EOQ) ---
    with tab_eoq:
        st.subheader("Economic Order Quantity (EOQ)")
        st.markdown(
            "**EOQ** finds the optimal order size that minimizes the total of ordering costs and "
            "inventory holding costs. Ordering more at once reduces ordering frequency (lower ordering costs) "
            "but increases average inventory (higher holding costs). EOQ balances these two trade-offs."
        )
        st.latex(r"Q^* = \sqrt{\frac{2 \times C_o \times D}{C_h}}")
        st.markdown(
            "Where: **Q*** = optimal order quantity, **C_o** = fixed cost per order, "
            "**D** = demand rate (units per period), **C_h** = holding cost per unit per period."
        )
        st.caption(
            "**C_h** (holding cost) typically includes storage cost + capital cost. "
            "Capital cost = unit price × cost of capital rate."
        )

        # Formula-style input — sqrt layout
        c_left, c_right = st.columns([1.5, 5])
        with c_left:
            st.markdown("")
            st.markdown("")
            st.markdown(
                '<div style="text-align:right; font-size:1.15em; font-weight:600; '
                'color:#333; padding-top:20px; line-height:1;">Q* &nbsp;= &nbsp;√</div>',
                unsafe_allow_html=True
            )
        with c_right:
            # Numerator: 2 × Co × D
            n_two, n_mul1, n_co, n_mul2, n_d = st.columns([0.4, 0.3, 2, 0.3, 2])
            with n_two:
                formula_text("2")
            with n_mul1:
                formula_op("×")
            with n_co:
                order_cost = st.number_input("Order Cost (Co)", value=85.0, key="eoq_co",
                                             help="Fixed cost per order (e.g., shipping, admin)")
            with n_mul2:
                formula_op("×")
            with n_d:
                demand_eoq = st.number_input("Demand Rate (D)", value=50.0, key="eoq_d",
                                             help="Demand in units per period")
                demand_period = st.selectbox("Period", ["Per Day", "Per Week", "Per Month", "Per Year"], index=2, key="eoq_d_period")
            # Fraction bar
            st.markdown(
                '<hr style="margin: 2px 0; border: none; border-top: 2px solid #555;">',
                unsafe_allow_html=True
            )
            # Denominator: Ch
            d_ch, d_pad = st.columns([3, 3])
            with d_ch:
                holding_cost = st.number_input("Holding Cost per unit per period (Ch)", value=1.5, key="eoq_ch",
                                               help="Inventory holding cost per unit per period (storage + capital cost)")

        if st.button("Calculate EOQ"):
            if order_cost <= 0 or demand_eoq <= 0 or holding_cost <= 0:
                st.error("All values (Co, D, Ch) must be greater than 0.")
            else:
                q_star = math.sqrt(2 * order_cost * demand_eoq / holding_cost)

                # Number of orders per period
                orders_per_period = demand_eoq / q_star

                # Average inventory
                avg_inventory = q_star / 2

                # Average inventory holding cost per period
                avg_holding_cost = holding_cost * avg_inventory

                # Average ordering cost per period
                avg_ordering_cost = order_cost * orders_per_period

                # Total cost per period (excluding purchase cost)
                total_cost = avg_holding_cost + avg_ordering_cost

                # Time between orders (in periods)
                time_between_orders = q_star / demand_eoq

                st.divider()
                st.markdown("### Optimal Order")
                c1, c2 = st.columns(2)
                c1.metric("Optimal Order Quantity (Q*)", f"{q_star:.1f} units")
                c2.metric("Rounded", f"{math.ceil(q_star)} units")

                st.divider()
                st.markdown("### Order Schedule")
                c1, c2, c3 = st.columns(3)
                period_label = demand_period.replace("Per ", "").lower()
                c1.metric(f"Orders / {period_label}", f"{orders_per_period:.2f}")
                c2.metric(f"Time Between Orders", f"{time_between_orders:.2f} {period_label}s")
                c3.metric("Avg Inventory", f"{avg_inventory:.1f} units")

                st.divider()
                st.markdown(f"### Costs (per {period_label})")
                c1, c2, c3 = st.columns(3)
                c1.metric("Inventory Holding Cost", f"${avg_holding_cost:.2f}")
                c2.metric("Ordering Cost", f"${avg_ordering_cost:.2f}")
                c3.metric("Total (Holding + Ordering)", f"${total_cost:.2f}")

                st.info(
                    f"At EOQ, holding cost (${avg_holding_cost:.2f}) ≈ ordering cost (${avg_ordering_cost:.2f}). "
                    f"This is a property of the EOQ formula — the two costs are equal at the optimum."
                )

# ==========================================
# WEEK 5: QUEUING & THROUGHPUT LOSS
# ==========================================
elif week_selection == "Week 5: Queuing Theory & Throughput Loss":
    st.header("Week 5: Queuing & Capacity")
    tab_queue, tab_inv_queue, tab_loss, tab_abandon = st.tabs(["Waiting Time (Queue)", "Inventory in Queue", "Throughput Loss (Erlang Loss)", "Adjusted Wait (Willingness to Wait)"])

    # --- Standard Queue (G/G/m) ---
    with tab_queue:
        st.subheader("Standard Queue (G/G/m)")
        st.markdown("**Waiting Time in Queue** estimates how long a customer waits before being served, using the G/G/m approximation. Use when customers **wait in line** (e.g., call centers, checkout lines).")
        st.latex(r"T_q = \frac{p}{m} \;\times\; \frac{u^{\sqrt{2(m+1)}-1}}{1-u} \;\times\; \frac{CV_a^2 + CV_p^2}{2}")
        st.markdown("""
Where: **p** = processing time, **m** = number of servers, **u** = utilization (*p / (a × m)*),
**a** = interarrival time, **CV_a** = coefficient of variation of arrivals, **CV_p** = coefficient of variation of processing.
""")

        # Formula-style input — Row 1: Utilization sub-formula
        st.markdown("**Utilization:**")
        u_lbl, u_eq, u_p, u_div, u_br1, u_a, u_mul, u_m, u_br2 = st.columns(
            [0.5, 0.3, 1.8, 0.3, 0.2, 1.8, 0.3, 1.2, 0.2]
        )
        with u_lbl:
            formula_label("u")
        with u_eq:
            formula_op("=")
        with u_p:
            p_val = st.number_input("Processing Time (p)", value=6.0)
            p_unit = st.selectbox("Unit (p)", ["Seconds", "Minutes", "Hours"], index=1, key="q_p")
        with u_div:
            formula_op("÷")
        with u_br1:
            formula_text("(")
        with u_a:
            a_val = st.number_input("Interarrival Time (a)", value=5.0)
            a_unit = st.selectbox("Unit (a)", ["Seconds", "Minutes", "Hours"], index=1, key="q_a")
        with u_mul:
            formula_op("×")
        with u_m:
            m = st.number_input("Servers (m)", min_value=1, value=2)
        with u_br2:
            formula_text(")")

        # Formula-style input — Row 2: Variability sub-formula
        st.markdown("**Variability:**")
        v_br1, v_cva, v_plus, v_cvp, v_br2, v_div, v_two = st.columns(
            [0.2, 2, 0.3, 2, 0.2, 0.3, 0.5]
        )
        with v_br1:
            formula_text("(")
        with v_cva:
            cv_a = st.number_input("CV of Arrivals (CVa)", value=1.0)
        with v_plus:
            formula_op("+")
        with v_cvp:
            cv_p = st.number_input("CV of Process (CVp)", value=0.5)
        with v_br2:
            formula_text(")")
        with v_div:
            formula_op("÷")
        with v_two:
            formula_text("2")

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

    # --- Inventory in Queue ---
    with tab_inv_queue:
        st.subheader("Inventory in the Queue")
        st.markdown(
            "**Inventory in the Queue** calculates the average number of flow units (customers, jobs) "
            "waiting in line and being served. Uses the G/G/m queuing model to derive waiting time, "
            "then applies Little's Law to convert to inventory measures."
        )
        st.latex(r"I_q = \frac{1}{a} \times T_q \qquad \text{(inventory waiting)}")
        st.latex(r"I_p = u \times m \qquad \text{(inventory in service)}")
        st.latex(r"I = I_q + I_p \qquad \text{(total inventory)}")
        st.markdown(
            "Where: **a** = interarrival time, **T_q** = waiting time in queue (from G/G/m formula), "
            "**u** = utilization, **m** = number of servers, **I_q** = avg units waiting, "
            "**I_p** = avg units being served, **I** = total avg units in system."
        )

        # Formula-style input — Row 1: Utilization sub-formula
        st.markdown("**Utilization:**")
        u_lbl, u_eq, u_p, u_div, u_br1, u_a, u_mul, u_m, u_br2 = st.columns(
            [0.5, 0.3, 1.8, 0.3, 0.2, 1.8, 0.3, 1.2, 0.2]
        )
        with u_lbl:
            formula_label("u")
        with u_eq:
            formula_op("=")
        with u_p:
            p_iq_val = st.number_input("Processing Time (p)", value=6.0, key="iq_p")
            p_iq_unit = st.selectbox("Unit (p)", ["Seconds", "Minutes", "Hours"], index=1, key="iq_p_unit")
        with u_div:
            formula_op("÷")
        with u_br1:
            formula_text("(")
        with u_a:
            a_iq_val = st.number_input("Interarrival Time (a)", value=5.0, key="iq_a")
            a_iq_unit = st.selectbox("Unit (a)", ["Seconds", "Minutes", "Hours"], index=1, key="iq_a_unit")
        with u_mul:
            formula_op("×")
        with u_m:
            m_iq = st.number_input("Servers (m)", min_value=1, value=2, key="iq_m")
        with u_br2:
            formula_text(")")

        # Formula-style input — Row 2: Variability sub-formula
        st.markdown("**Variability:**")
        v_br1, v_cva, v_plus, v_cvp, v_br2, v_div, v_two = st.columns(
            [0.2, 2, 0.3, 2, 0.2, 0.3, 0.5]
        )
        with v_br1:
            formula_text("(")
        with v_cva:
            cv_a_iq = st.number_input("CV of Arrivals (CVa)", value=1.0, key="iq_cva")
        with v_plus:
            formula_op("+")
        with v_cvp:
            cv_p_iq = st.number_input("CV of Process (CVp)", value=0.5, key="iq_cvp")
        with v_br2:
            formula_text(")")
        with v_div:
            formula_op("÷")
        with v_two:
            formula_text("2")

        # Normalize to Minutes
        a_iq_min = to_minutes(a_iq_val, a_iq_unit)
        p_iq_min = to_minutes(p_iq_val, p_iq_unit)

        if st.button("Calculate Inventory in Queue"):
            if a_iq_min > 0 and m_iq > 0:
                util_iq = p_iq_min / (a_iq_min * m_iq)
                st.metric("Utilization", f"{util_iq:.2%}")

                if util_iq >= 1.0:
                    st.error(
                        "System Unstable (u >= 100%) — queue grows without bound, "
                        "inventory approaches infinity."
                    )
                elif util_iq > 0:
                    # Calculate Tq using G/G/m formula
                    term1 = p_iq_min / m_iq
                    exponent = math.sqrt(2 * (m_iq + 1)) - 1
                    term2 = (util_iq ** exponent) / (1 - util_iq)
                    term3 = (cv_a_iq**2 + cv_p_iq**2) / 2
                    tq_iq = term1 * term2 * term3

                    # Inventory measures
                    flow_rate = 1 / a_iq_min  # units per minute
                    iq = flow_rate * tq_iq     # inventory waiting in queue
                    ip = util_iq * m_iq        # inventory in service
                    i_total = iq + ip          # total inventory

                    # Flow time
                    t_total = tq_iq + p_iq_min

                    st.divider()
                    st.markdown("### Time Measures")
                    c1, c2 = st.columns(2)
                    c1.metric("Waiting Time (Tq)", f"{tq_iq:.2f} min")
                    c2.metric("Flow Time (T = Tq + p)", f"{t_total:.2f} min")

                    st.divider()
                    st.markdown("### Inventory Measures")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Inventory in Queue (Iq)", f"{iq:.2f} units",
                              help="Avg number of units waiting to be served")
                    c2.metric("Inventory in Service (Ip)", f"{ip:.2f} units",
                              help="Avg number of units currently being served")
                    c3.metric("Total Inventory (I)", f"{i_total:.2f} units",
                              help="Total avg units in the system (waiting + in service)")
                else:
                    st.info("No demand — all inventory measures are 0.")
            else:
                st.error("Interarrival time and number of servers must be greater than 0.")

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

        # Formula-style input: r = λ × p  with m servers
        st.markdown("**Traffic Intensity:**")
        r_lbl, r_eq, r_lam, r_mul, r_p, r_with, r_m = st.columns(
            [0.5, 0.3, 2, 0.3, 2, 0.5, 1.5]
        )
        with r_lbl:
            formula_label("r")
        with r_eq:
            formula_op("=")
        with r_lam:
            if input_method == "Interarrival Time (a)":
                val_a = st.number_input("Avg Interarrival Time", value=3.0)
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
        with r_mul:
            formula_op("×")
        with r_p:
            proc_time = st.number_input("Avg Processing Time (p)", value=2.0)
            proc_unit = st.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=1, key="loss_p")
            # Calculate P (in hours)
            p_hours = to_minutes(proc_time, proc_unit) / 60
        with r_with:
            formula_text("with")
        with r_m:
            m_loss = st.number_input("Servers (m)", value=3, min_value=1, key="loss_m")

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

        # Formula-style input — Row 1: Utilization sub-formula
        st.markdown("**Utilization:**")
        u_lbl, u_eq, u_p, u_div, u_br1, u_a, u_mul, u_m, u_br2 = st.columns(
            [0.5, 0.3, 1.8, 0.3, 0.2, 1.8, 0.3, 1.2, 0.2]
        )
        with u_lbl:
            formula_label("u")
        with u_eq:
            formula_op("=")
        with u_p:
            p_adj_val = st.number_input("Processing Time (p)", value=6.0, key="adj_p")
            p_adj_unit = st.selectbox("Unit (p)", ["Seconds", "Minutes", "Hours"], index=1, key="adj_p_unit")
        with u_div:
            formula_op("÷")
        with u_br1:
            formula_text("(")
        with u_a:
            a_adj_val = st.number_input("Interarrival Time (a)", value=5.0, key="adj_a")
            a_adj_unit = st.selectbox("Unit (a)", ["Seconds", "Minutes", "Hours"], index=1, key="adj_a_unit")
        with u_mul:
            formula_op("×")
        with u_m:
            m_adj = st.number_input("Servers (m)", min_value=1, value=2, key="adj_m")
        with u_br2:
            formula_text(")")

        # Formula-style input — Row 2: Variability sub-formula
        st.markdown("**Variability:**")
        v_br1, v_cva, v_plus, v_cvp, v_br2, v_div, v_two = st.columns(
            [0.2, 2, 0.3, 2, 0.2, 0.3, 0.5]
        )
        with v_br1:
            formula_text("(")
        with v_cva:
            cv_a_adj = st.number_input("CV of Arrivals (CVa)", value=1.0, key="adj_cva")
        with v_plus:
            formula_op("+")
        with v_cvp:
            cv_p_adj = st.number_input("CV of Process (CVp)", value=0.5, key="adj_cvp")
        with v_br2:
            formula_text(")")
        with v_div:
            formula_op("÷")
        with v_two:
            formula_text("2")

        # Formula-style input — Row 3: Willingness to Wait
        st.markdown("**Patience:**")
        w_lbl, w_eq, w_inp, _, _ = st.columns([0.5, 0.3, 2, 2, 2])
        with w_lbl:
            formula_label("W")
        with w_eq:
            formula_op("=")
        with w_inp:
            w_val = st.number_input("Willingness to Wait (W)", value=5.0, min_value=0.01, key="adj_w")
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
    tab_cap, tab_ucl, tab_takt, tab_lost = st.tabs(["Process Capability (k-sigma)", "Control Limits (UCL/LCL)", "Takt Time", "Customer Lost Rate"])

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

        # Formula-style input — two sub-formulas for k
        # Row 1: ( USL - μ ) ÷ σ
        st.markdown("**Upper distance:**")
        k1_br1, k1_usl, k1_minus, k1_mu, k1_br2, k1_div, k1_sig = st.columns(
            [0.2, 1.8, 0.3, 1.8, 0.2, 0.3, 1.5]
        )
        with k1_br1:
            formula_text("(")
        with k1_usl:
            usl = st.number_input("Upper Spec Limit (USL)", value=56.0, key="cap_usl")
        with k1_minus:
            formula_op("−")
        with k1_mu:
            mean_val = st.number_input("Process Mean (μ)", value=50.0, key="cap_mean")
        with k1_br2:
            formula_text(")")
        with k1_div:
            formula_op("÷")
        with k1_sig:
            sigma_val = st.number_input("Std Deviation (σ)", value=2.0, min_value=0.001, key="cap_sigma")

        # Row 2: ( μ - LSL ) ÷ σ
        st.markdown("**Lower distance:**")
        k2_br1, k2_mu, k2_minus, k2_lsl, k2_br2, k2_div, k2_sig = st.columns(
            [0.2, 1.8, 0.3, 1.8, 0.2, 0.3, 1.5]
        )
        with k2_br1:
            formula_text("(")
        with k2_mu:
            formula_text("μ")
        with k2_minus:
            formula_op("−")
        with k2_lsl:
            lsl = st.number_input("Lower Spec Limit (LSL)", value=44.0, key="cap_lsl")
        with k2_br2:
            formula_text(")")
        with k2_div:
            formula_op("÷")
        with k2_sig:
            formula_text("σ")

        st.markdown("*k = min of the two distances above*")

        if st.button("Calculate Process Capability"):
            if sigma_val > 0 and usl > lsl:
                # Process Capability = P(LSL < X < USL)
                capability = norm_cdf(usl, mean_val, sigma_val) - norm_cdf(lsl, mean_val, sigma_val)
                defect_rate = 1 - capability

                st.divider()
                st.markdown("### Process Capability")
                st.latex(r"\text{Capability} = \Phi\!\left(\frac{\text{USL} - \mu}{\sigma}\right) - \Phi\!\left(\frac{\text{LSL} - \mu}{\sigma}\right)")
                c1, c2 = st.columns(2)
                c1.metric("Process Capability", f"{capability:.3%}")
                c2.metric("Defect Rate", f"{defect_rate:.3%}")

                # k-sigma
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

    # --- Control Limits (UCL / LCL) ---
    with tab_ucl:
        st.subheader("Control Limits (UCL / LCL)")
        st.markdown(
            "**Statistical Process Control** monitors whether a process is behaving as expected. "
            "We take samples of size *n* and plot the **sample average**. "
            "If a sample average falls outside the control limits, the process may be **out of control**."
        )
        st.latex(r"\text{UCL} = \mu + 3 \times \frac{\sigma}{\sqrt{n}}")
        st.latex(r"\text{LCL} = \mu - 3 \times \frac{\sigma}{\sqrt{n}}")
        st.markdown(
            "Where: **μ** = process mean, **σ** = process standard deviation, "
            "**n** = sample size (number of units measured per sample)."
        )
        st.markdown(
            "**Important:** Control limits (UCL/LCL) determine whether the *process* is in control. "
            "They are different from specification limits (USL/LSL), which determine whether *individual units* meet requirements."
        )

        # Formula-style input: UCL/LCL = μ ± 3 × σ ÷ √n
        c_lbl, c_eq, c_mu, c_pm, c_three, c_mul, c_sig, c_div, c_sqn = st.columns(
            [1.2, 0.3, 1.5, 0.3, 0.4, 0.3, 1.5, 0.3, 1.5]
        )
        with c_lbl:
            formula_label("UCL / LCL")
        with c_eq:
            formula_op("=")
        with c_mu:
            mean_cl = st.number_input("Process Mean (μ)", value=51.15, key="cl_mean")
        with c_pm:
            formula_op("±")
        with c_three:
            formula_text("3")
        with c_mul:
            formula_op("×")
        with c_sig:
            sigma_cl = st.number_input("Std Deviation (σ)", value=2.604, min_value=0.001, key="cl_sigma")
        with c_div:
            formula_op("÷")
        with c_sqn:
            n_cl = st.number_input("√ Sample Size (n)", value=5, min_value=1, key="cl_n")

        if st.button("Calculate Control Limits"):
            if sigma_cl > 0 and n_cl > 0:
                ucl = mean_cl + 3 * sigma_cl / math.sqrt(n_cl)
                lcl = mean_cl - 3 * sigma_cl / math.sqrt(n_cl)

                st.divider()
                c1, c2, c3 = st.columns(3)
                c1.metric("UCL", f"{ucl:.4f}")
                c2.metric("Mean (μ)", f"{mean_cl:.4f}")
                c3.metric("LCL", f"{lcl:.4f}")

                st.info(
                    f"A sample average between **{lcl:.4f}** and **{ucl:.4f}** indicates the process is **in control**. "
                    f"If any sample average falls outside this range, investigate the process for assignable causes."
                )

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

        # Formula-style input: Takt = Available Time ÷ Demand
        c_lbl, c_eq, c_time, c_div, c_dem = st.columns([1.5, 0.3, 2, 0.3, 2])
        with c_lbl:
            formula_label("Takt Time")
        with c_eq:
            formula_op("=")
        with c_time:
            avail_time = st.number_input("Available Production Time", value=480.0, key="takt_time")
            time_unit_takt = st.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=0, key="takt_time_unit")
        with c_div:
            formula_op("÷")
        with c_dem:
            demand_takt = st.number_input("Customer Demand (units)", value=240.0, min_value=0.01, key="takt_demand")

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

        # Formula-style input: Output = Demand × (1 - P_loss)
        st.markdown("**Output Flow Rate:**")
        o_lbl, o_eq, o_dem, o_mul, o_br1, o_one, o_minus, o_pl, o_br2 = st.columns(
            [1.2, 0.3, 2, 0.3, 0.2, 0.4, 0.3, 1.5, 0.2]
        )
        with o_lbl:
            formula_label("Output")
        with o_eq:
            formula_op("=")
        with o_dem:
            demand_rate_lr = st.number_input("Demand Rate", value=10.0, key="lr_demand")
            demand_unit_lr = st.selectbox("Rate Unit", ["Per Minute", "Per Hour", "Per Day"], index=1, key="lr_demand_unit")
        with o_mul:
            formula_op("×")
        with o_br1:
            formula_text("(")
        with o_one:
            formula_text("1")
        with o_minus:
            formula_op("−")
        with o_pl:
            p_loss_input = st.number_input("P_loss", value=0.05, min_value=0.0, max_value=1.0, step=0.01, key="lr_ploss")
        with o_br2:
            formula_text(")")

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

# ==========================================
# WEEK 7: MANISH & ADELE WEDDING
# ==========================================
elif week_selection == "Week 7: Manish & Adele Wedding":
    st.header("Week 7: Manish & Adele Wedding \U0001f492")
    st.markdown("Apply **Operations Management** principles to plan the perfect wedding. Use the tabs below to manage guests, catering, budget, and the reception queue.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Guest & Seating Planner",
        "Catering Estimator",
        "Budget Breakdown",
        "Reception Queue (Little's Law)"
    ])

    # --------------------------------------------------
    # TAB 1: Guest & Seating Planner
    # --------------------------------------------------
    with tab1:
        st.subheader("Guest & Seating Planner")
        st.markdown("Calculate expected attendance, tables required, and venue utilisation.")

        col1, col2 = st.columns(2)
        with col1:
            total_invited = st.number_input("Total Guests Invited", min_value=1, value=150, step=1, key="w7_invited")
            rsvp_rate = st.number_input("Expected RSVP / Attendance Rate (%)", min_value=0.0, max_value=100.0, value=80.0, step=0.5, key="w7_rsvp")
        with col2:
            seats_per_table = st.number_input("Seats per Table", min_value=1, value=10, step=1, key="w7_seats")
            venue_capacity = st.number_input("Venue Capacity (max guests)", min_value=1, value=130, step=1, key="w7_venue")

        if st.button("Calculate Seating", key="w7_seat_btn"):
            expected_guests = round(total_invited * (rsvp_rate / 100))
            tables_needed = math.ceil(expected_guests / seats_per_table)
            utilisation = expected_guests / venue_capacity if venue_capacity > 0 else 0

            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Expected Guests", f"{expected_guests}")
            c2.metric("Tables Needed", f"{tables_needed}")
            c3.metric("Seats Available", f"{tables_needed * seats_per_table}")
            c4.metric("Venue Utilisation", f"{utilisation:.1%}")

            empty_seats = tables_needed * seats_per_table - expected_guests
            st.caption(f"Empty seats per arrangement: **{empty_seats}**")

            if utilisation > 1.0:
                st.error(f"Venue capacity exceeded! ({expected_guests} guests vs {venue_capacity} capacity). Consider a larger venue or reduce the guest list.")
            elif utilisation > 0.90:
                st.warning(f"Venue is at {utilisation:.0%} utilisation — very tight. Have a contingency plan ready.")
            else:
                st.success(f"Venue utilisation is {utilisation:.0%} — comfortable fit for the celebration!")

    # --------------------------------------------------
    # TAB 2: Catering Estimator
    # --------------------------------------------------
    with tab2:
        st.subheader("Catering Estimator")
        st.markdown("Estimate food, drinks, and catering cost for the wedding reception.")

        col1, col2 = st.columns(2)
        with col1:
            num_guests_cat = st.number_input("Number of Guests", min_value=1, value=120, step=1, key="w7_cat_guests")
            cost_per_head = st.number_input("Meal Cost per Guest ($)", min_value=0.0, value=85.0, step=5.0, key="w7_cost_head")
            reception_hours = st.number_input("Reception Duration (hours)", min_value=0.5, value=5.0, step=0.5, key="w7_rec_hours")
        with col2:
            drinks_per_hour = st.number_input("Drinks per Guest per Hour", min_value=0.0, value=2.0, step=0.5, key="w7_drinks_hr")
            cost_per_drink = st.number_input("Cost per Drink ($)", min_value=0.0, value=8.0, step=0.5, key="w7_drink_cost")
            cake_cost = st.number_input("Wedding Cake Cost ($)", min_value=0.0, value=600.0, step=50.0, key="w7_cake")

        if st.button("Estimate Catering Cost", key="w7_cat_btn"):
            total_drinks = num_guests_cat * drinks_per_hour * reception_hours
            food_cost = num_guests_cat * cost_per_head
            drinks_cost = total_drinks * cost_per_drink
            total_catering = food_cost + drinks_cost + cake_cost

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Food Cost", f"${food_cost:,.2f}")
            c2.metric("Total Drinks Cost", f"${drinks_cost:,.2f}")
            c3.metric("Wedding Cake", f"${cake_cost:,.2f}")

            st.divider()
            st.metric("Total Catering Cost", f"${total_catering:,.2f}", delta=f"${total_catering/num_guests_cat:.2f} per guest")

            import pandas as pd
            breakdown_df = pd.DataFrame({
                "Category": ["Food (meals)", "Drinks", "Wedding Cake", "Total"],
                "Cost ($)": [f"${food_cost:,.2f}", f"${drinks_cost:,.2f}", f"${cake_cost:,.2f}", f"${total_catering:,.2f}"],
                "% of Catering": [
                    f"{food_cost/total_catering:.1%}" if total_catering > 0 else "—",
                    f"{drinks_cost/total_catering:.1%}" if total_catering > 0 else "—",
                    f"{cake_cost/total_catering:.1%}" if total_catering > 0 else "—",
                    "100%"
                ]
            })
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    # --------------------------------------------------
    # TAB 3: Budget Breakdown
    # --------------------------------------------------
    with tab3:
        st.subheader("Wedding Budget Breakdown")
        st.markdown("Allocate your total budget across key wedding categories and check against actuals.")

        total_budget = st.number_input("Total Wedding Budget ($)", min_value=0.0, value=30000.0, step=500.0, key="w7_budget")

        st.markdown("#### Budget Allocations")
        col1, col2 = st.columns(2)
        with col1:
            venue_pct    = st.slider("Venue (%)",               0, 100, 30, key="w7_b_venue")
            catering_pct = st.slider("Catering (%)",            0, 100, 35, key="w7_b_cat")
            photo_pct    = st.slider("Photography/Video (%)",   0, 100, 12, key="w7_b_photo")
            flowers_pct  = st.slider("Flowers & Decor (%)",     0, 100, 8,  key="w7_b_flowers")
        with col2:
            music_pct    = st.slider("Music/Entertainment (%)", 0, 100, 5,  key="w7_b_music")
            attire_pct   = st.slider("Attire & Styling (%)",    0, 100, 5,  key="w7_b_attire")
            transport_pct= st.slider("Transport (%)",           0, 100, 2,  key="w7_b_trans")
            misc_pct     = st.slider("Miscellaneous (%)",       0, 100, 3,  key="w7_b_misc")

        if st.button("Calculate Budget Allocation", key="w7_budget_btn"):
            total_pct = venue_pct + catering_pct + photo_pct + flowers_pct + music_pct + attire_pct + transport_pct + misc_pct

            categories = ["Venue", "Catering", "Photography/Video", "Flowers & Decor",
                          "Music/Entertainment", "Attire & Styling", "Transport", "Miscellaneous"]
            percentages = [venue_pct, catering_pct, photo_pct, flowers_pct,
                           music_pct, attire_pct, transport_pct, misc_pct]
            amounts = [total_budget * p / 100 for p in percentages]

            import pandas as pd
            df = pd.DataFrame({
                "Category": categories,
                "Allocation (%)": [f"{p}%" for p in percentages],
                "Budget Amount ($)": [f"${a:,.2f}" for a in amounts]
            })

            st.divider()
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Budget", f"${total_budget:,.2f}")
            c2.metric("Total Allocated", f"${total_budget * total_pct / 100:,.2f}")
            c3.metric("Allocations Sum", f"{total_pct}%")

            if total_pct > 100:
                st.error(f"Allocations sum to {total_pct}% — over budget by {total_pct - 100}%. Reduce some categories.")
            elif total_pct < 100:
                leftover = total_budget * (100 - total_pct) / 100
                st.warning(f"Allocations sum to {total_pct}% — ${leftover:,.2f} unallocated. Consider adding to Miscellaneous or savings buffer.")
            else:
                st.success("Allocations sum to exactly 100% — perfect budget balance!")

    # --------------------------------------------------
    # TAB 4: Reception Queue — Little's Law
    # --------------------------------------------------
    with tab4:
        st.subheader("Reception Queue — Little's Law")
        st.markdown(
            "Apply **Little's Law** (L = \u03bbW) to the wedding receiving line. "
            "Find out how long guests wait to greet the couple and how many are in the queue at any time."
        )

        col1, col2 = st.columns(2)
        with col1:
            arrival_rate_rl = st.number_input("Guest Arrival Rate (guests / minute)", min_value=0.1, value=3.0, step=0.1, key="w7_rl_arr")
            service_time_rl = st.number_input("Average Greeting Time per Guest (minutes)", min_value=0.1, value=1.5, step=0.1, key="w7_rl_svc")
        with col2:
            num_greeters   = st.number_input("Number of Greeters (servers)", min_value=1, value=2, step=1, key="w7_rl_greet")
            total_arriving = st.number_input("Total Guests Expected in Receiving Line", min_value=1, value=100, step=1, key="w7_rl_total")

        if st.button("Analyse Receiving Line", key="w7_rl_btn"):
            # Throughput (capacity of receiving line)
            capacity = num_greeters / service_time_rl  # guests per minute

            # Utilisation
            utilisation_rl = arrival_rate_rl / capacity

            if utilisation_rl >= 1.0:
                st.error(
                    f"Utilisation is {utilisation_rl:.1%} — the receiving line cannot keep up with arrivals! "
                    f"Add more greeters or shorten greetings."
                )
            else:
                # M/M/c approximation for average number in system using simple single-server proxy
                # For simplicity: use Kingman-style approximation with rho
                rho = utilisation_rl

                # Average wait in queue (M/M/1 approximation scaled)
                Wq = (rho * service_time_rl) / (num_greeters * (1 - rho))
                # Average time in system
                W = Wq + service_time_rl
                # Average guests in system (Little's Law: L = lambda * W)
                L = arrival_rate_rl * W
                # Average guests in queue
                Lq = arrival_rate_rl * Wq
                # Time to clear all guests through
                time_to_clear = total_arriving / capacity

                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("Receiving Line Utilisation", f"{utilisation_rl:.1%}")
                c2.metric("Line Capacity", f"{capacity:.2f} guests/min")

                st.divider()
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Avg Guests in System (L)", f"{L:.1f}")
                c2.metric("Avg Guests in Queue (Lq)", f"{Lq:.1f}")
                c3.metric("Avg Wait in Queue (Wq)", f"{Wq:.2f} min")
                c4.metric("Avg Time in System (W)", f"{W:.2f} min")

                st.divider()
                st.metric("Estimated Time to Clear All Guests", f"{time_to_clear:.1f} minutes ({time_to_clear/60:.2f} hrs)")

                if utilisation_rl > 0.80:
                    st.warning(f"High utilisation ({utilisation_rl:.0%}). Queue could grow long during peak arrivals. Consider more greeters.")
                else:
                    st.success(f"Receiving line is well-managed at {utilisation_rl:.0%} utilisation. Guests should flow smoothly!")
