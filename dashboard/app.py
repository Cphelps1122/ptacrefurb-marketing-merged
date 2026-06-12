import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="PTAC Refurb Marketing OS",
    page_icon="📊",
    layout="wide"
)

RED = "#9C0100"
DARK = "#343434"
GRAY = "#666666"

SHEET_NAMES = {
    "calendar": "Content Calendar",
    "dashboard": "Executive Dashboard",
    "kpi": "Weekly KPI Tracker",
    "leads": "Lead CRM",
    "pipeline": "Opportunity Pipeline",
    "library": "Content Library",
    "engagement": "Engagement Tracker",
    "website": "Website Roadmap",
    "revenue": "Revenue Attribution",
}

EXPECTED_COLUMNS = {
    "Content Calendar": ["Date", "Time", "Platform", "Topic", "Bucket", "Graphic Status", "Caption Status", "Approval Status", "Posted", "Caption", "Notes"],
    "Content Library": ["Topic", "Bucket", "Hook", "Caption", "Graphic Concept", "Status", "Notes"],
    "Engagement Tracker": ["Date", "Company/Page", "Post Topic", "Comment", "Engagement Type", "Follow Up Needed", "Notes"],
    "Weekly KPI Tracker": ["Week", "LinkedIn Followers", "Facebook Followers", "Website Visitors", "Content Impressions", "Content Clicks", "New Leads", "Quote Requests", "Notes"],
    "Lead CRM": ["Date", "Company", "Contact Name", "Role", "Source", "Status", "Estimated Value", "Notes"],
    "Opportunity Pipeline": ["Date", "Company", "Stage", "Pipeline Value", "Next Step", "Target Date", "Notes"],
    "Website Roadmap": ["Task", "Priority", "Status", "Target Date", "Notes"],
    "Revenue Attribution": ["Date", "Company", "Source", "Closed Revenue", "Notes"],
}


