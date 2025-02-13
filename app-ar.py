import streamlit as st
import pandas as pd
import io

# Initialize session state
if "products" not in st.session_state:
    st.session_state.products = []
    st.session_state.current_product = 0
    st.session_state.file_uploaded = False  

def load_excel_data(file):
    """Load Excel or CSV data and store it in session state"""
    try:
        # Detect file format
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Standardize column names
        column_mapping = {"image": "image link"}  
        df.rename(columns=column_mapping, inplace=True)

        # Required columns
        required_columns = {"name", "image link", "details"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            st.error(f"❌ خطأ: الأعمدة المفقودة: {', '.join(missing_columns)}")
            return

        # Convert dataframe to a list of dictionaries
        products = df.to_dict("records")
        if not products:
            st.error("⚠️ الملف فارغ أو لا يحتوي على منتجات.")
            return

        # Store in session state
        st.session_state.products = products
        st.session_state.current_product = 0  
        st.session_state.file_uploaded = True  
        st.rerun()

    except Exception as e:
        st.error(f"❌ خطأ في تحميل الملف: {e}")

def next_product():
    """Move to the next product"""
    if st.session_state.products:
        st.session_state.current_product = (st.session_state.current_product + 1) % len(st.session_state.products)

def prev_product():
    """Move to the previous product"""
    if st.session_state.products:
        st.session_state.current_product = (st.session_state.current_product - 1) % len(st.session_state.products)

def reset_products():
    """Reset uploaded products"""
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
    </style>
""", unsafe_allow_html=True)

# --- Streamlit UI ---
st.markdown("<h1 style='text-align: center; color: #BB9167;'>📦 معرض المنتجات</h1></br>", unsafe_allow_html=True)

# File uploader
if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("📂 تحميل ملف Excel أو CSV", type=["xlsx", "csv"])
    if uploaded_file is not None:
        load_excel_data(uploaded_file)

st.button("🔄 إعادة ضبط", on_click=reset_products)

# Display product information
if st.session_state.products:
    product = st.session_state.products[st.session_state.current_product]

    st.markdown(f"<h2 style='text-align: center;'>{product['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #ababab;'>{product['details']}</p>", unsafe_allow_html=True)
    
    # Custom CSS for Vertical Centering Buttons
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
            font-family: Cairo, sans-serif;
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
            st.image(image_url, width=400)
        else:
            st.warning("⚠️ لا يوجد رابط صورة صالح. سيتم عرض صورة افتراضية.")
            st.image("https://github.com/AlexNoor74/product-gallery/blob/main/pngwing.com.png", width=400)

    with col3:
        if len(st.session_state.products) > 1:
            st.button("التالي ▶", on_click=next_product, help="المنتج التالي")

    st.markdown(f"</br><p style='text-align: center; font-size: 18px; font-weight: bold;'>🛍️ المنتج {st.session_state.current_product + 1} من {len(st.session_state.products)}</p>", unsafe_allow_html=True)

else:
    st.info("📌 لا يوجد منتجات لعرضها. يرجى تحميل ملف Excel أو CSV.")

# Sidebar: Instructions (Translated)
st.sidebar.header("📌 التعليمات")
st.sidebar.write("""
1. قم بإعداد ملف **Excel (.xlsx) أو CSV (.csv)** يحتوي على الأعمدة:  
   - **name (الاسم)**  
   - **image link (رابط الصورة)**  
   - **details (التفاصيل)**  
2. اضغط على **"تحميل ملف"** لإضافة الملف.  
3. سيعرض التطبيق المنتجات مع الصور والأسماء والتفاصيل.  
4. استخدم **⬅️ السابق & التالي ➡️** للتنقل بين المنتجات.  
""")

# Sidebar: Sample Excel Download
st.sidebar.header("📄 Sample Excel Format")
sample_data = pd.DataFrame({
    "name": ["Product A", "Product B", "Product C"],
    "image": ["https://images.pexels.com/photos/19254458/pexels-photo-19254458/free-photo-of-elegant-couple-walking-on-the-pavement-in-city.jpeg", 
              "https://images.pexels.com/photos/19986440/pexels-photo-19986440/free-photo-of-sweet-cake-with-heart-and-letter.jpeg",
              "https://images.unsplash.com/photo-1576566588028-4147f3842f27"],
    "details": ["Details about Product A", "Details about Product B", "Details about Product C"]
})

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    sample_data.to_excel(writer, index=False, sheet_name="Sheet1")
st.sidebar.download_button(
    label="📥 Download Sample Excel",
    data=buffer,
    file_name="sample_product_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
