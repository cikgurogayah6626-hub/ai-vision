# app.py

````python
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import traceback

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Automotive AI Vision Analyzer",
    page_icon="🚗",
    layout="centered"
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🚗 AI Vision: Automotive Component Analyzer")

st.markdown(
    """
Upload gambar komponen kereta dan AI akan:

✅ Kenal pasti komponen  
✅ Detect brand  
✅ Extract spesifikasi  
✅ Terangkan fungsi  
✅ Detect part number  
✅ OCR teks pada label/packaging  
"""
)

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

    # TEST API BUTTON
    if st.button("🧪 Test API Key", use_container_width=True):

        if not api_key:
            st.error("Paste API key first.")

        else:
            try:
                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Reply with OK"
                )

                st.success(response.text)

            except Exception as e:

                st.error(str(e))
                st.code(traceback.format_exc())

# -------------------------------------------------
# FILE UPLOADER
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "📁 Upload Automotive Component Image",
    type=["jpg", "jpeg", "png", "webp"]
)

# -------------------------------------------------
# DEFAULT PROMPT
# -------------------------------------------------
default_prompt = """
You are an automotive component analysis AI assistant.

Analyze the uploaded automotive component image carefully using OCR and visual recognition.

Return STRICT JSON only.

Required JSON format:

{
  "component_name": "",
  "brand": "",
  "category": "",
  "part_number": "",
  "vehicle_compatibility": "",
  "specifications": {
    "material": "",
    "size": "",
    "weight": "",
    "power_rating": "",
    "voltage": "",
    "dimensions": ""
  },
  "function_or_usage": "",
  "condition": "",
  "estimated_price": null,
  "visible_text": [],
  "detected_labels": [],
  "confidence_score": 0
}

Rules:
1. Return STRICT JSON only.
2. Use null if information is missing.
3. Never guess unknown values.
4. Read all visible text from labels, stickers, engraving, packaging.
5. Detect automotive components accurately.
6. Explain briefly the function or usage.
7. confidence_score must be between 0 and 100.
"""

# -------------------------------------------------
# PROMPT BOX
# -------------------------------------------------
st.markdown("### 🎯 AI Prompt")

prompt = st.text_area(
    "Prompt",
    value=default_prompt,
    height=350
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
        st.error("❌ Please enter Gemini API Key.")
        st.stop()

    if not uploaded_file:
        st.error("❌ Please upload image first.")
        st.stop()

    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("❌ File too large. Max 10MB.")
        st.stop()

    try:

        # OPEN IMAGE
        image = Image.open(uploaded_file).convert("RGB")

        # DISPLAY
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📷 Uploaded Image")
            st.image(image, use_container_width=True)

        # GEMINI CLIENT
        client = genai.Client(api_key=api_key)

        with col2:

            st.markdown("### 🤖 AI Analysis")

            with st.spinner("Analyzing component..."):

                response = client.models.generate_content(

                    model="gemini-2.5-flash",

                    contents=[prompt, image],

                    config=types.GenerateContentConfig(

                        temperature=0.1,

                        response_mime_type="application/json",

                        response_schema={
                            "type": "object",
                            "properties": {

                                "component_name": {
                                    "type": ["string", "null"]
                                },

                                "brand": {
                                    "type": ["string", "null"]
                                },

                                "category": {
                                    "type": ["string", "null"]
                                },

                                "part_number": {
                                    "type": ["string", "null"]
                                },

                                "vehicle_compatibility": {
                                    "type": ["string", "null"]
                                },

                                "specifications": {
                                    "type": "object"
                                },

                                "function_or_usage": {
                                    "type": ["string", "null"]
                                },

                                "condition": {
                                    "type": ["string", "null"]
                                },

                                "estimated_price": {
                                    "type": ["number", "null"]
                                },

                                "visible_text": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },

                                "detected_labels": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },

                                "confidence_score": {
                                    "type": "number"
                                }
                            }
                        }
                    )
                )

                # ---------------------------------
                # SAFE RESPONSE PARSING
                # ---------------------------------
                raw_text = ""

                if hasattr(response, "text") and response.text:
                    raw_text = response.text.strip()

                elif response.candidates:
                    raw_text = (
                        response.candidates[0]
                        .content.parts[0]
                        .text.strip()
                    )

                # CLEAN MARKDOWN
                raw_text = raw_text.strip()

                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1]

                if "```" in raw_text:
                    raw_text = raw_text.split("```")[0]

                raw_text = raw_text.strip()

                # ---------------------------------
                # JSON PARSE
                # ---------------------------------
                try:

                    parsed_json = json.loads(raw_text)

                    st.success("✅ Analysis Complete")

                    st.json(parsed_json)

                    # DOWNLOAD
                    json_str = json.dumps(
                        parsed_json,
                        indent=2,
                        ensure_ascii=False
                    )

                    st.download_button(
                        label="⬇️ Download JSON",
                        data=json_str,
                        file_name="automotive_analysis.json",
                        mime="application/json",
                        use_container_width=True
                    )

                except json.JSONDecodeError:

                    st.warning(
                        "⚠️ Invalid JSON response."
                    )

                    st.code(raw_text, language="json")

    except Exception as e:

        error_msg = str(e)

        if (
            "API key" in error_msg
            or "API_KEY" in error_msg
            or "401" in error_msg
        ):

            st.error("❌ Invalid API Key.")

        elif (
            "quota" in error_msg.lower()
            or "rate" in error_msg.lower()
            or "429" in error_msg
        ):

            st.error(
                "❌ Rate limit exceeded."
            )

        elif (
            "404" in error_msg
            or "NOT_FOUND" in error_msg
        ):

            st.error(
                "❌ Model not found."
            )

        else:

            st.error(f"❌ System Error: {error_msg}")

            st.code(traceback.format_exc())

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")

st.caption(
    "🚗 Automotive AI Vision Analyzer • Gemini 2.5 Flash"
)
````
