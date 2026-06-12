
import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta
st.write("Secrets loaded:", list(st.secrets.keys()))

st.set_page_config(page_title="PTAC Refurb Marketing OS", page_icon="📊", layout="wide")
RED="#9C0100"; DARK="#343434"; GRAY="#666666"
SHEET_NAMES={"calendar":"Content Calendar","dashboard":"Executive Dashboard","kpi":"Weekly KPI Tracker","leads":"Lead CRM","pipeline":"Opportunity Pipeline","library":"Content Library","engagement":"Engagement Tracker","website":"Website Roadmap","revenue":"Revenue Attribution"}
EXPECTED_COLUMNS={
"Content Calendar":["Date","Time","Platform","Topic","Bucket","Graphic Status","Caption Status","Approval Status","Posted","Caption","Notes"],
"Content Library":["Topic","Bucket","Hook","Caption","Graphic Concept","Status","Notes"],
"Engagement Tracker":["Date","Company/Page","Post Topic","Comment","Engagement Type","Follow Up Needed","Notes"],
"Weekly KPI Tracker":["Week","LinkedIn Followers","Facebook Followers","Website Visitors","Content Impressions","Content Clicks","New Leads","Quote Requests","Notes"],
"Lead CRM":["Date","Company","Contact Name","Role","Source","Status","Estimated Value","Notes"],
"Opportunity Pipeline":["Date","Company","Stage","Pipeline Value","Next Step","Target Date","Notes"],
"Website Roadmap":["Task","Priority","Status","Target Date","Notes"],
"Revenue Attribution":["Date","Company","Source","Closed Revenue","Notes"]}

def css():
    st.markdown(f"""
    <style>.block-container{{padding-top:1rem;max-width:1600px}}.hero{{background:linear-gradient(135deg,#fff 0%,#fff 68%,{DARK} 68%,{RED} 100%);border:1px solid #ddd;border-radius:18px;padding:22px 28px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.05)}}.hero h1{{margin:0;color:{DARK};font-size:40px;font-weight:900;letter-spacing:-1px}}.hero p{{margin:4px 0 0;color:{RED};font-weight:800;letter-spacing:.6px}}.section-title{{background:linear-gradient(90deg,{RED},{DARK});color:white;padding:8px 12px;border-radius:10px;font-weight:800;margin:16px 0 10px}}div[data-testid="stMetric"]{{background:white;border:1px solid #e5e7eb;border-radius:14px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,.04)}}.post-card{{border:1px solid #ddd;border-radius:16px;padding:16px;background:#fff;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,.04)}}.badge{{display:inline-block;padding:4px 8px;border-radius:10px;background:#f3f3f3;border:1px solid #ddd;font-size:12px;font-weight:700;margin-right:4px}}.approved{{background:#dcfce7;border-color:#86efac}}.needs{{background:#fee2e2;border-color:#fecaca}}.planned{{background:#e0f2fe;border-color:#bae6fd}}.ready{{background:#fef9c3;border-color:#fde68a}}</style>
    """,unsafe_allow_html=True)
def header(): st.markdown("""<div class='hero'><h1>PTAC Refurb Marketing OS</h1><p>90-Day Content Calendar • Approvals • Engagement • Leads • Pipeline</p></div>""",unsafe_allow_html=True)
def get_config(): return st.secrets.get('APPS_SCRIPT_URL',''), st.secrets.get('APPS_SCRIPT_TOKEN','')
def has_live_connection():
    u,t=get_config(); return bool(u and t)
@st.cache_data(ttl=60, show_spinner=False)
def read_sheet(sheet_name):
    sheet_id = st.secrets.get("1Cz1iP6K6w8FomYK-y22eiWddG4PIUFsx_lp8IKYuybI", "")

    if not sheet_id:
        st.error("Missing GOOGLE_SHEET_ID in Streamlit secrets.")
        return pd.DataFrame()

    try:
        url = (
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?"
            f"tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
        )

        return pd.read_csv(url)

    except Exception as e:
        st.error(f"Could not read {sheet_name}: {e}")
        return pd.DataFrame()
def append_row(sheet_name,row):
    u,t=get_config()
    if not u or not t: st.error('Missing Streamlit secrets.'); return False
    try:
        data=requests.post(u,json={'action':'append','sheet':sheet_name,'token':t,'row':row},timeout=25).json()
        if data.get('status')=='success': st.cache_data.clear(); return True
        st.error(data.get('message','Append failed')); return False
    except Exception as e: st.error(f'Could not append row: {e}'); return False
