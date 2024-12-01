import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import conn
import mysql.connector


def leave_review(transaction_id, author_id, target_id, post_id):
    """사용자(구매자/판매자)가 상대방에게 리뷰를 남길 수 있도록 합니다."""
    review_window = tk.Toplevel()
    review_window.title("Leave Review")
    review_window.geometry("400x400")

    tk.Label(review_window, text="Leave a Review", font=("Comic Sans MS", 16)).pack(pady=10)
    tk.Label(review_window, text="Satisfaction (1-5):", font=("Comic Sans MS", 14), bg="#ffffff", fg="#333333").pack(pady=5)
    satisfaction_var = tk.DoubleVar(value=3.0)
    tk.Entry(review_window, textvariable=satisfaction_var).pack()

    tk.Label(review_window, text="Review Content:", font=("Comic Sans MS", 14), bg="#ffffff", fg="#333333").pack(pady=5)
    review_content_var = tk.StringVar()
    tk.Entry(review_window, textvariable=review_content_var, width=50).pack()

    def submit_review():
        """트랜잭션에 대한 리뷰를 제출하고 대상 사용자의 TransactionSatisfaction을 업데이트합니다."""
        # 만족도 점수 검증
        if satisfaction_var.get() < 1.0 or satisfaction_var.get() > 5.0:
            messagebox.showerror("Error", "Satisfaction rating must be between 1.0 and 5.0")
            return

        # 리뷰 내용 검증
        if not review_content_var.get().strip():
            messagebox.showerror("Error", "Review content cannot be empty.")
            return

        try:
            
            if conn is None or not conn.is_connected():
                conn.reconnect(attempts=3, delay=2)
            
            cursor = conn.cursor()

            # 해당 TransactionID와 AuthorID로 이미 리뷰가 존재하는지 확인
            cursor.execute("""
                SELECT COUNT(*) 
                FROM Review 
                WHERE TransactionID = %s AND AuthorID = %s
            """, (transaction_id, author_id))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "You have already submitted a review for this transaction.")
                return

            # Review 테이블에 새로운 리뷰 삽입
            cursor.execute("""
                INSERT INTO Review (TransactionID, AuthorID, TargetID, PostID, TransactionSatisfaction, ReviewContent)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (transaction_id, author_id, target_id, post_id, satisfaction_var.get(), review_content_var.get()))
            conn.commit()

            # 대상 사용자의 TransactionSatisfaction 업데이트
            update_transaction_satisfaction(target_id, satisfaction_var.get())

           
            messagebox.showinfo("Success", "Review submitted successfully!")
            review_window.destroy()

        except Exception as e:
            conn.rollback()  
            messagebox.showerror("Error", f"Failed to submit review: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

                
                

    tk.Button(review_window, text="Submit Review", command=submit_review).pack(pady=20)



def update_transaction_satisfaction(user_id, new_satisfaction):
    """새 리뷰를 기반으로 사용자의 TransactionSatisfaction을 업데이트합니다."""
    cursor = None
    try:
        # 새로운 만족도에 대해 유효성 검사
        if not isinstance(new_satisfaction, (int, float)) or not (1 <= new_satisfaction <= 5):
            raise ValueError(f"Invalid new_satisfaction value: {new_satisfaction}. Must be between 1 and 5.")

        if conn is None or not conn.is_connected():
            conn.reconnect(attempts=3, delay=2)

        cursor = conn.cursor(dictionary=True)

        # 현재 TransactionSatisfaction 및 TotalReviews 가져오기
        cursor.execute("""
            SELECT TransactionSatisfaction, TotalReviews
            FROM users
            WHERE UserID = %s
        """, (user_id,))
        user = cursor.fetchone()

        if not user:
            raise Exception(f"User with ID {user_id} not found.")

        current_satisfaction = float(user['TransactionSatisfaction'])
        total_reviews = user['TotalReviews']

        if total_reviews < 0:
            raise ValueError(f"Invalid total_reviews value: {total_reviews}.")

        # 새로운 가중 평균 계산
        updated_satisfaction = round(
            ((current_satisfaction * total_reviews) + new_satisfaction) / (total_reviews + 1), 1
        )

        # 사용자의 TransactionSatisfaction 업데이트 및 TotalReviews 증가
        cursor.execute("""
            UPDATE users
            SET TransactionSatisfaction = %s, TotalReviews = TotalReviews + 1
            WHERE UserID = %s
        """, (updated_satisfaction, user_id))
        conn.commit()

    except Exception as e:
        conn.rollback()  
        print(f"Error updating TransactionSatisfaction for user {user_id}: {e}")
    finally:
        if cursor:
            cursor.close()



