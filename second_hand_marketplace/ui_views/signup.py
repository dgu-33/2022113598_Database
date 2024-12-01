import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
import tkinter as tk
from tkinter import messagebox
from database import conn, create_connection  
import mysql.connector



def validate_inputs(user_data):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'      
    if not re.match(email_pattern, user_data["Email"]):          # 이메일이 올바른 형식인지 확인
        messagebox.showerror("Error", "Invalid email format.")
        return False
    if not user_data["Phone Number"].isdigit():             # 전화번호가 숫자인지 확인
        messagebox.showerror("Error", "Phone Number must contain only digits.")
        return False
    return True



def show_signup_window(app):
    """회원가입 창을 표시."""
    signup_window = tk.Toplevel(app)
    signup_window.title("Sign Up")
    signup_window.geometry("600x800")  
    signup_window.configure(bg="#ffffff")  

    
    header_frame = tk.Frame(signup_window, bg="#ff7f0e", height=100)
    header_frame.pack(fill="x")
    tk.Label(
        header_frame, text="Sign Up", font=("Comic Sans MS", 24, "bold"), bg="#ff7f0e", fg="#ffffff"
    ).pack(pady=20)
    

    
    form_frame = tk.Frame(signup_window)
    form_frame.pack(pady=10, padx=20, fill="both", expand=True)

     # 입력 필드 정의
    fields = [
        "UserID",
        "Password",
        "Name",
        "Age",
        "Nickname",
        "Email",
        "Phone Number",
        "Primary Neighborhood"
    ]

    entries = {}  
    for field in fields:
        tk.Label(form_frame, text=f"{field}:", font=("Comic Sans MS", 14), bg="#ffffff", fg="#333333").pack(anchor="w", pady=5)
        entry = tk.Entry(form_frame, font=("Comic Sans MS", 12), bg="#f8f8f8", fg="#333333")
        entry.pack(fill="x", pady=5)
        entries[field] = entry

   
    entries["Password"].config(show="*")

  

    def reconnect_db():
        global conn
        if conn is None or not conn.is_connected():
            conn = create_connection()
        return conn is not None



    def submit_signup():
            """회원가입 양식 제출."""
            user_data = {field: entry.get() for field, entry in entries.items()}
            if not all(user_data.values()):
                messagebox.showerror("Error", "All fields must be filled!")
                return
            try:
                user_data["Age"] = int(user_data["Age"])
            except ValueError:
                messagebox.showerror("Error", "Age must be a number.")
                return
            if not validate_inputs(user_data):
                return
           
            if not reconnect_db():
                messagebox.showerror("Error", "Database connection error.")
                return
            try:
                if insert_user_data(user_data):
                    messagebox.showinfo("Success", "Sign Up successful!")
                    signup_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Sign up failed: {e}")
                
                
    tk.Button(
        form_frame,
        text="Submit",
        font=("Comic Sans MS", 14, "bold"),
        bg="#ff7f0e",
        fg="#ffffff",
        command=submit_signup,
    ).pack(pady=20)

    
    footer_frame = tk.Frame(signup_window, bg="#ff7f0e", height=50)
    footer_frame.pack(fill="x")
    tk.Label(
        footer_frame, text="Welcome to 동국 중고 마켓!", font=("Comic Sans MS", 12), bg="#ff7f0e", fg="#ffffff"
    ).pack(pady=10)

 
    def insert_user_data(user_data):
        """사용자 데이터를 데이터베이스에 삽입."""
        cursor = None
        try:
            cursor = conn.cursor()
            # SQL 쿼리: 사용자를 users 테이블에 삽입
            cursor.execute("""
                INSERT INTO users (UserID, Password, Name, Age, Nickname, Email, PhoneNumber, PrimaryNeighborhood)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_data["UserID"], user_data["Password"], user_data["Name"], user_data["Age"],
                user_data["Nickname"], user_data["Email"], user_data["Phone Number"],
                user_data["Primary Neighborhood"]
            ))
            conn.commit()
            return True
        finally:
            if cursor:
                cursor.close()


    tk.Button(signup_window, text="Submit", font=("Segoe UI", 14), command=submit_signup).pack(pady=20)

    signup_window.mainloop()