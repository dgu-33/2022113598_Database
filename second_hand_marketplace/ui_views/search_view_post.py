import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chat import open_chat_window
from review import leave_review
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import conn
import mysql.connector


def search_posts(tree, title_var, neighborhood_var, category_var, min_price_var, max_price_var, status_var, likes_var):
    """제공된 필터를 사용하여 게시물을 검색합니다."""
    cursor = None
    try:
        if conn is None:
            raise Exception("Database connection is not established.")

        cursor = conn.cursor(dictionary=True)

        # 필터 값 가져오기
        title = title_var.get()
        neighborhood = neighborhood_var.get()
        category = category_var.get()
        min_price = int(min_price_var.get()) if min_price_var.get().isdigit() else 0
        max_price = int(max_price_var.get()) if max_price_var.get().isdigit() else 999999
        status = status_var.get()
        min_likes = int(likes_var.get()) if likes_var.get().isdigit() else 0

        # SQL 쿼리: 필터 조건에 따라 게시물 검색
        query = """
        SELECT PostID, Title, Price, Status, LikesCount, Category, Neighborhood, PostDate
        FROM Post
        WHERE 1=1
          AND (Title LIKE %s OR %s = '')
          AND (%s = 'All' OR Category = %s)  -- Simplified condition for "All" or specific category
          AND (Neighborhood = %s OR %s = '')
          AND (Price BETWEEN %s AND %s)
          AND (%s = 'All' OR Status = %s)  -- "All" or specific status
          AND (LikesCount >= %s);
        """
        
        params = (
            f"%{title}%", title,  
            category, category,  
            neighborhood, neighborhood,  
            min_price, max_price,  
            status, status,  
            min_likes, 
        )

        cursor.execute(query, params)
        results = cursor.fetchall()

        # TreeView의 기존 행 삭제
        for row in tree.get_children():
            tree.delete(row)

        # TreeView에 결과 추가
        for post in results:
            tree.insert("", "end", values=(
                post["PostID"], post["Title"], post["Price"], post["Status"], post["LikesCount"],
                post["Category"], post["Neighborhood"], post["PostDate"]
            ))
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        if cursor:
            cursor.close()




