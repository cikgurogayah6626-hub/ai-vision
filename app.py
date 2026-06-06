import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import pandas as pd
import io
import traceback

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Automotive AI Vision Analyzer",
    page_icon="🚗",
    layout="wide"
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🚗 Automotive AI Vision Analyzer")

st.markdown("""
Upload gambar komponen kereta dan AI akan:

✅ Kenal pasti komponen  
✅ Detect brand  
✅ Extract spesifikasi  
✅ Terangkan fungsi  
✅ OCR teks pada label  
✅ Export ke Excel  
""")

st.markdown("---")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:

    st.header("⚙️ Gemini API Setup")

    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password"
    )

    st.markdown(
        "[🔑 Get API Key](https://aistudio.google.com/app/apikey)"
    )

    st.divider()

    if st.button("🧪 Test API Key", use_container_width=True):

        if not api_key:
            st.error("Paste API key first.")

        else:
            try:
                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Reply only with: OK"
                )

                st.success(response.text)

            except Exception as e:
                st.error(str(e))
                st.code(traceback.format_exc())

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "📁 Upload Automotive Component Image",
    type=["jpg", "jpeg", "png", "webp"]
)

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
default_prompt = """
Analyze this automotive component image.

Extract:
- Component Name
- Brand
- Category
- Part Number
- Vehicle Compatibility
- Specifications
- Function or Usage
- Condition
- Estimated Price
- Visible Text
- Confidence Score

Return clean readable text only.
"""

# -------------------------------------------------
# PROMPT BOX
# -------------------------------------------------
st.markdown("### 🎯 AI Prompt")

prompt = st.text_area(
    "Prompt",
    value=default_prompt,
    height=180
)

# -------------------------------------------------
# ANALYZE BUTTON
# -------------------------------------------------
if st.button(
    "🚀 Analyze Component",
    type="primary",
    use_container_width=True
):

    # VALIDATION
    if not api_key:
        st.error("❌ Please enter API key.")
        st.stop()

    if not uploaded_file:
        st.error("❌ Please upload image.")
        st.stop()

    try:

        # OPEN IMAGE
        image = Image.open(uploaded_file).convert("RGB")

        # DISPLAY
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(
                image,
                caption="Uploaded Image",
                use_container_width=True
            )

        # GEMINI CLIENT
        client = genai.Client(api_key=api_key)

        with col2:

            with st.spinner("🤖 AI analyzing automotive component..."):

                response = client.models.generate_content(

                    model="gemini-2.5-flash",

                    contents=[prompt, image],

                    config=types.GenerateContentConfig(
                        temperature=0.1
                    )
                )

                result = response.text

                # -----------------------------------------
                # SIMPLE TEXT PARSING
                # -----------------------------------------
                lines = result.split("\n")

                data = {
                    "Field": [],
                    "Value": []
                }

                for line in lines:

                    if ":" in line:

                        parts = line.split(":", 1)

                        field = parts[0].strip()
                        value = parts[1].strip()

                        if field and value:

                            data["Field"].append(field)
                            data["Value"].append(value)

                # -----------------------------------------
                # FALLBACK IF NO STRUCTURE
                # -----------------------------------------
                if len(data["Field"]) == 0:

                    data["Field"].append("Analysis")
                    data["Value"].append(result)

                # -----------------------------------------
                # DATAFRAME
                # -----------------------------------------
                df = pd.DataFrame(data)

                st.success("✅ Analysis Complete")

                st.markdown("### 📊 Analysis Table")

                st.dataframe(
                    df,
                    use_container_width=True
                )

                # -----------------------------------------
                # EXCEL EXPORT
                # -----------------------------------------
                output = io.BytesIO()

                with pd.ExcelWriter(
                    output,
                    engine="openpyxl"
                ) as writer:

                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Automotive Analysis"
                    )

                excel_data = output.getvalue()

                st.download_button(
                    label="⬇️ Download Excel Report",
                    data=excel_data,
                    file_name="automotive_analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                # -----------------------------------------
                # RAW RESPONSE
                # -----------------------------------------
                with st.expander("🧠 Raw AI Response"):

                    st.text(result)

    except Exception as e:

        st.error(f"❌ Error: {str(e)}")

        st.code(traceback.format_exc())

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")

st.caption(
    "🚗 Automotive AI Vision Analyzer • Streamlit + Gemini 2.5 Flash"
)
