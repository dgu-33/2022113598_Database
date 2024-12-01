import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chat import open_chat_window
import tkinter as tk
from tkinter import ttk, messagebox
from ui_views.search_view_post import show_post_details
from database import conn  # Ensure this connects to your MySQL database


def show_profile(app):
    """로그인한 사용자의 프로필을 오렌지와 흰색의 모던 디자인으로 표시합니다."""
    if not app.current_user_id:
        messagebox.showerror("Error", "You must be logged in to view your profile.")
        return

    profile_window = tk.Toplevel(app)
    profile_window.title("Profile")
    profile_window.geometry("800x600")
    profile_window.configure(bg="#ffffff")  

    
    canvas = tk.Canvas(profile_window, bg="#ffffff", highlightthickness=0)
    scrollbar = ttk.Scrollbar(profile_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#ffffff")  

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", configure_scroll_region)

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        # SQL 쿼리: 사용자의 기본 정보 가져오기
        cursor.execute("""
            SELECT Nickname, Email, PhoneNumber, TransactionSatisfaction, PrimaryNeighborhood
            FROM users
            WHERE UserID = %s
        """, (app.current_user_id,))
        user = cursor.fetchone()
        if not user:
            messagebox.showerror("Error", "Failed to retrieve user information.")
            return

        # 사용자 정보 섹션
        details_frame = tk.Frame(scrollable_frame, bg="#ff7f0e", bd=2, relief="groove")  
        details_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            details_frame, text="User Profile", font=("Comic Sans MS", 18, "bold"),
            bg="#ff7f0e", fg="#ffffff"  
        ).pack(anchor="w", padx=10, pady=(10, 5))

        user_details = [
            f"Nickname: {user['Nickname']}",
            f"Email: {user['Email']}",
            f"Phone Number: {user['PhoneNumber']}",
            f"Transaction Satisfaction: {user['TransactionSatisfaction']}/5",
            f"Primary Neighborhood: {user['PrimaryNeighborhood']}"
        ]

        for detail in user_details:
            tk.Label(
                details_frame, text=detail, font=("Comic Sans MS", 12),
                bg="#ff7f0e", fg="#ffffff"
            ).pack(anchor="w", padx=10, pady=2)

        # 거래 버튼
        tk.Button(
            details_frame, text="Your Transactions", command=lambda: show_transactions(app),
            font=("Comic Sans MS", 12, "bold"), bg="#ffffff", fg="#ff7f0e", bd=0, padx=10, pady=5
        ).pack(pady=10, padx=10, anchor="w")

        # 리뷰 섹션
        tk.Label(
            scrollable_frame, text="Reviews You Received", font=("Comic Sans MS", 16, "bold"),
            bg="#ffffff", fg="#ff7f0e"
        ).pack(anchor="w", padx=20, pady=10)

        # SQL 쿼리: 받은 리뷰 가져오기
        cursor.execute("""
            SELECT 
                r.ReviewContent, 
                r.TransactionSatisfaction, 
                u.Nickname AS AuthorNickname
            FROM Review r
            JOIN users u ON r.AuthorID = u.UserID
            WHERE r.TargetID = %s
        """, (app.current_user_id,))
        received_reviews = cursor.fetchall()

        # 리뷰 표시
        if received_reviews:
            for review in received_reviews:
                review_frame = tk.Frame(scrollable_frame, bg="#ffffff", bd=1, relief="solid")
                review_frame.pack(fill="x", padx=20, pady=5)

                tk.Label(
                    review_frame, text=f"From: {review['AuthorNickname']}",
                    font=("Comic Sans MS", 12, "bold"), bg="#ffffff", fg="#ff7f0e"
                ).pack(anchor="w", padx=10, pady=5)

                tk.Label(
                    review_frame, text=f"Satisfaction: {review['TransactionSatisfaction']}/5",
                    font=("Comic Sans MS", 11), bg="#ffffff", fg="#555555"
                ).pack(anchor="w", padx=10, pady=2)

                tk.Label(
                    review_frame, text=f"Review: {review['ReviewContent']}",
                    font=("Comic Sans MS", 11, "italic"), bg="#ffffff", fg="#333333"
                ).pack(anchor="w", padx=10, pady=5)
        else:
            tk.Label(
                scrollable_frame, text="No reviews received.", font=("Comic Sans MS", 11, "italic"),
                bg="#ffffff", fg="#777777"
            ).pack(anchor="w", padx=20, pady=5)

        # 사용자가 작성한 게시물 섹션
        tk.Label(
            scrollable_frame, text="Your Posts", font=("Comic Sans MS", 16, "bold"),
            bg="#ffffff", fg="#ff7f0e"
        ).pack(anchor="w", padx=20, pady=10)

        posts_tree = ttk.Treeview(
            scrollable_frame, columns=("PostID", "Title", "Price", "Status", "Likes", "Category", "Neighborhood"),
            show="headings", height=10
        )
        posts_tree.heading("PostID", text="PostID")
        posts_tree.heading("Title", text="Title")
        posts_tree.heading("Price", text="Price")
        posts_tree.heading("Status", text="Status")
        posts_tree.heading("Likes", text="Likes")
        posts_tree.heading("Category", text="Category")
        posts_tree.heading("Neighborhood", text="Neighborhood")

        
        style = ttk.Style()
        style.configure("Treeview", font=("Comic Sans MS", 11))
        style.configure("Treeview.Heading", font=("Comic Sans MS", 12, "bold"))

         # SQL 쿼리: 사용자가 작성한 게시물 가져오기
        cursor.execute("""
            SELECT PostID, Title, Price, Status, LikesCount AS Likes, Category, Neighborhood
            FROM Post
            WHERE UserID = %s
        """, (app.current_user_id,))
        posts = cursor.fetchall()
        for post in posts:
            posts_tree.insert("", "end", values=(
                post["PostID"], post["Title"], post["Price"], post["Status"],
                post["Likes"], post["Category"], post["Neighborhood"]
            ))

        posts_tree.pack(fill="x", padx=20, pady=5)

        def on_post_double_click(event):
            selected_item = posts_tree.selection()
            if not selected_item:
                return
            show_post_details(event, app.current_user_id)

        posts_tree.bind("<Double-1>", on_post_double_click)

        # 채팅 섹션
        tk.Label(
            scrollable_frame, text="Your Chatrooms", font=("Comic Sans MS", 16, "bold"),
            bg="#ffffff", fg="#ff7f0e"
        ).pack(anchor="w", padx=20, pady=10)

        unique_post_ids = set()

        # SQL 쿼리: 채팅 기록에서 PostID 가져오기
        cursor.execute("""
            SELECT DISTINCT PostID, ReceiverID, SenderID
            FROM Chats
            WHERE SenderID = %s OR ReceiverID = %s
        """, (app.current_user_id, app.current_user_id))
        chats = cursor.fetchall()

        # 채팅 버튼 표시
        if chats:
            for chat in chats:
                post_id = chat['PostID']
                if post_id not in unique_post_ids:
                    unique_post_ids.add(post_id)
                    other_user_id = chat['ReceiverID'] if chat['ReceiverID'] != app.current_user_id else chat['SenderID']
                    tk.Button(
                        scrollable_frame,
                        text=f"Chat on Post {post_id}",
                        command=lambda post_id=post_id, other_user_id=other_user_id: open_chat_window(post_id, app.current_user_id, other_user_id),
                        font=("Comic Sans MS", 11), bg="#ff7f0e", fg="#ffffff", bd=0, padx=10, pady=5
                    ).pack(anchor="w", padx=30, pady=2)
        else:
            tk.Label(
                scrollable_frame, text="No chats found.", font=("Comic Sans MS", 11, "italic"),
                bg="#ffffff", fg="#777777"
            ).pack(anchor="w", padx=30, pady=5)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load profile: {e}")
    finally:
        if cursor:
            cursor.close()


            