def show_post_details(event, current_user_id):
    """Treeview에서 항목을 더블 클릭했을 때 게시물 세부 정보를 표시합니다."""
    tree = event.widget
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No post selected.")
        return

    # TreeView에서 게시물 데이터 가져오기
    post = tree.item(selected_item[0], "values")
    try:
        post_id = post[0]  # PostID는 첫 번째 열
        title = post[1]
        price = post[2]
        status = post[3]
        likes = post[4]
        category = post[5]
        neighborhood = post[6]
    except IndexError:
        messagebox.showerror("Error", "Post data is incomplete.")
        return

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # 게시물 세부 정보 가져오는 SQL 쿼리
        query = "SELECT Description, MainPhoto, LikesCount, UserID FROM Post WHERE PostID = %s"
        cursor.execute(query, (post_id,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Post details not found.")
            return
        
         # 게시물 정보 가져오기
        description = result.get("Description", "No description available.")
        main_photo = result.get("MainPhoto", None)
        likes_count = result.get("LikesCount", 0)
        post_owner_id = result.get("UserID")

        # 이미지 경로 구성
        image_folder = r"C:\Users\지동우\Documents\second_hand_marketplace\ui_views\product_images"
        image_path = os.path.join(image_folder, main_photo) if main_photo else None

        # 세부 정보 창 생성
        detail_window = tk.Toplevel(event.widget)
        detail_window.title(f"Details: {title}")
        detail_window.geometry("700x900")
        detail_window.configure(bg="#ffffff")   
        
        
         # 헤더
        header_frame = tk.Frame(detail_window, bg="#ff7f0e", height=80)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Post Details", font=("Comic Sans MS", 20, "bold"), bg="#ff7f0e", fg="#ffffff").pack(pady=20)

        if main_photo and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((300, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                tk.Label(detail_window, image=photo).pack(pady=10)
                detail_window.photo = photo
            except Exception:
                tk.Label(detail_window, text="Error loading photo.", font=("Comic Sans MS", 12)).pack(pady=10)
        else:
            tk.Label(detail_window, text="Photo not available.", font=("Comic Sans MS", 12)).pack(pady=10)
           
        # 세부 정보 목록
        details = {
            "Title": title,
            "Price": f"${price}",
            "Status": status,
            "Likes": likes_count,
            "Category": category,
            "Neighborhood": neighborhood,
            "Description": description,
        }

        for key, value in details.items():
            tk.Label(detail_window, text=f"{key}: {value}", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)

        # 사용자 소유권 확인 및 버튼 설정
        if post_owner_id == current_user_id:
            # 사용자가 게시물의 소유자인 경우 "Edit Post" 버튼 표시
            def edit_post():
                """Open the Edit Post window."""
                open_edit_post_window(current_user_id, post_id, title, price, status, description, main_photo, category)

            tk.Button(detail_window, text="Edit Post", command=edit_post).pack(pady=10)
        else:
            # 다른 사용자의 경우 "Send Message" 및 "Like" 버튼 표시
            def send_message():
                """게시물 소유자와의 채팅 창 열기."""
                if not current_user_id:
                    messagebox.showerror("Error", "You must be logged in to send a message.")
                    return
                open_chat_window(post_id, current_user_id, post_owner_id)

            def like_product():
                """게시물 좋아요 상태 토글."""
                if not current_user_id:
                    messagebox.showerror("Error", "You must be logged in to leave a like!")
                    return
                try:
                    # 사용자가 이미 이 게시물에 좋아요를 눌렀는지 확인
                    toggle_cursor = conn.cursor(dictionary=True)
                    toggle_cursor.execute("SELECT * FROM UserLikes WHERE UserID = %s AND PostID = %s",
                                          (current_user_id, post_id))
                    liked = toggle_cursor.fetchone()

                    if liked:
                        # 이미 좋아요를 누른 경우 -> 좋아요 취소
                        toggle_cursor.execute("DELETE FROM UserLikes WHERE UserID = %s AND PostID = %s",
                                              (current_user_id, post_id))   # UserLikes 테이블에서 삭제
                        conn.commit()
                        
                         # Post 테이블에서 LikesCount 감소
                        toggle_cursor.execute("UPDATE Post SET LikesCount = LikesCount - 1 WHERE PostID = %s", (post_id,))
                        conn.commit()
                        
                        # 성공 메시지 표시
                        messagebox.showinfo("Unliked", f"You unliked {title}.")
                        
                         # 버튼 텍스트를 "Like"로 변경
                        like_button.config(text="Like")  
                    else:
                        # 아직 좋아요를 누르지 않은 경우 -> 좋아요 추가
                        toggle_cursor.execute("INSERT INTO UserLikes (UserID, PostID) VALUES (%s, %s)",
                                              (current_user_id, post_id))
                        conn.commit()
                        
                        # Post 테이블에서 LikesCount 증가
                        toggle_cursor.execute("UPDATE Post SET LikesCount = LikesCount + 1 WHERE PostID = %s", (post_id,))
                        conn.commit()
                        
                        # 성공 메시지 표시 
                        messagebox.showinfo("Liked", f"You liked {title}!")
                        
                        # 버튼 텍스트를 "Unlike"로 변경
                        like_button.config(text="Unlike")  
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to toggle like status: {e}")
                finally:
                    if toggle_cursor:
                        toggle_cursor.close()

            tk.Button(detail_window, text="Send Message", command=send_message).pack(pady=10)
            like_button = tk.Button(detail_window, text="Like", command=like_product)
            like_button.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load post details: {e}")
    finally:
        if cursor:
            cursor.close()

def open_edit_post_window(current_user_id, post_id, title, price, status, description, main_photo, category):
    """게시물 세부 정보를 편집할 수 있는 창 열기."""
    edit_window = tk.Toplevel()
    edit_window.title("Edit Post")
    edit_window.geometry("500x700")

    tk.Label(edit_window, text="Edit Post", font=("Comic Sans MS", 18, "bold")).pack(pady=10)

    
    status_choices = ["Available", "Reserved", "Sold"]
    category_choices = ["Appliances", "Electronics", "Toys", "Furniture"]

    
    fields = {
        "Title": title,
        "Price": price,
        "Description": description,
        "MainPhoto": main_photo,
    }
    entries = {}

    for key, value in fields.items():
        tk.Label(edit_window, text=key, font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
        entry = tk.Entry(edit_window, font=("Comic Sans MS", 12))
        entry.insert(0, value)
        entry.pack(fill=tk.X, padx=20)
        entries[key] = entry

    
    tk.Label(edit_window, text="Status", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
    status_var = tk.StringVar(value=status)
    status_dropdown = ttk.Combobox(edit_window, textvariable=status_var, values=status_choices, state="readonly")
    status_dropdown.pack(fill=tk.X, padx=20)

    
    tk.Label(edit_window, text="Category", font=("Comic Sans MS", 12)).pack(anchor="w", padx=20, pady=5)
    category_var = tk.StringVar(value=category)
    category_dropdown = ttk.Combobox(edit_window, textvariable=category_var, values=category_choices, state="readonly")
    category_dropdown.pack(fill=tk.X, padx=20)

    def save_changes():
        """데이터베이스에 변경 사항 저장."""
        updated_values = {key: entry.get().strip() for key, entry in entries.items()}
        updated_values["Status"] = status_var.get()
        updated_values["Category"] = category_var.get()

        try:
            cursor = conn.cursor(dictionary=True)  

            # 상태가 'Sold'로 변경된 경우 거래를 추가
            if updated_values["Status"] == "Sold":
                # 판매자에게 구매자 닉네임 입력 요청
                buyer_nickname = tk.simpledialog.askstring("Buyer Nickname", "Enter the Buyer's Nickname:")
                if not buyer_nickname:
                    messagebox.showerror("Error", "Buyer nickname is required to mark this post as sold.")
                    return

                 # 구매자 닉네임 확인 및 UserID 가져오기
                cursor.execute("SELECT UserID FROM users WHERE Nickname = %s", (buyer_nickname,))
                buyer_data = cursor.fetchone()  # 첫 번째 결과만 가져오기

                if not buyer_data:
                    messagebox.showerror("Error", f"Buyer with nickname '{buyer_nickname}' does not exist.")
                    return

                buyer_id = buyer_data["UserID"]  # UserID 추출

               # Transactions 테이블에 데이터 추가
                cursor.execute("""
                    INSERT INTO Transactions (PostID, SellerID, BuyerID)
                    VALUES (%s, %s, %s)
                """, (post_id, current_user_id, buyer_id))
                conn.commit()

                # 거래 생성 성공 메시지
                messagebox.showinfo("Transaction Created", f"Transaction with Buyer '{buyer_nickname}' has been saved.")

             # Post 테이블의 게시물 세부 정보 업데이트
            cursor.execute("""
                UPDATE Post 
                SET Title = %s, Price = %s, Status = %s, Description = %s, MainPhoto = %s, Category = %s
                WHERE PostID = %s
            """, (updated_values["Title"], updated_values["Price"], updated_values["Status"],
                updated_values["Description"], updated_values["MainPhoto"], updated_values["Category"], post_id))
            conn.commit()
            messagebox.showinfo("Success", "Post updated successfully!")
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update post: {e}")
        finally:
            if cursor:
                cursor.close()




    def delete_post():
        """데이터베이스에서 게시물 삭제."""
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this post?")
        if not confirm:
            return
        try:
            cursor = conn.cursor()
             # 'Post' 테이블에서 게시물 삭제
            cursor.execute("DELETE FROM Post WHERE PostID = %s", (post_id,))
            conn.commit()
            messagebox.showinfo("Success", "Post deleted successfully!")
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete post: {e}")
        finally:
            if cursor:
                cursor.close()

   
    tk.Button(edit_window, text="Save Changes", command=save_changes).pack(pady=10)
    tk.Button(edit_window, text="Delete Post", command=delete_post).pack(pady=10)

        