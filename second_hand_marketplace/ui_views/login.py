import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox
from database import conn  

def show_login_window(app):
    # 로그인 창 생성
    login_window = tk.Toplevel(app)
    login_window.title("Log In")
    login_window.geometry("400x400")
    login_window.configure(bg="#ffffff")
    
    
    # ID 레이블 및 입력 필드
    tk.Label(login_window, text="ID:").pack(pady=5)
    ID_entry = tk.Entry(login_window)
    ID_entry.pack(pady=5)

    # 비밀번호 레이블 및 입력 필드
    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")  # 비밀번호 입력 숨기기
    password_entry.pack(pady=5)

     
    def login():                   # 로그인 동작을 처리하는 함수
        ID = ID_entry.get()
        password = password_entry.get()

        if not ID or not password:
            messagebox.showerror("Error", "Both ID and Password are required!")
            return

        cursor = conn.cursor()
        try:
            
            print(f"ID: {ID}, Password: {password}")

           # 자격 증명 유효성을 확인하는 쿼리
            cursor.execute("""
                SELECT UserID, Password FROM users
                WHERE UserID = %s OR Email = %s OR PhoneNumber = %s
            """, (ID, ID, ID))

            user = cursor.fetchone()
            print(f"User Retrieved: {user}")  # 디버그 메시지

            if user and password == user[1]:  # 비밀번호 일치 확인
                app.current_user_id = user[0]  # 로그인된 UserID 저장
                messagebox.showinfo("Success", f"Welcome, {user[0]}!")
                login_window.destroy()
                
                # 메뉴 상태 업데이트
                app.update_account_menu()
            else:
                messagebox.showerror("Error", "Invalid ID or Password.")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            print(f"Database error: {e}")  
        finally:
            cursor.close()

    
     # 버튼 섹션
    button_frame = tk.Frame(login_window, bg="#ffffff")
    button_frame.pack(pady=20)

    tk.Button(
        button_frame,
        text="Log In",
        font=("Comic Sans MS", 14, "bold"),
        bg="#ff7f0e",
        fg="#ffffff",
        width=15,
        command=login
    ).pack(pady=10)

    tk.Button(
        button_frame,
        text="Cancel",
        font=("Comic Sans MS", 14, "bold"),
        bg="#ffffff",
        fg="#ff7f0e",
        width=15,
        command=login_window.destroy,
    ).pack(pady=10)