def show_transactions(app):
    from review import leave_review
    """로그인된 사용자의 거래 내역(판매자와 구매자 모두)을 표시합니다."""
    if not app.current_user_id:
        messagebox.showerror("Error", "You must be logged in to view your transactions.")
        return

    transactions_window = tk.Toplevel(app)
    transactions_window.title("Your Transactions")
    transactions_window.geometry("600x400")

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 거래 내역을 가져오는 SQL 쿼리
        cursor.execute("""
            SELECT 
                t.TransactionID, 
                t.PostID, 
                t.SellerID, 
                t.BuyerID, 
                p.Title, 
                CASE 
                    WHEN t.SellerID = %s THEN 'Seller'
                    WHEN t.BuyerID = %s THEN 'Buyer'
                END AS Role,
                (SELECT COUNT(*) FROM Review r 
                 WHERE r.TransactionID = t.TransactionID 
                 AND r.AuthorID = %s) AS ReviewExists
            FROM Transactions t
            JOIN Post p ON t.PostID = p.PostID
            WHERE t.SellerID = %s OR t.BuyerID = %s
        """, (app.current_user_id, app.current_user_id, app.current_user_id, app.current_user_id, app.current_user_id))
        transactions = cursor.fetchall()

        tk.Label(transactions_window, text="Your Transactions", font=("Comic Sans MS", 16)).pack(pady=10)

        if transactions:
            for transaction in transactions:
                role = transaction['Role']  # 사용자의 역할(판매자/구매자)
                review_exists = transaction['ReviewExists'] > 0 # 리뷰 작성 여부 확인

                if review_exists:
                    # 리뷰가 이미 작성된 경우 텍스트 표시
                    tk.Label(
                        transactions_window, 
                        text=f"{transaction['Title']} ({role}) - Review Submitted", 
                        font=("Comic Sans MS", 10, "italic")
                    ).pack(pady=5)
                else:
                    # 리뷰가 작성되지 않은 경우 "Leave Review" 버튼 생성
                    tk.Button(
                        transactions_window, 
                        text=f"{transaction['Title']} ({role}) - Leave Review", 
                        command=lambda t=transaction: leave_review(
                            t["TransactionID"],
                            app.current_user_id,
                            t["BuyerID"] if role == 'Seller' else t["SellerID"],    # 리뷰 대상 ID
                            t["PostID"]
                        )
                    ).pack(pady=5)
        else:
            # 거래 내역이 없는 경우 메시지 표시
            tk.Label(transactions_window, text="No transactions found.", font=("Comic Sans MS", 12, "italic")).pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load transactions: {e}")
    finally:
        if cursor:
            cursor.close()