def css():
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-top: 1rem;
            max-width: 1600px;
        }}
        .hero {{
            background: linear-gradient(135deg, #fff 0%, #fff 68%, {DARK} 68%, {RED} 100%);
            border: 1px solid #ddd;
            border-radius: 18px;
            padding: 22px 28px;
            margin-bottom: 18px;
            box-shadow: 0 2px 10px rgba(0,0,0,.05);
        }}
        .hero h1 {{
            margin: 0;
            color: {DARK};
            font-size: 40px;
            font-weight: 900;
            letter-spacing: -1px;
        }}
        .hero p {{
            margin: 4px 0 0;
            color: {RED};
            font-weight: 800;
            letter-spacing: .6px;
        }}
        .section-title {{
            background: linear-gradient(90deg,{RED},{DARK});
            color: white;
            padding: 8px 12px;
            border-radius: 10px;
            font-weight: 800;
            margin: 16px 0 10px;
        }}
        div[data-testid="stMetric"] {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,.04);
        }}
        .post-card {{
            border: 1px solid #ddd;
            border-radius: 16px;
            padding: 16px;
            background: #fff;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,.04);
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 10px;
            background: #f3f3f3;
            border: 1px solid #ddd;
            font-size: 12px;
            font-weight: 700;
            margin-right: 4px;
        }}
        .approved {{ background: #dcfce7; border-color: #86efac; }}
        .needs {{ background: #fee2e2; border-color: #fecaca; }}
        .planned {{ background: #e0f2fe; border-color: #bae6fd; }}
        .ready {{ background: #fef9c3; border-color: #fde68a; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def header():
    st.markdown(
        """
        <div class='hero'>
            <h1>PTAC Refurb Marketing OS</h1>
            <p>90-Day Content Calendar • Approvals • Engagement • Leads • Pipeline</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=60, show_spinner=False)
def read_sheet(sheet_name):
    sheet_id = st.secrets.get("GOOGLE_SHEET_ID", "")

    if not sheet_id:
        st.error("Missing GOOGLE_SHEET_ID in Streamlit secrets.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS.get(sheet_name, []))

    try:
        url = (
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?"
            f"tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
        )

        df = pd.read_csv(url)

        for col in EXPECTED_COLUMNS.get(sheet_name, []):
            if col not in df.columns:
                df[col] = ""

        return df

    except Exception as e:
        st.error(f"Could not read {sheet_name}: {e}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS.get(sheet_name, []))


def to_num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def parse_dates(df):
    if df.empty or "Date" not in df.columns:
        return df

    out = df.copy()
    out["_date"] = pd.to_datetime(out["Date"], errors="coerce").dt.date
    return out


def badge(text):
    value = str(text).lower()
    cls = "badge"

    if any(x in value for x in ["approved", "done", "yes", "posted", "complete"]):
        cls += " approved"
    elif any(x in value for x in ["needed", "needs", "not started", "missing", "no"]):
        cls += " needs"
    elif any(x in value for x in ["planned", "draft", "scheduled"]):
        cls += " planned"
    elif "ready" in value:
        cls += " ready"

    return f"<span class='{cls}'>{text or '—'}</span>"


def show_post_card(row):
    st.markdown(
        f"""
        <div class='post-card'>
            <h3 style='margin:0;color:{DARK};'>{row.get("Topic", "")}</h3>
            <p style='margin:4px 0 10px;color:{GRAY};'>
                <b>{row.get("Date", "")}</b> • {row.get("Time", "")} • {row.get("Platform", "")} • {row.get("Bucket", "")}
            </p>
            <div>
                {badge("Graphic: " + str(row.get("Graphic Status", "")))}
                {badge("Caption: " + str(row.get("Caption Status", "")))}
                {badge("Approval: " + str(row.get("Approval Status", "")))}
                {badge("Posted: " + str(row.get("Posted", "")))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if row.get("Caption", ""):
        with st.expander("View caption"):
            st.write(row.get("Caption", ""))


def page_executive():
    header()

    cal = read_sheet(SHEET_NAMES["calendar"])
    kpi = read_sheet(SHEET_NAMES["kpi"])
    leads = read_sheet(SHEET_NAMES["leads"])
    pipe = read_sheet(SHEET_NAMES["pipeline"])
    eng = read_sheet(SHEET_NAMES["engagement"])

    latest = kpi.tail(1) if not kpi.empty else pd.DataFrame()

    followers = (
        int(to_num(latest["LinkedIn Followers"]).iloc[0])
        if not latest.empty and "LinkedIn Followers" in latest.columns
        else 0
    )

    impressions = (
        int(to_num(latest["Content Impressions"]).iloc[0])
        if not latest.empty and "Content Impressions" in latest.columns
        else 0
    )

    pipeline_value = (
        to_num(pipe["Pipeline Value"]).sum()
        if not pipe.empty and "Pipeline Value" in pipe.columns
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("LinkedIn Followers", followers)
    c2.metric("Content Impressions", impressions)
    c3.metric("Tracked Leads", len(leads))
    c4.metric("Pipeline Value", f"${pipeline_value:,.0f}")

    st.markdown("<div class='section-title'>This Week's Posting Plan</div>", unsafe_allow_html=True)

    dated = parse_dates(cal)
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    if "_date" in dated.columns:
        week = dated[(dated["_date"] >= start) & (dated["_date"] <= end)].sort_values(
            ["_date", "Time"], na_position="last"
        )
    else:
        week = dated.head(10)

    if week.empty:
        st.info("No posts scheduled for this week yet.")
    else:
        for _, row in week.iterrows():
            show_post_card(row)

    st.markdown("<div class='section-title'>Action Center</div>", unsafe_allow_html=True)

    a, b, c = st.columns(3)

    graphics_needed = (
        len(
            cal[
                cal.get("Graphic Status", pd.Series(dtype=str))
                .astype(str)
                .str.lower()
                .isin(["needed", "needs graphic", "not started", ""])
            ]
        )
        if not cal.empty
        else 0
    )

    approvals_needed = (
        len(
            cal[
                cal.get("Approval Status", pd.Series(dtype=str))
                .astype(str)
                .str.lower()
                .isin(["needed", "pending", "needs approval", "not approved", ""])
            ]
        )
        if not cal.empty
        else 0
    )

    a.metric("Graphics Needed", graphics_needed)
    b.metric("Approvals Needed", approvals_needed)
    c.metric("Engagement Actions Logged", len(eng) if not eng.empty else 0)


def page_calendar():
    header()
    st.markdown("<div class='section-title'>90-Day Content Calendar</div>", unsafe_allow_html=True)

    df = parse_dates(read_sheet(SHEET_NAMES["calendar"]))

    cols = [
        "Date",
        "Time",
        "Platform",
        "Topic",
        "Bucket",
        "Graphic Status",
        "Caption Status",
        "Approval Status",
        "Posted",
    ]

    st.dataframe(
        df[[c for c in cols if c in df.columns]],
        use_container_width=True,
        hide_index=True,
    )


def page_library():
    header()
    st.markdown("<div class='section-title'>Content Library</div>", unsafe_allow_html=True)
    st.dataframe(read_sheet(SHEET_NAMES["library"]), use_container_width=True, hide_index=True)


def page_engagement():
    header()
    st.markdown("<div class='section-title'>Engagement Tracker</div>", unsafe_allow_html=True)
    st.dataframe(read_sheet(SHEET_NAMES["engagement"]), use_container_width=True, hide_index=True)


def page_leads():
    header()
    st.markdown("<div class='section-title'>Lead CRM</div>", unsafe_allow_html=True)
    st.dataframe(read_sheet(SHEET_NAMES["leads"]), use_container_width=True, hide_index=True)


def page_data(key, title):
    header()
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    st.dataframe(read_sheet(SHEET_NAMES[key]), use_container_width=True, hide_index=True)


def page_setup():
    header()
    st.markdown("<div class='section-title'>Setup Check</div>", unsafe_allow_html=True)

    if st.secrets.get("GOOGLE_SHEET_ID", ""):
        st.success("GOOGLE_SHEET_ID is set.")
        st.code(st.secrets.get("GOOGLE_SHEET_ID", ""))
    else:
        st.error("GOOGLE_SHEET_ID is missing.")

    st.markdown("Expected Google Sheet tabs:")
    st.code("\n".join(SHEET_NAMES.values()))


def main():
    css()

    pages = {
        "Executive Dashboard": page_executive,
        "Content Calendar": page_calendar,
        "Content Library": page_library,
        "Engagement Tracker": page_engagement,
        "Lead CRM": page_leads,
        "Weekly KPI Tracker": lambda: page_data("kpi", "Weekly KPI Tracker"),
        "Opportunity Pipeline": lambda: page_data("pipeline", "Opportunity Pipeline"),
        "Website Roadmap": lambda: page_data("website", "Website Roadmap"),
        "Revenue Attribution": lambda: page_data("revenue", "Revenue Attribution"),
        "Setup Check": page_setup,
    }

    with st.sidebar:
        st.markdown("## PTAC Refurb")
        page = st.radio("Navigation", list(pages.keys()))
        st.markdown("---")

        if st.secrets.get("GOOGLE_SHEET_ID", ""):
            st.success("Connected to Google Sheet")
        else:
            st.warning("Add GOOGLE_SHEET_ID secret")

    pages[page]()


if __name__ == "__main__":
    main()
