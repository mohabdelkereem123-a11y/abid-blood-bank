# احفظ الكود ده باسم app.py
import streamlit as st
import pandas as pd

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(page_title="Smart AbID System", layout="wide")

st.title("🩸 Smart Antibody Identification System (AI-Assisted)")
st.markdown("**Version 5.0 | Kidd/Duffy/MNS Dosage Sensitive Logic**")

# ==========================================
# 2. البيانات الأساسية (Logic Core)
# ==========================================
antigens = ["D", "C", "c", "E", "e", "K", "k", "Fya", "Fyb", "Jka", "Jkb", "M", "N", "S", "s"]
allele_pairs = {'C':'c', 'c':'C', 'E':'e', 'e':'E', 'Fya':'Fyb', 'Fyb':'Fya', 
                'Jka':'Jkb', 'Jkb':'Jka', 'M':'N', 'N':'M', 'S':'s', 's':'S', 'K':'k', 'k':'K'}

def is_homozygous(ag, ph):
    if ag == 'D': return True 
    partner = allele_pairs.get(ag)
    if not partner: return True
    return ph.get(ag) == 1 and ph.get(partner) == 0

# ==========================================
# 3. شاشة المدير (Admin Panel) - لتعديل اللوت
# ==========================================
with st.expander("🛠️ Admin Panel: Panel Configuration (اضغط هنا لتعديل الجدول)", expanded=True):
    st.info("قم بمطابقة الجدول الأسفل مع الـ Master Sheet الموجود في المعمل.")
    
    # مصفوفة لتخزين قيم الجدول (session state)
    if 'panel_grid' not in st.session_state:
        # القيمة الافتراضية (مثال Bio-Rad شائع)
        default_grid = [
             {"D":1,"C":1,"c":0,"E":0,"e":1,"K":0,"k":1,"Fya":1,"Fyb":1,"Jka":1,"Jkb":0,"M":1,"N":0,"S":0,"s":1}, # 1
             {"D":1,"C":1,"c":0,"E":0,"e":1,"K":0,"k":1,"Fya":0,"Fyb":1,"Jka":1,"Jkb":0,"M":1,"N":0,"S":0,"s":1}, # 2
             {"D":1,"C":0,"c":1,"E":1,"e":0,"K":0,"k":1,"Fya":1,"Fyb":0,"Jka":0,"Jkb":1,"M":0,"N":1,"S":0,"s":1}, # 3
             {"D":0,"C":1,"c":1,"E":0,"e":1,"K":0,"k":1,"Fya":1,"Fyb":0,"Jka":1,"Jkb":1,"M":0,"N":1,"S":1,"s":1}, # 4
             {"D":0,"C":0,"c":1,"E":1,"e":1,"K":0,"k":1,"Fya":0,"Fyb":1,"Jka":1,"Jkb":0,"M":0,"N":1,"S":1,"s":1}, # 5
             {"D":0,"C":0,"c":1,"E":0,"e":1,"K":1,"k":1,"Fya":0,"Fyb":1,"Jka":0,"Jkb":1,"M":1,"N":1,"S":1,"s":0}, # 6
             {"D":0,"C":0,"c":1,"E":0,"e":1,"K":0,"k":1,"Fya":0,"Fyb":1,"Jka":1,"Jkb":0,"M":0,"N":1,"S":0,"s":1}, # 7
             {"D":1,"C":0,"c":1,"E":0,"e":1,"K":0,"k":1,"Fya":0,"Fyb":0,"Jka":1,"Jkb":0,"M":0,"N":1,"S":0,"s":1}, # 8
             {"D":0,"C":0,"c":1,"E":0,"e":1,"K":0,"k":1,"Fya":0,"Fyb":1,"Jka":0,"Jkb":1,"M":0,"N":1,"S":0,"s":1}, # 9
             {"D":0,"C":0,"c":1,"E":0,"e":1,"K":0,"k":1,"Fya":1,"Fyb":0,"Jka":1,"Jkb":0,"M":1,"N":0,"S":1,"s":1}, # 10 (Edited to fit User Data Example)
             {"D":0,"C":0,"c":1,"E":0,"e":1,"K":0,"k":1,"Fya":1,"Fyb":0,"Jka":0,"Jkb":1,"M":0,"N":1,"S":0,"s":1}, # 11
        ]
        st.session_state.panel_grid = default_grid

    # رسم الجدول التفاعلي (Data Editor)
    # ده أسهل من الأزرار بكتير، جدول زي الاكسل تعدل فيه براحتك
    df_panel = pd.DataFrame(st.session_state.panel_grid)
    df_panel.index = [f"Cell {i+1}" for i in range(11)]
    
    edited_df = st.data_editor(df_panel, use_container_width=True, height=400)
    
    # تحديث الداتا بناء على تعديل المستخدم
    panel_data_list = []
    for idx, row in edited_df.iterrows():
        panel_data_list.append({"id": idx, "ph": row.to_dict()})

