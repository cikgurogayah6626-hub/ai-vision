# ==========================================
# CELL 2: BUILD THE AI VISION APP (app.py)
# FIXED: Using gemini-2.5-flash (current model)
# ==========================================


import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import traceback

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Vision AI Data Extractor | MISDEC",
    page_icon="🤖",
    layout="centered"
)

# --- HEADER ---
st.title("📄 AI Vision: Document Data Extractor")
st.caption("Built for MISDEC AI Training • Cik Kiah War Room")
st.markdown("---")
st.markdown(
    "Upload a document image (receipt, invoice, form, handwriting) and watch "
    "Gemini AI extract structured data in seconds. ✨"
)

# --- SIDEBAR: API KEY ---
with st.sidebar:
    st.header("⚙️ System Setup")
    api_key = st.text_input(
        "Enter your Gemini API Key:",
        type="password",
        help="Get it from Google AI Studio"
    )
    st.markdown(
        "🔑 [Get your API Key](https://aistudio.google.com/app/apikey)"
    )

    # --- API Key Tester Button ---
    st.divider()
    if st.button("🧪 Test API Key", use_container_width=True):
        if not api_key:
            st.error("Paste a key first")
        else:
            try:
                client = genai.Client(api_key=api_key)
                test_response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=["Say hello in one word"]
                )
                st.success(f"✅ Key works! Response: {test_response.text}")
            except Exception as e:
                st.error(f"❌ RAW ERROR:\n\n{type(e).__name__}: {str(e)}")
                st.code(traceback.format_exc())

    st.divider()
    st.caption("💡 Your API key is never stored. Stays in your browser only.")
    st.divider()
    st.caption("🎓 MISDEC AI Vision Training")
    st.caption("Trainer: Muhammad Nur Aqmal bin Khatiman")

# --- MAIN: FILE UPLOAD ---
uploaded_file = st.file_uploader(
    "📁 Upload your document image:",
    type=["jpg", "png", "jpeg", "webp"],
    help="Max 10MB. Works best with clear, well-lit images."
)

# --- DEFAULT PROMPT ---
default_prompt = """You are a professional data extraction assistant.

Extract these fields into JSON:
- document_type: receipt | invoice | claim_form | other
- date: YYYY-MM-DD, or null
- currency: MYR | USD | GBP | AUD | null   (detect from the document)
- vendor_name: string, or null
- total_amount: number only; null if absent (null is NOT 0.00)
- key_items: list of { "item": string|null, "amount": number|null }

Rules:
1. Every field present. If genuinely absent/unreadable, use null — never guess.
2. null = "not in the document"; 0.00 = the document says zero.
3. Preserve original language for text fields.
"""

# --- PROMPT EDITOR ---
st.markdown("### 🎯 AI Instruction (Prompt)")
prompt = st.text_area(
    "Edit the prompt to customize what you want to extract:",
    value=default_prompt,
    height=250,
    label_visibility="collapsed"
)

# --- ACTION BUTTON ---
if st.button("🚀 Extract Data with AI", type="primary", use_container_width=True):

    if not api_key:
        st.error("❌ Please enter your Gemini API Key in the sidebar.")
        st.stop()

    if not uploaded_file:
        st.error("❌ Please upload a document image first.")
        st.stop()

    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("❌ File too large. Please upload an image under 10MB.")
        st.stop()

    try:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📷 Your Document")
            st.image(image, use_container_width=True)

        client = genai.Client(api_key=api_key)

        with col2:
            st.markdown("#### ✨ AI Extraction Result")
            with st.spinner("🧠 AI is analyzing your document..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, image],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    )
                )

                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                try:
                    parsed_json = json.loads(raw_text)
                    st.success("✅ Data extracted successfully!")
                    st.json(parsed_json)

                    json_str = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="⬇️ Download JSON",
                        data=json_str,
                        file_name="extracted_data.json",
                        mime="application/json",
                        use_container_width=True
                    )
                except json.JSONDecodeError:
                    st.warning("⚠️ AI returned data but not strict JSON.")
                    st.code(raw_text, language="json")

    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "API_KEY" in error_msg or "401" in error_msg:
            st.error(
                "❌ Invalid API Key. Double-check the key you pasted. "
                "Get a new one from [Google AI Studio](https://aistudio.google.com/app/apikey)."
            )
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower() or "429" in error_msg:
            st.error(
                "❌ Rate limit hit. Wait 1 minute and try again. "
                "Free tier has limits — that's normal."
            )
        elif "404" in error_msg or "NOT_FOUND" in error_msg:
            st.error(
                "❌ Model not found. The model name might be outdated. "
                "Contact trainer for assistance."
            )
        else:
            st.error(f"❌ System Error: {error_msg}")

# --- FOOTER ---
st.markdown("---")
st.caption(
    "🎓 Building AI Vision App with Gemini API • "
    "MISDEC Melaka • 06 June 2026"
)
