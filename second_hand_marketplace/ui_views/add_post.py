import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database import conn, create_connection
import mysql.connector

def show_add_product_window(app):
    # 사용자가 로그인했는지 확인
    if not hasattr(app, 'current_user_id') or not app.current_user_id:
        messagebox.showerror("Error", "Please log in to add a product.")
        return

    user_id = app.current_user_id  # 로그인된 UserID 가져오기

    # "Add Post" 생성
    add_post_window = tk.Toplevel(app)
    add_post_window.title("Add Post")
    add_post_window.geometry("600x800")
    add_post_window.configure(bg="#ffffff")  

   
    tk.Label(add_post_window, text="Add Post", font=("Comic Sans MS", 24, "bold"), bg="#ff7f0e", fg="#ffffff").pack(
        pady=20, fill="x"
    )

    
    form_frame = tk.Frame(add_post_window, bg="#ffffff")
    form_frame.pack(pady=10, padx=20, fill="both", expand=True)

    fields = ["Title", "Category", "Price", "Description", "Main Photo"]
    entries = {}

    for field in fields:
        tk.Label(form_frame, text=f"{field}:", font=("Comic Sans MS", 14)).pack(anchor="w", pady=5)
        if field == "Category":
            category_var = tk.StringVar(value="Select Category")
            category_dropdown = ttk.Combobox(
                form_frame,
                textvariable=category_var,
                values=["Electronics", "Furniture", "Appliances", "Toys", "Others"],
                state="readonly"
            )
            category_dropdown.pack(fill="x", pady=5)
            entries[field] = category_var
        elif field == "Main Photo":
            photo_entry = tk.Entry(form_frame, font=("Comic Sans MS", 12))
            photo_entry.pack(fill="x", pady=5)

            def browse_photo():
                file_path = filedialog.askopenfilename(
                    title="Select Main Photo",
                    filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif"), ("All Files", "*.*")]
                )
                photo_entry.delete(0, tk.END)
                photo_entry.insert(0, file_path)

            tk.Button(form_frame, text="Browse", command=browse_photo).pack(pady=5)
            entries[field] = photo_entry
        elif field == "Description":
            description_entry = tk.Text(form_frame, font=("Comic Sans MS", 12), height=5)
            description_entry.pack(fill="x", pady=5)
            entries[field] = description_entry
        else:
            entry = tk.Entry(form_frame, font=("Comic Sans MS", 12))
            entry.pack(fill="x", pady=5)
            entries[field] = entry

    def submit_post():
        # 로그인된 사용자 가져오기
        user_id = app.current_user_id
        if not user_id:
            messagebox.showerror("Error", "Please log in to add a post.")
            return

        # 게시물 세부 정보 수집
        post_data = {
            "Title": entries["Title"].get(),
            "Category": entries["Category"].get(),
            "Price": int(entries["Price"].get()) if entries["Price"].get().isdigit() else None,
            "Description": entries["Description"].get("1.0", tk.END).strip(),
            "MainPhoto": entries["Main Photo"].get(),
            "UserID": user_id  # 로그인된 사용자의 ID 사용
        }

        if not all(post_data.values()):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # 사용자의 PrimaryNeighborhood 가져오기
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT PrimaryNeighborhood FROM users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            if not user or not user["PrimaryNeighborhood"]:
                messagebox.showerror("Error", "User's neighborhood could not be found.")
                return

            post_data["Neighborhood"] = user["PrimaryNeighborhood"]

            # 게시물 데이터베이스에 삽입
            cursor.execute("""
                INSERT INTO Post (UserID, Title, Category, Price, Description, MainPhoto, Status, LikesCount, Neighborhood)
                VALUES (%s, %s, %s, %s, %s, %s, 'Available', 0, %s)
            """, (
                post_data["UserID"],
                post_data["Title"],
                post_data["Category"],
                post_data["Price"],
                post_data["Description"],
                post_data["MainPhoto"],
                post_data["Neighborhood"]
            ))
            conn.commit()
            messagebox.showinfo("Success", "Post added successfully!")
            add_post_window.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
            conn.rollback()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please check your data.")
        finally:
            if cursor:
                cursor.close()

    tk.Button(add_post_window, text="Submit", font=("Segoe UI", 14), command=submit_post).pack(pady=20)

    add_post_window.mainloop()
