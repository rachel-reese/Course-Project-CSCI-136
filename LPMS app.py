import tkinter as tk
import random
from tkinter import *
from tkinter import messagebox, filedialog
import mysql.connector
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Entity:
    _id = 0
    _name = ""
    _points = 0

    def __init__(self, name, points):
        self._id = random.randint(100, 999)
        self._name = name
        self._points = points

    def get_id(self):
        id = self._id
        return id

    def get_name(self):
        name = self._name
        return name

    def get_points(self):
        points = self._points
        return self._points

    def set_points(self, points):
        self._points = points


class Account(Entity):
    _purchases = None

    def __init__(self, name, points, purchases):
        self._id = random.randint(1000000000, 10000000000)
        self._name = name
        self._points = points
        self._purchases = purchases

    def get_purchases(self):
        purchases = self._purchases
        return purchases


class Product(Entity):

    def __init__(self, name, points):
        self._id = random.randint(1000000000, 10000000000)
        self._name = name
        self._points = points

    def set_name(self, new_name):
        self._name = new_name


class Reward(Product):

    def __init__(self, name, points):
        self._id = random.randint(1000000000, 10000000000)
        self._name = name
        self._points = points


LPMSdb = mysql.connector.connect(
    host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
    user="ucoualjdf6fkwbkz",
    passwd="VsRHA6IchSrICzGGpk0o",
    database="btnh0atttknaekiqi5e9"
)

cursor = LPMSdb.cursor()

large_font = ("Verdana", 12)


class LPMSApp(tk.Tk):
    visible_frame = None
    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        tk.Tk.wm_title(self, "Loyalty Program Management System")
        tk.Tk.geometry(self, "1000x1000")
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Home, AccountSearch, ProductsPage, RewardsPage, SalesPage, UploadInfoPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, stick="nsew")

        self.show_frame(Home)

    def show_frame(self, cont):
        cursor.close()
        LPMSdb.close()
        frame = self.frames[cont]
        frame.tkraise()


