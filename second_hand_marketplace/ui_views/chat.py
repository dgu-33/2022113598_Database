import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import messagebox
from database import conn
import mysql.connector

def ensure_connection():
    global conn
    if conn is None or not conn.is_connected():
        conn.reconnect(attempts=3, delay=2)



def open_chat_window(post_id, current_user_id, other_user_id):
    """주어진 게시물과 참여자를 위한 채팅 창을 엽니다."""
    try:
        # 데이터베이스 연결이 활성 상태인지 확인
        ensure_connection()

        cursor = conn.cursor(dictionary=True)

        # 채팅 창 열기
        chat_window = tk.Toplevel()
        chat_window.title("Chat")
        chat_window.geometry("600x400")
        

        # 채팅 표시 영역
        chat_display = tk.Text(chat_window, state='disabled', wrap='word')
        chat_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 이전 메시지 가져오기
        cursor.execute("""
        SELECT 
            c.Message, 
            c.Timestamp, 
            s.Nickname AS SenderNickname
        FROM Chats c
        JOIN users s ON c.SenderID = s.UserID
        WHERE c.PostID = %s 
          AND ((c.SenderID = %s AND c.ReceiverID = %s) 
               OR (c.SenderID = %s AND c.ReceiverID = %s))
        ORDER BY c.Timestamp;
        """, (post_id, current_user_id, other_user_id, other_user_id, current_user_id))
        messages = cursor.fetchall()

         # 채팅 표시를 채우기
        chat_display.config(state='normal')
        for msg in messages:
            chat_display.insert('end', f"{msg['SenderNickname']} ({msg['Timestamp']}): {msg['Message']}\n")
        chat_display.config(state='disabled')

         # 입력 필드 및 전송 버튼
        input_frame = tk.Frame(chat_window)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        message_var = tk.StringVar()

        def send_message():
            """메시지 전송을 처리합니다."""
            try:
                
                ensure_connection()

                
                cursor = conn.cursor(dictionary=True)
                message_text = message_var.get().strip()

                if not message_text:
                    messagebox.showerror("Error", "Message cannot be empty.")
                    return

                 # Chats 테이블에 새 메시지 삽입
                cursor.execute("""
                INSERT INTO Chats (SenderID, ReceiverID, PostID, Message)
                VALUES (%s, %s, %s, %s)
                """, (current_user_id, other_user_id, post_id, message_text))
                conn.commit()

                # 새 메시지로 채팅 표시 업데이트
                chat_display.config(state='normal')
                chat_display.insert('end', f"You: {message_text}\n")
                chat_display.config(state='disabled')
                message_var.set("") 
            except mysql.connector.Error as db_err:
                messagebox.showerror("Database Error", f"Database error: {db_err}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")
            finally:
                if cursor:
                    cursor.close()

        tk.Entry(input_frame, textvariable=message_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Button(input_frame, text="Send", command=send_message).pack(side=tk.RIGHT)

    except mysql.connector.Error as db_err:
        messagebox.showerror("Database Error", f"Database error: {db_err}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open chat: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

