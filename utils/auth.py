import streamlit as st
import requests

def login():
    st.subheader("Login")
    username = st.text_input("Username", "")
    password = st.text_input("Password", "", type="password")
    
    if st.button("Login"):
        response = requests.post(
            "http://127.0.0.1:5000/login", 
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            st.session_state["logged_in"] = True
            st.success("Login successful!")
            return True
        else:
            st.error("Invalid credentials")
    return st.session_state.get("logged_in", False)

def register():
    st.subheader("Register")
    new_username = st.text_input("New Username", "")
    new_password = st.text_input("New Password", "", type="password")
    new_email = st.text_input("Email", "")
    
    if st.button("Register"):
        response = requests.post(
            "http://127.0.0.1:5000/register", 
            json={
                "username": new_username, 
                "password": new_password,
                "email": new_email
            }
        )
        if response.status_code == 201:
            st.success("Registration successful! You can now log in.")
        else:
            st.error("Registration failed. Try a different username.")