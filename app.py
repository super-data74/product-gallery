import streamlit as st
import pandas as pd
import io

# Initialize session state
if "products" not in st.session_state:
    st.session_state.products = []
    st.session_state.current_product = 0
    st.session_state.file_uploaded = False  # Track file upload status

def load_excel_data(file):
    """Load Excel data and store it in session state"""
    try:
        df = pd.read_excel(file)

        # Automatically detect column names
        column_mapping = {"image": "image link"}  # Handle 'image' instead of 'image link'
        df.rename(columns=column_mapping, inplace=True)

        # Required columns
        required_columns = {"name", "image link", "details"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            st.error(f"Error: Missing required columns: {', '.join(missing_columns)}")
            return

        # Convert dataframe to a list of dictionaries
        products = df.to_dict("records")
        if not products:
            st.error("Uploaded file is empty or contains no products.")
            return

        # Store in session state
        st.session_state.products = products
        st.session_state.current_product = 0  # Reset to first product
        st.session_state.file_uploaded = True  # Auto-hide file uploader
        st.rerun()  # 🔥 Auto-refresh UI to hide uploader immediately

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

# Define callback functions to switch products
def next_product():
    """Move to the next product"""
    if st.session_state.products:
        st.session_state.current_product = (st.session_state.current_product + 1) % len(st.session_state.products)

def prev_product():
    """Move to the previous product"""
    if st.session_state.products:
        st.session_state.current_product = (st.session_state.current_product - 1) % len(st.session_state.products)

def reset_products():
    """Reset uploaded products and show file uploader again"""
    st.session_state.products = []
    st.session_state.current_product = 0
    st.session_state.file_uploaded = False  # Show file uploader again
    st.rerun()  # 🔥 Auto-refresh UI to show uploader immediately

# --- Streamlit UI ---
st.markdown(
    """
    <h1 style="text-align: center; font-family: 'Cairo', sans-serif; color: #BB9167;">📦 Gallery App</h1>
    """,
    unsafe_allow_html=True
)

# File uploader (Auto-hide after successful upload)
if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("📂 Upload an Excel file", type="xlsx", key="file_uploader")

    if uploaded_file is not None:
        load_excel_data(uploaded_file)  # 🔥 File uploader auto-hides immediately after upload

# Always show reset button
st.button("🔄 Reset", on_click=reset_products)

# Display product information if available
if st.session_state.products:
    product = st.session_state.products[st.session_state.current_product]

    # Product Name
    st.markdown(
        f"<h2 style='text-align: center; font-family: Cairo, sans-serif;'>{product['name']}</h2>",
        unsafe_allow_html=True
    )

    # Product Details (under the name)
    st.markdown(
        f"<p style='text-align: center; font-size: 18px; font-family: Cairo, sans-serif; color: #ababab;'>{product['details']}</p>",
        unsafe_allow_html=True
    )

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

    # Centered layout: Previous button | Image | Next button
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if len(st.session_state.products) > 1:
            st.button("◀", on_click=prev_product, key="prev_button", help="Previous Product", args=(), kwargs={}, disabled=False)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if isinstance(product.get("image link"), str) and product["image link"].startswith("http"):
            st.markdown(
                f"""
                <div class="image-container">
                    <img src="{product['image link']}" width="530" height="650">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ No valid image URL provided.")

    with col3:
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if len(st.session_state.products) > 1:
            st.button("▶", on_click=next_product, key="next_button", help="Next Product", args=(), kwargs={}, disabled=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # Centered Product Counter
    st.markdown(
        f"</br><p class='counter'>🛍️ Product {st.session_state.current_product + 1} of {len(st.session_state.products)}</p>",
        unsafe_allow_html=True
    )

else:
    st.info("📌 No products to display. Please upload an Excel file.")

# Sidebar: Instructions
st.sidebar.header("📌 Instructions")
st.sidebar.write("""
1. Prepare an Excel file with columns: **name, image, details**.
2. Click **"Browse files"** to upload your Excel file.
3. The app will display products with images, names, and details.
4. Use **⬅️ & ➡️ buttons** to navigate between products.
""")

# Sidebar: Sample Excel Download
st.sidebar.header("📄 Sample Excel Format")
sample_data = pd.DataFrame({
    "name": ["Product A", "Product B"],
    "image": ["https://images.pexels.com/photos/19254458/pexels-photo-19254458/free-photo-of-elegant-couple-walking-on-the-pavement-in-city.jpeg", "https://images.pexels.com/photos/19986440/pexels-photo-19986440/free-photo-of-sweet-cake-with-heart-and-letter.jpeg"],
    "details": ["Details about Product A", "Details about Product B"]
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
