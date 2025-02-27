# main.py
import streamlit as st
import requests
from utils.model import load_model, detect_skin_disease
from utils.image_processing import preprocess_image
from utils.auth import login, register
from PIL import Image

def main():
    st.title("Skin Disease Detection using YOLO")
    
    menu = ["Login", "Register", "Detection"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    # Kiểm tra đăng nhập
    if choice == "Login":
        login()
        return
    elif choice == "Register":
        register()
        return
    
    # Kiểm tra trạng thái đăng nhập trước khi cho phép sử dụng features
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in to use this feature")
        st.stop()
    
    # Chỉ hiện features khi đã đăng nhập
    model = load_model()
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        processed_image = preprocess_image(image)
        results = detect_skin_disease(model, processed_image)
        
        st.image(results, caption="Detection Result", use_column_width=True)

if __name__ == "__main__":
    main()
