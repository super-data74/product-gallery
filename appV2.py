import streamlit as st
import pandas as pd
import io

# Initialize session state
if "products" not in st.session_state:
    st.session_state.products = []
    st.session_state.current_product = 0
    st.session_state.file_uploaded = False  
    st.session_state.data_source = "Google Sheet"  # default option

def load_excel_data(file):
    """Load Excel or CSV data and store it in session state."""
    try:
        # Detect file format
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        process_dataframe(df)
    except Exception as e:
        st.error(f"Error loading file: {e}", icon="❌")

def load_google_sheet_data(sheet_id, sheet_name):
    """Load data from a Google Sheet using its sheet id and tab name."""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)
        process_dataframe(df)
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}", icon="❌")

def process_dataframe(df):
    """Process the dataframe by standardizing columns and updating session state."""
    # Rename column "image" to "image link" if needed.
    df.rename(columns={"image": "image link"}, inplace=True)

    required_columns = {"name", "image link", "details", "price"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        st.error(f"Error: Missing columns: {', '.join(missing_columns)}", icon="❌")
        return

    products = df.to_dict("records")
    if not products:
        st.error("The file is empty or contains no products.", icon="⚠️")
        return

    st.session_state.products = products
    st.session_state.current_product = 0  
    st.session_state.file_uploaded = True  
    st.rerun()

def next_product():
    """Move to the next product."""
    if st.session_state.products:
        st.session_state.current_product = (st.session_state.current_product + 1) % len(st.session_state.products)

def prev_product():
    """Move to the previous product."""
    if st.session_state.products:
        st.session_state.current_product = (st.session_state.current_product - 1) % len(st.session_state.products)

def reset_products():
    """Reset uploaded products."""
    st.session_state.products = []
    st.session_state.current_product = 0
    st.session_state.file_uploaded = False
    st.rerun()

# --- Global CSS for Cairo Font ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;700&display=swap');
    * {
        font-family: 'Cairo', sans-serif !important;
    }
    .stButton>button {
        font-family: 'Cairo', sans-serif;
        font-size: 16px;
    }
    .stTextInput>div>div>input {
        font-family: 'Cairo', sans-serif;
    }
    .stSidebar .stDownloadButton>button {
        font-family: 'Cairo', sans-serif;
    }
    .stMarkdown {
        font-family: 'Cairo', sans-serif;
    }
    .stRadio {
        place-items: center;
        font-size: 20px;
        background-color: rgb(165 142 109 / 60%);
        border-radius: 10px;
        padding: 0px 10px;
    }
    .stRadio>label>div {
        font-size: 20px;
        # background-color: rgb(193 152 111 / 35%);
        # border-radius: 10px;
        # padding: 0px 10px;
    }
    # .stButton {
    #     text-align-last: center;
    # }
    </style>
""", unsafe_allow_html=True)

# --- Streamlit UI Header ---
st.markdown("<h1 style='text-align: center; color: #BB9167;'>📦 معرض المنتجات</h1></br>", unsafe_allow_html=True)
st.button("🔄 إعادة ضبط", on_click=reset_products)

# --- Data Source Selector ---
if not st.session_state.file_uploaded:
    # st.markdown("### Select Data Source")
    data_source = st.radio("Select Data Source", horizontal=True,
                           options=["Offline File [CSV, Excel]", "Google Sheet"], index=1)  # default is Google Sheet
    st.session_state.data_source = data_source

    if data_source == "Offline File [CSV, Excel]":
        uploaded_file = st.file_uploader("📂 تحميل ملف Excel أو CSV", type=["xlsx", "csv"])
        if uploaded_file is not None:
            load_excel_data(uploaded_file)

    else:
        # st.toast("🔒 Make sure the Google Sheet is publicly accessible.", icon="🔒")
        # st.info("Provide your Google Sheet information:")
        sheet_id = st.text_input("Sheet ID", value="1qHVPWgCJrnC91TKQ_p4yruru53kUQrxSsaGrWfieaa4").replace(" ", "%20")
        sheet_name = st.text_input("Sheet Name", value="Sheet1").replace(" ", "%20")
        if st.button("Load Google Sheet Data", type='primary'):
            load_google_sheet_data(sheet_id, sheet_name)

# --- Display product information ---
if st.session_state.products:
    product = st.session_state.products[st.session_state.current_product]

    st.markdown(f"<h2 style='text-align: center;'>{product['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #ababab;'>{product['details']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 14px; color: #ababab;'>{product['price']}</p>", unsafe_allow_html=True)    
    
    st.markdown("""
        <style>
        .container { 
            display: flex; 
            align-items: center; 
            justify-content: center; 
        }
        .image-container {
            text-align: center;
        }
        .nav-button {
            display: flex; 
            align-items: center; 
            justify-content: center;
            height: 100%;
        }
        img {
            border-radius: 20px;
        }
        .stColumn {align-content: center;}  
        .counter {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Cairo', sans-serif;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        if len(st.session_state.products) > 1:
            st.button("◀ السابق", on_click=prev_product, help="المنتج السابق")

    with col2:
        image_url = product.get("image link", "")
        if isinstance(image_url, str) and image_url.startswith("http"):
            st.image(image_url, width=500)
        else:
            st.warning("No valid image URL found. Displaying a placeholder image.", icon="⚠️")
            st.image("https://via.placeholder.com/400", width=500)

    with col3:
        if len(st.session_state.products) > 1:
            st.button(" التالي ▶ ", on_click=next_product, help="المنتج التالي")

    st.markdown(f"</br><p style='text-align: center; font-size: 18px; font-weight: bold;'>🛍️ المنتج {st.session_state.current_product + 1} من {len(st.session_state.products)}</p>", unsafe_allow_html=True)

else:
    st.info("No products to display. Please load an Excel/CSV file or a Google Sheet.", icon="📌")

# --- Sidebar: Instructions (Translated) ---
st.sidebar.header("📌 التعليمات")
st.sidebar.write("""
1. قم بإعداد ملف **Excel (.xlsx) أو CSV (.csv)** يحتوي على الأعمدة:  
   - **name (الاسم)**  
   - **image link (رابط الصورة)**  
   - **details (التفاصيل)**  
   - **price (سعر)**  
2. أو قم بإعداد Google Sheet يحتوي على نفس الأعمدة.
3. اختر مصدر البيانات المناسب من الأعلى.
4. استخدم **⬅️ السابق & التالي ➡️** للتنقل بين المنتجات.  
""")

# --- Sidebar: Sample Excel Download ---
st.sidebar.header("📄 Sample Excel Format")
sample_data = pd.DataFrame({
    "name": ["Product A", "Product B", "Product C"],
    "image": [
        "https://images.pexels.com/photos/19254458/pexels-photo-19254458/free-photo-of-elegant-couple-walking-on-the-pavement-in-city.jpeg", 
        "https://images.pexels.com/photos/19986440/pexels-photo-19986440/free-photo-of-sweet-cake-with-heart-and-letter.jpeg",
        "https://images.unsplash.com/photo-1576566588028-4147f3842f27"
    ],
    "details": ["Details about Product A", "Details about Product B", "Details about Product C"],
    "price": ["2115 SAR", "250 SAR", "2300 SAR"]
})

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    sample_data.to_excel(writer, index=False, sheet_name="Sheet1")
st.sidebar.download_button(
    label="Download Sample Excel",
    icon="📥",
    data=buffer,
    file_name="sample_product_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
