import tkinter as tk
from tkinter import ttk, messagebox
from signup import show_signup_window
from ui_views.search_view_post import show_post_details
from ui_views.search_view_post import search_posts
from ui_views.add_post import show_add_product_window
from login import show_login_window
from database import conn
from profile import show_profile
from PIL import Image, ImageTk


# 메인 애플리케이션 창
class MarketplaceApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Secondhand Marketplace")
        self.geometry("800x600")
        self.current_user_id = None  # 초기화 시 사용자가 로그인되지 않음

        # 메뉴 바
        self.create_menu()

       # 계정 메뉴 상태 업데이트
        self.update_account_menu()

        # 스크롤 가능한 프레임 설정
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 캔버스와 스크롤바 배치
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

         # 마우스 휠 스크롤 추가
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        
        self.show_homepage()  

        
    def create_menu(self):
        """애플리케이션 메뉴 생성"""
        self.menu_bar = tk.Menu(self)

        
        home_menu = tk.Menu(self.menu_bar, tearoff=0)
        home_menu.add_command(label="Home", command=self.show_homepage)
        home_menu.add_command(label="Add Post", command=lambda: show_add_product_window(self))
        home_menu.add_command(label="Search Post", command=self.open_search_window)
        self.menu_bar.add_cascade(label="Menu", menu=home_menu)

        
        self.account_menu = tk.Menu(self.menu_bar, tearoff=0)  
        self.account_menu.add_command(label="Log In", command=lambda: show_login_window(self))
        self.account_menu.add_command(label="Sign Up", command=lambda: show_signup_window(self))
        self.account_menu.add_command(label="Log Out", command=self.log_out)
        self.account_menu.add_command(label="Profile", command=lambda: show_profile(self), state="disabled")
        self.menu_bar.add_cascade(label="Account", menu=self.account_menu)

        
        self.config(menu=self.menu_bar)
        self.config(menu=self.menu_bar)


    def update_account_menu(self):
        """사용자의 로그인 상태에 따라 계정 메뉴 상태 업데이트"""
        if self.current_user_id:
            # "Log In" 및 "Sign Up" 비활성화, "Log Out" 활성화
            self.account_menu.entryconfig(0, state="disabled")  # "Log In" 비활성화
            self.account_menu.entryconfig(1, state="disabled")  # "Sign Up" 비활성화
            self.account_menu.entryconfig(2, state="normal")    # "Log Out" 활성화
            self.account_menu.entryconfig(3, state="normal")  # "Profile" 활성화
        else:
             # "Log In" 및 "Sign Up" 활성화, "Log Out" 비활성화
            self.account_menu.entryconfig(0, state="normal")    # "Log In" 활성화
            self.account_menu.entryconfig(1, state="normal")    # "Sign Up" 활성화
            self.account_menu.entryconfig(2, state="disabled")  # "Log Out" 비활성화
            self.account_menu.entryconfig(3, state="disabled")  # "Profile" 비활성화

    def show_homepage(self):
        
        self.clear_main_frame()

        
        tk.Label(
            self.scrollable_frame,
            text="동국 중고 마켓",
            font=("Comic Sans MS", 30, "bold"),  
            bg="orange",
            fg="white",  
            relief="flat",
        ).pack(pady=(40, 0), padx=20)  

       
        image_path = r"C:\Users\지동우\Documents\second_hand_marketplace\ui_views\other images\데베설 아코.jpg"
        try:
            img = Image.open(image_path)
            img = img.resize((300, 300), Image.LANCZOS)  
            photo = ImageTk.PhotoImage(img)

            
            image_label = tk.Label(self.scrollable_frame, image=photo, bg="orange")
            image_label.image = photo  
            image_label.pack(pady=(20, 0))  
        except Exception as e:
            print(f"Error loading image: {e}")  

        
        self.scrollable_frame.pack(anchor="n", expand=True)
        
    def log_out(self):
        """현재 사용자 로그아웃"""
        if self.current_user_id:
            # 로그인된 사용자 초기화
            self.current_user_id = None
            # 사용자 알림
            messagebox.showinfo("log out", "you are now logged out")
            # 계정 메뉴 상태 업데이트
            self.update_account_menu()
        else:
            messagebox.showwarning("No User Logged In", "No user is currently logged in.")
    
    def open_search_window(self):
        """게시물 검색 기능 표시"""
        # 검색 기능용 새 창 생성
        search_window = tk.Toplevel(self)
        search_window.title("Search Post")
        search_window.geometry("800x600")
        search_window.configure(bg="#ffffff")  

        # 헤더 섹션
        header_frame = tk.Frame(search_window, bg="#ff7f0e", height=80)
        header_frame.pack(fill="x")
        tk.Label(
            header_frame, text="Search Posts", font=("Comic Sans MS", 20, "bold"), bg="#ff7f0e", fg="#ffffff"
        ).pack(pady=20)

        # 필터 섹션
        filter_frame = tk.Frame(search_window, bg="#ffffff", padx=20, pady=10)
        filter_frame.pack(fill="x")

        filters = [
            ("Title:", "title_var"),
            ("Neighborhood:", "neighborhood_var"),
            ("Category:", "category_var"),
            ("Min Price:", "min_price_var"),
            ("Max Price:", "max_price_var"),
            ("Status:", "status_var"),
            ("Min Likes:", "likes_var"),
        ]

        for idx, (label, var_name) in enumerate(filters):
            tk.Label(
                filter_frame, text=label, font=("Comic Sans MS", 12), bg="#ffffff", fg="#333333"
            ).grid(row=idx, column=0, sticky="w", pady=5)
            entry_var = tk.StringVar()
            setattr(self, var_name, entry_var)
            if label == "Category:":
                ttk.Combobox(
                    filter_frame, textvariable=entry_var, values=["All", "Furniture", "Appliances", "Electronics", "Toys", "Others"],
                    state="readonly"
                ).grid(row=idx, column=1, sticky="w", padx=10, pady=5)
            elif label == "Status:":
                ttk.Combobox(
                    filter_frame, textvariable=entry_var, values=["All", "Available", "Sold", "Reserved"],
                    state="readonly"
                ).grid(row=idx, column=1, sticky="w", padx=10, pady=5)
            else:
                tk.Entry(filter_frame, textvariable=entry_var).grid(row=idx, column=1, sticky="w", padx=10, pady=5)

        # 검색 버튼
        tk.Button(
            filter_frame, text="Search", font=("Comic Sans MS", 12, "bold"), bg="#ff7f0e", fg="#ffffff",
            command=lambda: search_posts(
                self.tree, self.title_var, self.neighborhood_var, self.category_var,
                self.min_price_var, self.max_price_var, self.status_var, self.likes_var
            )
        ).grid(row=len(filters), column=0, columnspan=2, pady=10)

        # 결과 섹션
        results_frame = tk.Frame(search_window, bg="#ffffff", pady=10)
        results_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            results_frame,
            columns=("PostID", "Title", "Price", "Status", "Likes", "Category", "Neighborhood", "PostDate"),
            show="headings",
            height=15
        )

        # TreeView 컬럼 설정
        for col in ("PostID", "Title", "Price", "Status", "Likes", "Category", "Neighborhood", "PostDate"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "Title" else 200)

        # TreeView 결과 표시
        self.tree.pack(side="left", fill="both", expand=True, padx=20)

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # PostID 숨기기
        self.tree.heading("PostID", text="PostID")
        self.tree.column("PostID", width=0, stretch=False)

        # 행 더블 클릭 이벤트 바인딩
        self.tree.bind("<Double-1>", lambda event: show_post_details(event, self.current_user_id))

      

    def display_items(self, items):
        """스크롤 가능한 프레임에 게시물 표시"""
        if not items:
            tk.Label(self.scrollable_frame, text="No posts found.", bg="white", font=("Comic Sans MS", 12)).pack(pady=10)
            return

        for item in items:
            frame = tk.Frame(self.scrollable_frame, bg="lightgray", pady=5, padx=5)
            frame.pack(fill="x", pady=5, padx=20)
            tk.Label(frame, text=f"Title: {item['Title']}", font=("Comic Sans MS", 12), bg="lightgray").pack(anchor="w")
            tk.Label(frame, text=f"Price: ${item['Price']}", font=("Comic Sans MS", 12), bg="lightgray").pack(anchor="w")
            tk.Label(frame, text=f"Description: {item['Description']}", font=("Comic Sans MS", 10), bg="lightgray", wraplength=700).pack(anchor="w")
            tk.Label(frame, text=f"Category: {item['Category']}", font=("Comic Sans MS", 10), bg="lightgray").pack(anchor="w")
            tk.Label(frame, text=f"Likes: {item['LikesCount']}", font=("Comic Sans MS", 10), bg="lightgray").pack(anchor="w")


    def clear_main_frame(self):
        """Clear all widgets in the main frame."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()


    def on_mouse_wheel(self, event):
        """Scroll the canvas using the mouse wheel."""
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

if __name__ == "__main__":
    app = MarketplaceApp()
    app.mainloop()