def to_num(s): return pd.to_numeric(s,errors='coerce').fillna(0)
def parse_dates(df):
    if df.empty or 'Date' not in df.columns: return df
    out=df.copy(); out['_date']=pd.to_datetime(out['Date'],errors='coerce').dt.date; return out
def badge(text):
    v=str(text).lower(); cls='badge'
    if any(x in v for x in ['approved','done','yes','posted','complete']): cls+=' approved'
    elif any(x in v for x in ['needed','needs','not started','missing','no']): cls+=' needs'
    elif any(x in v for x in ['planned','draft','scheduled']): cls+=' planned'
    elif 'ready' in v: cls+=' ready'
    return f"<span class='{cls}'>{text or '—'}</span>"
def show_post_card(row):
    st.markdown(f"""<div class='post-card'><h3 style='margin:0;color:{DARK};'>{row.get('Topic','')}</h3><p style='margin:4px 0 10px;color:{GRAY};'><b>{row.get('Date','')}</b> • {row.get('Time','')} • {row.get('Platform','')} • {row.get('Bucket','')}</p><div>{badge('Graphic: '+str(row.get('Graphic Status','')))} {badge('Caption: '+str(row.get('Caption Status','')))} {badge('Approval: '+str(row.get('Approval Status','')))} {badge('Posted: '+str(row.get('Posted','')))}</div></div>""",unsafe_allow_html=True)
    if row.get('Caption',''):
        with st.expander('View caption'): st.write(row.get('Caption',''))
def page_executive():
    header(); cal=read_sheet(SHEET_NAMES['calendar']); kpi=read_sheet(SHEET_NAMES['kpi']); leads=read_sheet(SHEET_NAMES['leads']); pipe=read_sheet(SHEET_NAMES['pipeline']); eng=read_sheet(SHEET_NAMES['engagement'])
    latest=kpi.tail(1) if not kpi.empty else pd.DataFrame(); followers=int(to_num(latest['LinkedIn Followers']).iloc[0]) if not latest.empty and 'LinkedIn Followers' in latest else 0; impr=int(to_num(latest['Content Impressions']).iloc[0]) if not latest.empty and 'Content Impressions' in latest else 0; pv=to_num(pipe['Pipeline Value']).sum() if not pipe.empty and 'Pipeline Value' in pipe else 0
    c1,c2,c3,c4=st.columns(4); c1.metric('LinkedIn Followers',followers); c2.metric('Content Impressions',impr); c3.metric('Tracked Leads',len(leads)); c4.metric('Pipeline Value',f'${pv:,.0f}')
    st.markdown("<div class='section-title'>This Week's Posting Plan</div>",unsafe_allow_html=True); d=parse_dates(cal); today=date.today(); start=today-timedelta(days=today.weekday()); end=start+timedelta(days=6)
    week=d[(d['_date']>=start)&(d['_date']<=end)].sort_values(['_date','Time'],na_position='last') if '_date' in d else d.head(10)
    if week.empty: st.info('No posts scheduled for this week yet.')
    else:
        for _,r in week.iterrows(): show_post_card(r)
    st.markdown("<div class='section-title'>Action Center</div>",unsafe_allow_html=True); a,b,c=st.columns(3)
    a.metric('Graphics Needed', len(cal[cal.get('Graphic Status',pd.Series(dtype=str)).astype(str).str.lower().isin(['needed','needs graphic','not started',''])]) if not cal.empty else 0)
    b.metric('Approvals Needed', len(cal[cal.get('Approval Status',pd.Series(dtype=str)).astype(str).str.lower().isin(['needed','pending','needs approval','not approved',''])]) if not cal.empty else 0)
    c.metric('Engagement Actions Logged', len(eng) if not eng.empty else 0)
def page_calendar():
    header(); st.markdown("<div class='section-title'>90-Day Content Calendar</div>",unsafe_allow_html=True); df=parse_dates(read_sheet(SHEET_NAMES['calendar']))
    st.dataframe(df[[c for c in ['Date','Time','Platform','Topic','Bucket','Graphic Status','Caption Status','Approval Status','Posted'] if c in df]],use_container_width=True,hide_index=True)
    st.markdown("<div class='section-title'>Add New Calendar Item</div>",unsafe_allow_html=True)
    with st.form('add_calendar'):
        c1,c2,c3=st.columns(3)
        with c1: d=st.date_input('Date'); tm=st.text_input('Time','8:00 AM CT'); platform=st.selectbox('Platform',['LinkedIn','Facebook','Personal LinkedIn','Other'])
        with c2: topic=st.text_input('Topic'); bucket=st.selectbox('Bucket',['Cost Savings','Education','Credibility','Company Story','Engagement','Personal Brand']); approval=st.selectbox('Approval Status',['Planned','Needs Approval','Approved'])
        with c3: graphic=st.selectbox('Graphic Status',['Needed','Planned','Done']); cap=st.selectbox('Caption Status',['Needed','Draft','Done']); posted=st.selectbox('Posted',['No','Yes'])
        caption=st.text_area('Caption'); notes=st.text_area('Notes')
        if st.form_submit_button('Add to Calendar'):
            if append_row(SHEET_NAMES['calendar'],{'Date':str(d),'Time':tm,'Platform':platform,'Topic':topic,'Bucket':bucket,'Graphic Status':graphic,'Caption Status':cap,'Approval Status':approval,'Posted':posted,'Caption':caption,'Notes':notes}): st.success('Added to Content Calendar.')
