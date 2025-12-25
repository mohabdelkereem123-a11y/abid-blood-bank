import streamlit as st
import pandas as pd

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="Blood Bank Expert System", layout="wide", page_icon="🩸")

st.markdown("""
<style>
    .reportview-container { margin-top: -2em; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)

st.title("🩸 Smart Antibody Identification System")
st.caption("AI Logic V7.0 | Kidd Dosage Support | Auto-Correction Grid")

# ==========================================
# 2. القواعد الثابتة
# ==========================================
antigens_order = ["D", "C", "c", "E", "e", "K", "k", "Fya", "Fyb", "Jka", "Jkb", "M", "N", "S", "s"]
allele_pairs = {'C':'c', 'c':'C', 'E':'e', 'e':'E', 'Fya':'Fyb', 'Fyb':'Fya', 
                'Jka':'Jkb', 'Jkb':'Jka', 'M':'N', 'N':'M', 'S':'s', 's':'S', 'K':'k', 'k':'K'}

def is_homozygous(ag, ph):
    if ag == 'D': return True
    partner = allele_pairs.get(ag)
    if not partner: return True
    # Antigen Present AND Partner Absent = Homozygous
    return ph.get(ag, 0) == 1 and ph.get(partner, 0) == 0

# ==========================================
# 3. إعدادات البانل (ADMIN MODE) - "السر هنا"
# ==========================================
with st.expander("🛠️ إعدادات البانل (Admin - Setup Panel Sheet)", expanded=True):
    col_up, col_edit = st.columns([1, 2])
    
    # تهيئة الجدول الفاضي أول مرة
    if 'editor_df' not in st.session_state:
        # Initial dummy data
        default_data = [{"Cell ID": f"Cell {i+1}", **{ag: 0 for ag in antigens_order}} for i in range(11)]
        st.session_state.editor_df = pd.DataFrame(default_data)

    with col_up:
        st.info("طريقتين لإدخال الجدول (مرة كل شهر):")
        st.write("1️⃣ ارفع ملف Excel (لو متوفر).")
        st.write("2️⃣ أو عدل الجدول في الناحية الثانية يدوياً.")
        uploaded_file = st.file_uploader("Upload Excel", type=["xlsx", "xls"])
        
        if uploaded_file:
            try:
                # محاولة قراءة الملف وتنظيفه
                raw_df = pd.read_excel(uploaded_file)
                # نحاول نلاقي العواميد المشتركة
                clean_rows = []
                for i in range(min(11, len(raw_df))):
                    row_dict = {"Cell ID": f"Cell {i+1}"}
                    for ag in antigens_order:
                        # بنحاول ندور على العمود حتى لو اسمه فيه مسافات
                        found = False
                        for col in raw_df.columns:
                            if str(col).strip() == ag:
                                val = raw_df.iloc[i][col]
                                row_dict[ag] = 1 if (val==1 or val=='+' or str(val).lower()=='pos') else 0
                                found = True
                                break
                        if not found: row_dict[ag] = 0
                    clean_rows.append(row_dict)
                st.session_state.editor_df = pd.DataFrame(clean_rows)
                st.success("تم استيراد الملف! راجع الجدول لتأكيد الدقة.")
            except:
                st.error("فشل قراءة الملف. تأكد من الصيغة.")

    with col_edit:
        st.write("### 📝 Panel Grid Editor (تعديل الجدول)")
        st.caption("اضغط مرتين على أي خلية لتغيير قيمتها (1 = موجب / 0 = سالب).")
        
        # الجدول التفاعلي الرهيب
        # num_rows="fixed" عشان المستخدم ميمسحش صفوف بالغلط
        edited_panel = st.data_editor(
            st.session_state.editor_df,
            hide_index=True,
            column_config={
                "Cell ID": st.column_config.TextColumn(disabled=True),
            },
            height=38*12, # ارتفاع مناسب لـ 11 خلية
            use_container_width=True
        )

# ==========================================
# 4. إدخال نتايج المريض
# ==========================================
st.divider()
st.subheader("🧪 إدخال نتائج المريض (Patient Reactions)")

c1, c2 = st.columns([3, 1])

with c1:
    user_inputs = {}
    grid_cols = st.columns(6) # صفين للعرض الجيد
    for i in range(1, 12):
        with grid_cols[(i-1)%6]: # توزيع متناسق
            val_s = st.selectbox(f"Cell {i}", ["Neg", "w+", "1+", "2+", "3+", "4+"], key=f"reac_{i}")
            score = 0 if val_s == "Neg" else (0.5 if val_s == "w+" else int(val_s.replace("+", "")))
            user_inputs[i] = score

with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    ac = st.radio("Auto Control", ["Negative", "Positive"])
    p_name = st.text_input("رقم الملف / المريض", placeholder="اختياري")
    run_btn = st.button("تشخيص الحالة 🩺", type="primary", use_container_width=True)

# ==========================================
# 5. ANALYSIS ENGINE V7 (FINAL)
# ==========================================
if run_btn:
    st.markdown("---")
    
    # 1. Prepare Panel Data form the Edited Grid
    panel_final = []
    for idx, row in edited_panel.iterrows():
        # Clean row data
        phenotype = {k: int(v) for k, v in row.items() if k in antigens_order}
        panel_final.append({"id": idx+1, "ph": phenotype})
    
    # 2. Safety Checks
    if ac == "Positive":
        st.error("⚠️ **Auto Control Positive:** Alloantibody identification logic is suspended. Suggest Auto-Antibody workup (DAT).")
    else:
        # A) EXCLUSION
        neg_cells = [k for k,v in user_inputs.items() if v == 0]
        pos_cells = [k for k,v in user_inputs.items() if v > 0]
        
        ruled_out = set()
        debug_log = []

        for ag in antigens_order:
            for n_id in neg_cells:
                # Safe access (handle index)
                cell = panel_final[n_id-1]['ph']
                
                if cell.get(ag) == 1:
                    # Homozygous Rule Check
                    if is_homozygous(ag, cell):
                        ruled_out.add(ag)
                        debug_log.append(f"Excluded {ag} (Homozygous on Cell {n_id})")
                        break # Ruled out
                    # else: Skipped due to Heterozygous Dosage
        
        candidates = [ag for ag in antigens_order if ag not in ruled_out]
        
        # B) INCLUSION
        matches = []
        flags = []
        
        if not candidates:
             st.warning("⚪ **Inconclusive:** No common alloantibodies found. Consider Low-Frequency Antigens.")
        else:
            for cand in candidates:
                # Check 1: Does it match Positive Pattern?
                missed = []
                for p_id in pos_cells:
                    cell = panel_final[p_id-1]['ph']
                    if cell.get(cand, 0) == 0:
                        missed.append(p_id)
                
                if not missed:
                    matches.append(cand)
                else:
                    flags.append(f"Anti-{cand} is unlikely (Reacted to Cell {missed} which is Antigen Negative).")
            
            # C) DISPLAY RESULTS
            c_res1, c_res2 = st.columns([2, 1])
            with c_res1:
                if matches:
                    st.success(f"✅ **Identified Antibody:**  {'  +  '.join(['Anti-'+m for m in matches])}")
                    st.info("📋 **Next Steps:**\n- Verify patient phenotype (must be negative).\n- Confirm with 3+ cells and 3- cells.")
                    
                    if len(matches) > 1:
                        st.warning("⚠️ Multiple candidates detected. Use selected cells or enzyme panel to separate.")
                else:
                    st.error("❌ **Result:** Inconclusive Pattern (Candidates exist but don't fit Inclusion Logic).")
            
            with c_res2:
                with st.expander("Show Logic Trace"):
                    st.write("Candidates survived:", candidates)
                    if flags: st.write("Mismatch Warnings:", flags)
                    st.write("Exclusion Log:", debug_log)
