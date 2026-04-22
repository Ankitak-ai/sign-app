from __future__ import annotations

import base64
from datetime import date

import streamlit as st
from streamlit.errors import StreamlitAPIException
from streamlit_drawable_canvas import st_canvas

from auth import login_widget
from pdf_generator import generate_contract
from signature_utils import apply_signature_to_pdf, normalize_signature_image, typed_signature_to_png_bytes
from storage import save_contract_record


st.set_page_config(page_title="HyperChat Contract Generator", layout="wide")
st.title("HyperChat Contract Generator")


for key, default in {
    "contract_data": None,
    "generated_pdf": None,
    "signing_status": "Not Generated",
    "signed_pdf": None,
    "signature_image": None,
    "contract_id": None,
    "is_authenticated": False,
    "user_email": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


use_auth = st.sidebar.toggle("Enable login", value=False)
if use_auth and not login_widget():
    st.info("Please login to continue.")
    st.stop()


left, right = st.columns([1, 1])


with left:
    with st.form("contract_form"):
        streamer_handle = st.text_input("Streamer Handle")
        streamer_legal_name = st.text_input("Streamer Legal Name")
        streamer_govt_id = st.text_input("Government ID")
        effective_date = st.date_input("Effective Date", value=date.today())
        contract_months = st.number_input("Contract Duration (months)", min_value=1, value=12, step=1)

        fee_type = st.radio("Fee Type", ["Fixed %", "Dynamic"], horizontal=True)
        fee_percentage = None
        if fee_type == "Fixed %":
            fee_percentage = st.number_input("Fee %", min_value=0.0, max_value=100.0, value=20.0, step=0.5)

        submitted = st.form_submit_button("Generate Contract")

        if submitted:
            data = {
                "streamer_handle": streamer_handle,
                "streamer_legal_name": streamer_legal_name,
                "streamer_govt_id": streamer_govt_id,
                "effective_date": effective_date.strftime("%d/%m/%Y"),
                "contract_months": int(contract_months),
                "fee_type": fee_type,
                "fee_percentage": str(fee_percentage).rstrip("0").rstrip(".") if fee_percentage is not None else None,
            }
            st.session_state.contract_data = data
            st.session_state.generated_pdf = generate_contract(data)
            st.session_state.signing_status = "Generated"
            st.session_state.signed_pdf = None
            st.session_state.signature_image = None
            st.session_state.contract_id = save_contract_record(data, st.session_state.generated_pdf)
            st.success("Contract generated.")

    if st.session_state.contract_data:
        st.subheader("Contract Metadata")
        st.write(f"**Name:** {st.session_state.contract_data['streamer_legal_name']}")
        st.write(f"**Duration:** {st.session_state.contract_data['contract_months']} months")
        if st.session_state.contract_data["fee_type"] == "Fixed %":
            st.write(f"**Fee structure:** Fixed {st.session_state.contract_data['fee_percentage']}%")
        else:
            st.write("**Fee structure:** Dynamic")
        st.write(f"**Status:** {st.session_state.signing_status}")


with right:
    st.subheader("PDF Preview")
    preview_pdf = st.session_state.signed_pdf or st.session_state.generated_pdf
    if preview_pdf:
        preview_rendered = False
        if hasattr(st, "pdf"):
            try:
                st.pdf(preview_pdf)
                preview_rendered = True
            except StreamlitAPIException:
                preview_rendered = False

        if not preview_rendered:
            b64 = base64.b64encode(preview_pdf).decode("utf-8")
            st.components.v1.html(
                f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="700" type="application/pdf"></iframe>',
                height=700,
            )
    else:
        st.info("Generate a contract to preview it here.")


st.markdown("---")
st.subheader("Signature")

if st.session_state.generated_pdf is None:
    st.info("Signing is disabled until a contract is generated.")
else:
    sig_option = st.radio("Choose signature method", ["Draw", "Upload", "Type"], horizontal=True)

    if sig_option == "Draw":
        canvas_result = st_canvas(
            stroke_width=3,
            stroke_color="#111111",
            background_color="#ffffff",
            height=200,
            width=600,
            drawing_mode="freedraw",
            key="signature_canvas",
        )
        if canvas_result.image_data is not None:
            from PIL import Image
            import io

            img = Image.fromarray((canvas_result.image_data).astype("uint8"), mode="RGBA")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.session_state.signature_image = normalize_signature_image(buf.getvalue())

    elif sig_option == "Upload":
        upload = st.file_uploader("Upload signature PNG", type=["png"])
        if upload is not None:
            st.session_state.signature_image = normalize_signature_image(upload.getvalue())

    else:
        typed_name = st.text_input("Type your signature", key="typed_signature")
        if typed_name.strip():
            st.session_state.signature_image = typed_signature_to_png_bytes(typed_name.strip())

    sign_disabled = st.session_state.signature_image is None
    if st.button("Sign Contract", disabled=sign_disabled):
        st.session_state.signed_pdf = apply_signature_to_pdf(st.session_state.generated_pdf, st.session_state.signature_image)
        st.session_state.signing_status = "Signed"
        save_contract_record(
            st.session_state.contract_data,
            st.session_state.generated_pdf,
            st.session_state.signature_image,
            st.session_state.signed_pdf,
        )
        st.success("Contract signed successfully.")


st.markdown("---")
st.subheader("Downloads")

unsigned_disabled = st.session_state.generated_pdf is None
signed_disabled = st.session_state.signed_pdf is None

st.download_button(
    "Download Unsigned Contract",
    data=st.session_state.generated_pdf or b"",
    file_name="HyperChat_Streamer_Agreement_unsigned.pdf",
    mime="application/pdf",
    disabled=unsigned_disabled,
)
st.download_button(
    "Download Signed Contract",
    data=st.session_state.signed_pdf or b"",
    file_name="HyperChat_Streamer_Agreement_signed.pdf",
    mime="application/pdf",
    disabled=signed_disabled,
)
