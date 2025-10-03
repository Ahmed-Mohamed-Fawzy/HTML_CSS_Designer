import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Canva to HTML Converter",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }
    .block-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    h1 {
        color: #667eea;
        text-align: center;
        font-size: 3rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


class CanvaToHTMLAgent:
    """Agent for converting Canva templates to HTML/CSS"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def analyze_design(self, image, custom_instructions: str = "") -> dict:
        """Analyze the design with optional custom instructions"""

        base_prompt = """Analyze this web design template image in extreme detail:

1. LAYOUT STRUCTURE: sections, grid, hierarchy
2. COLOR SCHEME: backgrounds, text, buttons, accents (hex codes)
3. TYPOGRAPHY: heading styles, body text, font weights
4. UI ELEMENTS: buttons, forms, images, icons, navigation
5. SPACING: padding, margins, alignment
6. SPECIAL EFFECTS: shadows, borders, gradients"""

        if custom_instructions:
            base_prompt += f"\n\nADDITIONAL FOCUS:\n{custom_instructions}"

        try:
            response = self.model.generate_content([base_prompt, image])
            return {"raw_analysis": response.text, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    def generate_html_css(self, analysis: dict, image, customizations: dict) -> dict:
        """Generate HTML/CSS with customization options"""

        # Build customization instructions
        custom_css = []
        if customizations.get("color_scheme"):
            custom_css.append(f"Use a {customizations['color_scheme']} color scheme")
        if customizations.get("font_size"):
            custom_css.append(f"Use {customizations['font_size']} font sizes")
        if customizations.get("spacing"):
            custom_css.append(f"Use {customizations['spacing']} spacing")
        if customizations.get("button_style"):
            custom_css.append(f"Style buttons as {customizations['button_style']}")
        if customizations.get("animations"):
            custom_css.append("Add smooth CSS animations and transitions")
        if customizations.get("custom_instructions"):
            custom_css.append(customizations["custom_instructions"])

        customization_text = (
            "\n- ".join(custom_css) if custom_css else "Follow original design"
        )

        code_prompt = f"""Generate complete HTML and CSS code based on this analysis:

ANALYSIS:
{analysis.get('raw_analysis', '')}

CUSTOMIZATIONS:
- {customization_text}

REQUIREMENTS:
1. Complete HTML5 document with DOCTYPE
2. Semantic HTML5 tags (header, nav, main, section, footer)
3. Modern CSS (Flexbox/Grid for layout)
4. Fully responsive (mobile-friendly with media queries)
5. Include ALL elements: text, buttons, forms, images (use https://placehold.co/800x400 for images)
6. Match colors exactly (use hex codes)
7. Add hover effects and transitions
8. Include viewport meta tag
9. Embed all CSS in <style> tag
10. Add helpful comments

OUTPUT: Provide ONLY complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations."""

        try:
            response = self.model.generate_content([code_prompt, image])
            html_code = self._extract_html(response.text)
            return {"html": html_code, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    def _extract_html(self, response_text: str) -> str:
        """Extract HTML from response"""
        if "```html" in response_text:
            start = response_text.find("```html") + 7
            end = response_text.find("```", start)
            return response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            return response_text[start:end].strip()
        elif "<!DOCTYPE" in response_text:
            start = response_text.find("<!DOCTYPE")
            end = response_text.rfind("</html>") + 7
            if end > start:
                return response_text[start:end].strip()
        return response_text.strip()


# Initialize session state
if "generated_html" not in st.session_state:
    st.session_state.generated_html = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# Header
st.title("🎨 Canva to HTML Converter")
st.markdown("### Transform your Canva designs into beautiful, responsive HTML/CSS code")

# Sidebar for API Key and Settings
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key Input
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Get your free API key from https://makersuite.google.com/app/apikey",
    )

    if api_key:
        st.success("✅ API Key configured")
    else:
        st.info("👆 Enter your API key to get started")

    st.markdown("---")

    st.header("🎨 Customization Options")

    color_scheme = st.selectbox(
        "Color Scheme",
        [
            "Original (from design)",
            "Modern Dark",
            "Light & Minimal",
            "Vibrant & Colorful",
            "Professional Blue",
            "Warm Earth Tones",
        ],
    )

    font_size = st.selectbox(
        "Font Size",
        ["Standard", "Small (Mobile-friendly)", "Large (Accessibility)", "Extra Large"],
    )

    spacing = st.selectbox(
        "Spacing", ["Normal", "Compact", "Generous", "Extra Spacious"]
    )

    button_style = st.selectbox(
        "Button Style",
        ["Original", "Rounded with Shadow", "Flat Modern", "Gradient", "Outlined"],
    )

    animations = st.checkbox("Add smooth animations", value=True)

    custom_instructions = st.text_area(
        "Custom Instructions",
        placeholder="E.g., 'Add a sticky navigation bar', 'Make hero section full-screen', etc.",
        height=100,
    )

    st.markdown("---")
    st.markdown("**📚 Quick Guide:**")
    st.markdown("1. Enter API key")
    st.markdown("2. Upload Canva image")
    st.markdown("3. Customize options")
    st.markdown("4. Generate HTML/CSS")
    st.markdown("5. Download result")

# Main Content Area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Canva Template")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg"],
        help="Upload your Canva template as PNG or JPG",
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Template", use_container_width=True)

        # Image info
        st.info(f"📊 Image Size: {image.size[0]} x {image.size[1]} pixels")

with col2:
    st.header("⚡ Generate Code")

    if not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar")
    elif not uploaded_file:
        st.warning("⚠️ Please upload a Canva template image")
    else:
        if st.button("✨ Generate HTML/CSS", type="primary"):

            # Prepare customizations
            customizations = {
                "color_scheme": (
                    color_scheme if color_scheme != "Original (from design)" else ""
                ),
                "font_size": (
                    font_size.split()[0].lower() if font_size != "Standard" else ""
                ),
                "spacing": spacing.lower() if spacing != "Normal" else "",
                "button_style": (
                    button_style.lower() if button_style != "Original" else ""
                ),
                "animations": animations,
                "custom_instructions": custom_instructions,
            }

            try:
                with st.spinner("🔍 Analyzing design..."):
                    agent = CanvaToHTMLAgent(api_key)
                    image = Image.open(uploaded_file)

                    # Step 1: Analyze
                    analysis = agent.analyze_design(image, custom_instructions)

                    if not analysis.get("success"):
                        st.error(f"❌ Analysis Error: {analysis.get('error')}")
                        st.stop()

                    st.session_state.analysis = analysis

                with st.spinner(
                    "💻 Generating HTML/CSS... (this may take 30-60 seconds)"
                ):
                    # Step 2: Generate
                    result = agent.generate_html_css(analysis, image, customizations)

                    if result.get("success"):
                        st.session_state.generated_html = result["html"]
                        st.success("✅ HTML/CSS generated successfully!")
                    else:
                        st.error(f"❌ Generation Error: {result.get('error')}")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Results Section
if st.session_state.generated_html:
    st.markdown("---")
    st.header("🎉 Generated Result")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📺 Preview", "💾 Download", "📊 Analysis"])

    with tab1:
        st.subheader("Live Preview")
        st.components.v1.html(
            st.session_state.generated_html, height=600, scrolling=True
        )

    with tab2:
        st.subheader("Download HTML")

        # Download button
        st.download_button(
            label="📥 Download HTML File",
            data=st.session_state.generated_html,
            file_name="generated_page.html",
            mime="text/html",
            type="primary",
        )

        # Show code
        with st.expander("👀 View HTML Code"):
            st.code(st.session_state.generated_html, language="html")

        st.info(
            "💡 **Tip:** Open the downloaded HTML file in any browser to view your webpage!"
        )

    with tab3:
        st.subheader("Design Analysis")
        if st.session_state.analysis:
            st.text_area(
                "AI Analysis of Your Design",
                st.session_state.analysis.get("raw_analysis", ""),
                height=400,
            )
        else:
            st.info("No analysis available")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🎨 <strong>Canva to HTML Converter</strong> | Powered by Google Gemini AI</p>
        <p>Made with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True,
)