# ==========================================
# 4. شاشة المستخدم (إدخال النتائج)
# ==========================================
st.divider()
st.subheader("🧪 Patient Results Entry")

col1, col2 = st.columns([2, 1])

with col1:
    user_reactions = {}
    cols_input = st.columns(4) # 4 columns layout
    for i in range(1, 12):
        with cols_input[(i-1)%4]:
            val_str = st.selectbox(f"Cell {i}", ["Neg", "w+", "1+", "2+", "3+", "4+"], key=f"r_{i}")
            val = 0 if val_str == "Neg" else (0.5 if val_str == "w+" else int(val_str.replace("+", "")))
            user_reactions[i] = val

with col2:
    st.write("### Control & Info")
    ac_val = st.radio("Auto Control", ["Negative", "Positive"])
    pt_id = st.text_input("Patient ID (Optional)")
    btn_calc = st.button("🔍 Analyze Results", type="primary", use_container_width=True)

# ==========================================
# 5. محرك التحليل (The Engine)
# ==========================================
if btn_calc:
    st.divider()
    st.subheader("📊 Analysis Report")
    
    if ac_val == "Positive":
        st.error("🛑 CRITICAL: Auto Control is POSITIVE. Direct Antiglobulin Test (DAT) Required. Logic Suspended.")
    else:
        # Phase 1: Exclusion
        neg_cells = [cid for cid, v in user_reactions.items() if v == 0]
        pos_cells = [cid for cid, v in user_reactions.items() if v > 0]
        
        ruled_out = set()
        debug_info = [] # عشان نشوف البرنامج فكر ازاي

        for ag in antigens:
            for cid in neg_cells:
                # Get phenotype from Edited Table
                cell_ph = panel_data_list[int(cid)-1]['ph'] # cid-1 because list index starts at 0
                
                if cell_ph.get(ag) == 1:
                    if is_homozygous(ag, cell_ph):
                        ruled_out.add(ag)
                        debug_info.append(f"Excluded {ag} on Homozygous Cell {cid}")
                        break
        
        candidates = [ag for ag in antigens if ag not in ruled_out]
        
        # Phase 2: Inclusion Pattern
        confirmed_matches = []
        notes = []

        if len(candidates) == 0:
             st.warning("⚪ Result: Pan-Negative or Antibody to Low Frequency Antigen.")
        else:
             for cand in candidates:
                 # Check Matches
                 missed_positives = []
                 for pid in pos_cells:
                     cell_ph = panel_data_list[int(pid)-1]['ph']
                     if cell_ph.get(cand) == 0:
                         missed_positives.append(pid)
                 
                 if not missed_positives:
                     confirmed_matches.append(cand)
                 else:
                     notes.append(f"Anti-{cand} is unlikely (Patient reacted to Cell {missed_positives} which lacks {cand}).")

             if confirmed_matches:
                 st.success(f"✅ Likely Antibody Identified: {', '.join(['Anti-'+c for c in confirmed_matches])}")
                 if len(confirmed_matches) > 1:
                     st.info("⚠️ Multiple candidates found. Compare pattern phases or use selected cells.")
                 
                 st.markdown("---")
                 st.write("**Rule-out Logic Log:**")
                 st.json(list(ruled_out))
             else:
                 st.error("❌ Inconclusive. Candidates exist but do not fit the reaction pattern.")
                 st.write("Candidates that passed exclusion but failed pattern match:", candidates)
                 for n in notes: st.write("- " + n)