def page_library():
    header(); st.markdown("<div class='section-title'>Content Library</div>",unsafe_allow_html=True); st.dataframe(read_sheet(SHEET_NAMES['library']),use_container_width=True,hide_index=True)
    with st.form('add_library'):
        topic=st.text_input('Topic'); bucket=st.selectbox('Bucket',['Cost Savings','Education','Credibility','Company Story','Engagement','Personal Brand']); hook=st.text_input('Hook'); graphic=st.text_area('Graphic Concept'); caption=st.text_area('Caption'); status=st.selectbox('Status',['Idea','Draft','Ready','Used']); notes=st.text_area('Notes')
        if st.form_submit_button('Save Idea'):
            if append_row(SHEET_NAMES['library'],{'Topic':topic,'Bucket':bucket,'Hook':hook,'Caption':caption,'Graphic Concept':graphic,'Status':status,'Notes':notes}): st.success('Saved.')
def page_engagement():
    header(); st.markdown("<div class='section-title'>Engagement Tracker</div>",unsafe_allow_html=True); st.dataframe(read_sheet(SHEET_NAMES['engagement']),use_container_width=True,hide_index=True)
    with st.form('add_engagement'):
        c1,c2=st.columns(2)
        with c1: d=st.date_input('Date',key='eng'); company=st.text_input('Company/Page'); post=st.text_input('Post Topic')
        with c2: et=st.selectbox('Engagement Type',['Comment','Like','Repost','Connection Request','Follow']); follow=st.selectbox('Follow Up Needed',['No','Yes'])
        comment=st.text_area('Comment'); notes=st.text_area('Notes')
        if st.form_submit_button('Log Engagement'):
            if append_row(SHEET_NAMES['engagement'],{'Date':str(d),'Company/Page':company,'Post Topic':post,'Comment':comment,'Engagement Type':et,'Follow Up Needed':follow,'Notes':notes}): st.success('Logged.')
def page_leads():
    header(); st.markdown("<div class='section-title'>Lead CRM</div>",unsafe_allow_html=True); st.dataframe(read_sheet(SHEET_NAMES['leads']),use_container_width=True,hide_index=True)
    with st.form('add_lead'):
        c1,c2,c3=st.columns(3)
        with c1: d=st.date_input('Date',key='lead'); company=st.text_input('Company'); contact=st.text_input('Contact Name')
        with c2: role=st.text_input('Role'); source=st.selectbox('Source',['LinkedIn','Facebook','Website','Referral','Other']); status=st.selectbox('Status',['New','Contacted','Quote Requested','Quote Sent','Won','Lost'])
        with c3: value=st.number_input('Estimated Value',min_value=0.0,step=100.0); notes=st.text_area('Notes')
        if st.form_submit_button('Add Lead'):
            if append_row(SHEET_NAMES['leads'],{'Date':str(d),'Company':company,'Contact Name':contact,'Role':role,'Source':source,'Status':status,'Estimated Value':value,'Notes':notes}): st.success('Lead added.')
def page_data(key,title): header(); st.markdown(f"<div class='section-title'>{title}</div>",unsafe_allow_html=True); st.dataframe(read_sheet(SHEET_NAMES[key]),use_container_width=True,hide_index=True)
def page_setup():
    header(); st.markdown("<div class='section-title'>Setup Check</div>",unsafe_allow_html=True); u,t=get_config(); st.success('APPS_SCRIPT_URL is set.') if u else st.error('APPS_SCRIPT_URL missing.'); st.success('APPS_SCRIPT_TOKEN is set.') if t else st.error('APPS_SCRIPT_TOKEN missing.'); st.code('\n'.join(SHEET_NAMES.values()))
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

        if has_live_connection():
            st.success("Connected to Apps Script")
        else:
            st.warning("Add Streamlit secrets")

    pages[page]()


if __name__ == "__main__":
    main()