class Home(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        logo = PhotoImage(file=r'C:\Users\Rachel\Pictures\logo2.png')
        logo_label = tk.Label(self, image=logo)
        logo_label.image = logo
        logo_label.pack()

        products_button = tk.Button(self, text="products", command=lambda: controller.show_frame(ProductsPage))
        products_button.pack()

        rewards_button = tk.Button(self, text="rewards", command=lambda: controller.show_frame(RewardsPage))
        rewards_button.pack()

        sales_button = tk.Button(self, text="sales", command=lambda: controller.show_frame(SalesPage))
        sales_button.pack()

        update_info_button = tk.Button(self, text="upload data", command=lambda: controller.show_frame(UploadInfoPage))
        update_info_button.pack()

        acct_search_button = tk.Button(self, text="account search",
                                       command=lambda: controller.show_frame(AccountSearch))
        acct_search_button.pack()


class AccountSearch(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        home_button = tk.Button(self, text="home", command=lambda: controller.show_frame(Home))
        home_button.pack()

        label = tk.Label(self, text="Account Search", font=large_font)
        label.pack(pady=20)

        search_bar = tk.Entry(self, font=large_font)
        search_bar.pack()

        listbox = tk.Listbox(self, relief='flat', bg='SystemButtonFace')
        listbox.pack(pady=40)

        query = "SELECT name from accounts"
        cursor.execute(query)
        names_tuple = cursor.fetchall()
        global names_list
        names_list = [name[0] for name in names_tuple]
        query = "SELECT id from accounts"
        cursor.execute(query)
        ids_tuple = cursor.fetchall()
        ids_list = [id[0] for id in ids_tuple]
        query = "SELECT points from accounts"
        cursor.execute(query)
        points_tuple = cursor.fetchall()
        points_list = [point[0] for point in points_tuple]
        customer_search_dict = {}
        for i in range(len(names_list)):
            customer_search_dict.update({names_list[i]: [ids_list[i], points_list[i]]})

        def to_results(e):
            listbox.delete(0, END)
            user_entry = search_bar.get()
            global results_list
            results_list = []
            global results
            results = {}
            if user_entry == '':
                results = customer_search_dict
            else:
                for key, value in customer_search_dict.items():
                    if user_entry.lower() in key.lower():
                        results.update({key: value})
                        results_list.append(key)
            for key in results:
                listbox.insert(END, key)

        def view_customer(e):
            selection = listbox.curselection()
            customer = results_list[selection[0]]
            for widget in self.winfo_children():
                widget.destroy()
            customer_label = tk.Label(self, text=customer, font=large_font)
            customer_label.grid(row=0, column=0)
            global value_list
            value_list = results[customer]
            global points
            points = value_list[1]
            global points_earned
            points_earned = tk.Label(self, text=f"Points: {points}")
            points_earned.grid(row=3, column=0)
            add_10pts = tk.Button(self, text="Add ten points", command=lambda: add_points(10))
            add_10pts.grid(row=5, column=0)
            add_20pts = tk.Button(self, text="Add twenty points", command=lambda: add_points(20))
            add_20pts.grid(row=5, column=1)
            custom_entry = tk.Entry(self)
            custom_entry.grid(row=6, column=2)
            add_custom = tk.Button(self, text="Add custom amount", command=lambda: custom_points(custom_entry))
            # command = custom_points(custom_entry)
            add_custom.grid(row=5, column=2)

        def custom_points(entrybox):
            entry = entrybox.get()
            if entry == "":
                tk.messagebox.showerror("invalid number", "Please enter a valid number")
            else:
                for char in entry:
                    if char.isdigit():
                        is_int = True
                    else:
                        is_int = False
                        tk.messagebox.showerror("invalid number", "Please enter a valid number")
                        break
                if is_int:
                    add_points(int(entry))
            entrybox.delete(0, END)

        def add_points(addition):
            global points
            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )
            cursor = LPMSdb.cursor()
            points += addition
            cursor.execute("UPDATE accounts SET points=%s WHERE id=%s", (points, value_list[0]))
            LPMSdb.commit()
            cursor.close()
            LPMSdb.close()
            global points_earned
            points_earned.config(text=f"Points: {points}")

        search_bar.bind("<Return>", to_results)
        listbox.bind('<<ListboxSelect>>', view_customer)


class ProductsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        LPMSdb = mysql.connector.connect(
            host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
            user="ucoualjdf6fkwbkz",
            passwd="VsRHA6IchSrICzGGpk0o",
            database="btnh0atttknaekiqi5e9"
        )

        global cursor
        cursor = LPMSdb.cursor()

        home_button = tk.Button(self, text="home", command=lambda: controller.show_frame(Home))
        home_button.pack()

        label = tk.Label(self, text="Products", font=large_font)
        label.pack(pady=20)

        product_listbox = tk.Listbox(self, relief='flat', bg='SystemButtonFace')
        product_listbox.pack()

        cursor.execute("SELECT name from products")
        product_names_tup = cursor.fetchall()
        global product_names_list
        product_names_list = [name[0] for name in product_names_tup]

        cursor.execute("SELECT id from products")
        product_ids_tup = cursor.fetchall()
        product_ids_list = [name[0] for name in product_ids_tup]

        cursor.execute("SELECT points from products")
        product_points_tup = cursor.fetchall()
        product_points_list = [name[0] for name in product_points_tup]

        cursor.close()
        LPMSdb.close()

        global product_search_dict
        product_search_dict = {}
        for i in range(len(product_names_list)):
            product_search_dict.update({product_names_list[i]: [product_ids_list[i], product_points_list[i]]})

        for key in product_search_dict:
            product_listbox.insert(END, key)

        def view_product(e):
            selection = product_listbox.curselection()
            global product
            product = product_names_list[selection[0]]
            global value_list
            value_list = product_search_dict[product]
            global points
            points = value_list[1]
            for widget in self.winfo_children():
                widget.destroy()
            product_label = tk.Label(self, text=product, font=large_font)
            product_label.pack()
            global points_label
            points_label = tk.Label(self, text=f"Points: {points}")
            points_label.pack()
            custom_entry = tk.Entry(self)
            custom_entry.pack()
            add_custom = tk.Button(self, text="Add points", command=lambda: custom_points(custom_entry))
            add_custom.pack()
            delete = tk.Button(self, text="Delete product", command=lambda: remove_product)
            delete.pack()

        def custom_points(entrybox):
            entry = entrybox.get()
            if entry == "":
                tk.messagebox.showerror("invalid number", "Please enter a valid number")
            else:
                for char in entry:
                    if char.isdigit():
                        is_int = True
                    else:
                        is_int = False
                        tk.messagebox.showerror("invalid number", "Please enter a valid number")
                        break
                if is_int:
                    add_points(int(entry))
            entrybox.delete(0, END)

        def add_points(addition):
            global points
            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )

            global cursor
            cursor = LPMSdb.cursor()
            points += addition
            cursor.execute("UPDATE products SET points=%s WHERE id=%s", (points, value_list[0]))
            LPMSdb.commit()
            cursor.close()
            LPMSdb.close()
            global points_label
            points_label.config(text=f"Points: {points}")

        def remove_product():
            global product
            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )

            global cursor
            cursor = LPMSdb.cursor()
            remove_yesno = tk.messagebox.askyesno(message=f"Delete {product}?")
            if remove_yesno:
                cursor.execute("DELETE FROM products WHERE id=%s", (value_list[0],))
                LPMSdb.commit()
                cursor.close()
                LPMSdb.close()
                controller.show_frame(Home)
                for widget in self.winfo_children():
                    widget.destroy()
                controller.show_frame(Home)
            else:
                return

        product_listbox.bind("<<ListboxSelect>>", view_product)


class RewardsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        LPMSdb = mysql.connector.connect(
            host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
            user="ucoualjdf6fkwbkz",
            passwd="VsRHA6IchSrICzGGpk0o",
            database="btnh0atttknaekiqi5e9"
        )
        cursor = LPMSdb.cursor()

        home_button = tk.Button(self, text="home", command=lambda: controller.show_frame(Home))
        home_button.pack()

        label = tk.Label(self, text="Rewards", font=large_font)
        label.pack(pady=20)

        reward_listbox = tk.Listbox(self, relief='flat', bg='SystemButtonFace')
        reward_listbox.pack()

        cursor.execute("SELECT name from rewards")
        rewards_names_tup = cursor.fetchall()
        global rewards_names_list
        rewards_names_list = [name[0] for name in rewards_names_tup]

        cursor.execute("SELECT id from rewards")
        rewards_ids_tup = cursor.fetchall()
        rewards_ids_list = [name[0] for name in rewards_ids_tup]

        cursor.execute("SELECT points from rewards")
        rewards_points_tup = cursor.fetchall()
        rewards_points_list = [name[0] for name in rewards_points_tup]

        cursor.close()
        LPMSdb.close()

        global rewards_search_dict
        rewards_search_dict = {}
        for i in range(len(rewards_names_list)):
            rewards_search_dict.update({rewards_names_list[i]: [rewards_ids_list[i], rewards_points_list[i]]})

        for key in rewards_search_dict:
            reward_listbox.insert(END, key)

        def view_reward(e):
            selection = reward_listbox.curselection()
            global reward
            reward = rewards_names_list[selection[0]]
            global value_list
            value_list = rewards_search_dict[reward]
            global points
            points = value_list[1]
            for widget in self.winfo_children():
                widget.destroy()
            reward_label = tk.Label(self, text=reward, font=large_font)
            reward_label.pack()
            global points_label
            points_label = tk.Label(self, text=f"Points: {points}")
            points_label.pack()
            custom_entry = tk.Entry(self)
            custom_entry.pack()
            add_custom = tk.Button(self, text="Add points", command=lambda: custom_points(custom_entry))
            add_custom.pack()
            delete = tk.Button(self, text="Delete reward", command= lambda: remove_reward())
            delete.pack()

        def custom_points(entrybox):
            entry = entrybox.get()
            if entry == "":
                tk.messagebox.showerror("invalid number", "Please enter a valid number")
            else:
                for char in entry:
                    if char.isdigit():
                        is_int = True
                    else:
                        is_int = False
                        tk.messagebox.showerror("invalid number", "Please enter a valid number")
                        break
                if is_int:
                    add_points(int(entry))
            entrybox.delete(0, END)

        def add_points(addition):
            global points
            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )
            points += addition
            cursor.execute("UPDATE products SET points=%s WHERE id=%s", (points, value_list[0]))
            LPMSdb.commit()
            cursor.close()
            LPMSdb.close()
            global points_label
            points_label.config(text=f"Points: {points}")

        def remove_reward():
            global reward
            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )
            remove_yesno = tk.messagebox.askyesno(message=f"Delete {reward}?")
            if remove_yesno:
                cursor.execute("DELETE FROM rewards WHERE id=%s", (value_list[0],))
                LPMSdb.commit()
                cursor.close()
                LPMSdb.close()
                controller.show_frame(Home)
                for widget in self.winfo_children():
                    widget.destroy()
                controller.show_frame(Home)
            else:
                return

        reward_listbox.bind('<<ListboxSelect>>', view_reward)


class SalesPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        home_button = tk.Button(self, text="home", command=lambda: controller.show_frame(Home))
        home_button.pack()

        LPMSdb = mysql.connector.connect(
            host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
            user="ucoualjdf6fkwbkz",
            passwd="VsRHA6IchSrICzGGpk0o",
            database="btnh0atttknaekiqi5e9"
        )
        global cursor
        cursor = LPMSdb.cursor()

        label = tk.Label(self, text="Sales", font=large_font)
        label.pack(pady=10, padx=10)

        button2 = tk.Button(self, text="Back", command=lambda: controller.show_frame(Home))
        button2.pack()

        cursor.execute("SHOW COLUMNS FROM purchases")
        columns = cursor.fetchall()
        foods_list = [name[0] for name in columns]
        foods_list = [food for food in foods_list[1:]]
        sums = []
        for item in foods_list:
            query = f"SELECT SUM(`{item}`) from purchases"
            cursor.execute(query)
            sum = cursor.fetchone()[0]
            sums.append(sum)

        cursor.close()
        LPMSdb.close()
        f = Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        a.bar(foods_list, sums)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class UploadInfoPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        home_button = tk.Button(self, text="home", command=lambda: controller.show_frame(Home))
        home_button.pack()

        upload_accounts = tk.Button(self, text="Upload account file (CSV)", command=lambda: open_file(1))
        upload_accounts.pack()
        upload_products = tk.Button(self, text="Upload product file (CSV)", command=lambda: open_file(2))
        upload_products.pack()
        upload_rewards = tk.Button(self, text="Upload rewards file (CSV)", command=lambda: open_file(3))
        upload_rewards.pack()

        global file_df
        file_df = None

        def open_file(number):
            filename = filedialog.askopenfilename(title="Select File", filetypes=(("CSV files", "*.csv"),))
            global file_df
            if filename == "":
                label = tk.Label(self, text=f"no file chosen")
                label.pack()
            else:
                label = tk.Label(self, text=f"{filename} uploaded successfully")
                label.pack()
                file_df = pd.read_csv(filename)
                file_df.dropna(subset=["name"], inplace=True)
                file_df = file_df[file_df.name != " "]
                file_df.dropna(how="all", inplace=True)
                file_df.fillna(0, inplace=True)
                file_df.reset_index()
            if number == 1:
                account_database()
            elif number == 2:
                product_database()
            elif number == 3:
                reward_database()

        def account_database():
            if file_df is not None:
                accounts_list = []
                for i in range(len(file_df)):
                    name = file_df.at[i, "name"]
                    points = int(file_df.at[i, "points"])
                    purchases = file_df.loc[i, ['croissant', 'breakfast sandwich', 'muffin', 'scone', 'black tea',
                                               'panini', 'matcha', 'chai', 'vanilla', 'mocha', 'caramel']]
                    purchases = purchases.to_frame()
                    purchases = purchases.T
                    new_account = Account(name, points, purchases)
                    accounts_list.append(new_account)
            else:
                return

            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )
            global cursor
            cursor = LPMSdb.cursor()

            for account in accounts_list:
                query = "INSERT INTO accounts (id, name, points) VALUES (%s, %s, %s)"
                values = (account.get_id(), account.get_name(), int(account.get_points()))
                cursor.execute(query, values)
                LPMSdb.commit()
                purchase_df = account.get_purchases()
                purchase_df.reset_index(drop=True, inplace=True)
                numbers_list = []
                for j in range(len(purchase_df.columns)):
                    numbers_list.append(int(purchase_df.iloc[0, j]))
                query = "INSERT INTO purchases (croissant, `breakfast sandwich`, muffin, scone, `black tea`, panini, " \
                        "matcha, chai, vanilla, mocha, caramel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (numbers_list[0], numbers_list[1], numbers_list[2], numbers_list[3], numbers_list[4],
                          numbers_list[5], numbers_list[6], numbers_list[7], numbers_list[8], numbers_list[9],
                          numbers_list[10])
                cursor.execute(query, values)
                LPMSdb.commit()
                i += 1

        def product_database():
            if file_df is not None:
                products_list = []
                for i in range(len(file_df)):
                    name = file_df.at[i, "name"]
                    points = int(file_df.at[i, "points"])
                    new_product = Product(name, points)
                    products_list.append(new_product)
            else:
                return

            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )
            global cursor
            cursor = LPMSdb.cursor()

            for product in products_list:
                query = "INSERT INTO products (id, name, points) VALUES (%s, %s, %s)"
                values = (product.get_id(), product.get_name(), int(product.get_points()))
                cursor.execute(query, values)
                LPMSdb.commit()

        def reward_database():
            if file_df is not None:
                rewards_list = []
                for i in range(len(file_df)):
                    name = file_df.at[i, "name"]
                    points = int(file_df.at[i, "points"])
                    new_reward = Product(name, points)
                    rewards_list.append(new_reward)
            else:
                return

            LPMSdb = mysql.connector.connect(
                host="btnh0atttknaekiqi5e9-mysql.services.clever-cloud.com",
                user="ucoualjdf6fkwbkz",
                passwd="VsRHA6IchSrICzGGpk0o",
                database="btnh0atttknaekiqi5e9"
            )
            global cursor
            cursor = LPMSdb.cursor()

            for reward in rewards_list:
                query = "INSERT INTO rewards (id, name, points) VALUES (%s, %s, %s)"
                values = (reward.get_id(), reward.get_name(), int(reward.get_points()))
                cursor.execute(query, values)
                LPMSdb.commit()

LPMS_app = LPMSApp()
LPMS_app.mainloop()
