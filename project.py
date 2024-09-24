from tkinter import (
    Tk,
    ttk,
    messagebox,
    Frame,
    TOP,
    NE,
    NW,
    EW,
    Text,
    Button,
    END,
    Menu,
    Widget,
    OptionMenu,
    Label,
    StringVar,
    Y,
    FALSE,
    TRUE,
    GROOVE,
    LEFT,
    RIGHT,
    CENTER,
    Toplevel,
)
from tksheet import Sheet
from customtkinter import CTkFrame, CTkLabel
from PIL import ImageTk, Image
import mysql.connector, json, csv, bcrypt, os, random, numpy, datetime, pandas
from functools import wraps

import location as loc


# Connection
def drop_db(mycursor, mydb, name):
    mycursor.execute(f"DROP DATABASE IF EXISTS {name}")
    mydb.commit()


def create_connection(host, user, password, port, name):
    try:
        mydb = mysql.connector.connect(
            host=host, user=user, password=password, port=port, database=name
        )
        mycursor = mydb.cursor()
        drop_db(mycursor, mydb, name)
    except:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
        )
        mycursor = mydb.cursor()
    finally:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
        )
        mycursor = mydb.cursor()
        mycursor.execute(f"""CREATE DATABASE {name}""")
        mydb.commit()
        del mydb, mycursor

        mydb = mysql.connector.connect(
            host=host, user=user, password=password, port=port, database=name
        )
        mycursor = mydb.cursor()
        return mydb, mycursor


# Login
def create_user_file():
    filename = r".config\user_list.json"
    user_list = {"users": {}}
    admin_pass = hash("admin")
    user_list["users"]["ADMIN"] = admin_pass
    with open(filename, "w") as f:
        json.dump(user_list, f, indent=4)


def log(user, password):
    filename = r".config\user_list.json"
    try:
        if not os.path.exists(filename):
            create_user_file()

        with open(filename, "r") as f:
            user_list = json.load(f)
        stored_password = user_list["users"].get(user)
        if check_pw(in_password=password, stored_password=stored_password):
            return True
        else:
            raise ValueError
    except FileNotFoundError as err:
        return err
    except ValueError:
        return "Not Correct User/Password"


def register(user, password):
    filename = r".config\user_list.json"
    try:
        if not os.path.exists(filename):
            create_user_file()

        with open(filename, "r") as f:
            user_list = json.load(f)
        if user in user_list:
            raise ValueError
        elif len(user) == 0 or len(password) == 0:
            return "Too short"
        else:
            user_list["users"][user] = hash(password)
            with open(filename, "w") as f:
                json.dump(user_list, f, indent=4)
    except ValueError:
        return f"User: {user} already registered"
    else:
        return f"User with name {user} is created!"


def login_main_loop(user, password):
    filename = r".config\user_list.json"
    if not os.path.exists(filename):
        create_user_file()
    return log(user, password)


def hash(password: str) -> str:
    salt = bcrypt.gensalt()
    password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt)
    return hashed_password.decode("utf-8")


def check_pw(in_password: str, stored_password: str) -> bool:
    return bcrypt.checkpw(in_password.encode("utf-8"), stored_password.encode("utf-8"))


# GUI
class GUILogin(Tk):
    with open(".config\config_database.json", "r") as f:
        config_data = json.load(f)
    info = config_data["INFO"]
    name = info["name"]
    images = config_data["RESOURCES"]

    def __init__(self) -> None:
        super().__init__()
        self.im_logo = ImageTk.PhotoImage(
            Image.open(GUILogin.images["company_icon"]).resize(size=(400, 300))
        )
        self.title(GUILogin.name)
        self.geometry(f"{self.im_logo.width()}x600")
        self.iconbitmap(MyGUI.images["windowIcon"])

        Label(self, image=self.im_logo, font=MyGUI.f_label, borderwidth=0).pack(
            anchor=NE
        )
        ttk.Separator(self, orient="horizontal").pack()

        login_frame1 = Frame(self, width=200, height=100)
        login_frame1.config(background=MyGUI.c_Log_F1)
        login_frame1.pack(side=TOP, fill="x", padx=0, pady=0)
        login_frame2 = Frame(self, width=200, height=100)
        login_frame2.config(background=MyGUI.c_Log_F2, bd=2)
        login_frame2.pack(side=TOP, fill="x", padx=0, pady=0)
        login_frame4 = Frame(self, width=200, height=100)
        login_frame4.config(background=MyGUI.c_Log_F1)
        login_frame4.pack(side=TOP, fill="x", padx=0, pady=0)
        login_frame5 = Frame(self, width=200, height=100)
        login_frame5.config(background=MyGUI.c_Log_F2, bd=2)
        login_frame5.pack(side=TOP, fill="x", padx=0, pady=0)
        login_frame3 = Frame(self, width=200, height=100)
        login_frame3.config(background=MyGUI.c_Log_F1)
        login_frame3.pack(side=TOP, fill="x", padx=0, pady=0)

        lab_user = Label(
            login_frame1, text="Username", font=(MyGUI.f_label, 12, "bold")
        )
        lab_user.pack(padx=5, pady=0)
        lab_user.configure(background=MyGUI.c_Log_F1, fg=MyGUI.c_Log_Letters)
        self.user_text = ttk.Entry(login_frame2, width=40, font=(MyGUI.f_text, 10))
        self.user_text.focus()
        self.user_text.pack(padx=0, pady=5)

        lab_pass = Label(
            login_frame4, text="Password", font=(MyGUI.f_label, 12, "bold")
        )
        lab_pass.pack(padx=5, pady=0)
        lab_pass.configure(background=MyGUI.c_Log_F1, fg=MyGUI.c_Log_Letters)
        self.password_text = ttk.Entry(
            login_frame5, width=40, font=(MyGUI.f_text, 10), show="*"
        )
        self.password_text.pack(padx=0, pady=5)

        self.user_text.bind(
            "<Return>", lambda e: self.password_text.focus_set() or "break"
        )
        self.password_text.bind("<Return>", lambda e: self.log_in())

        Button(
            login_frame3, text="Log in", font=(MyGUI.f_button, 12), command=self.log_in
        ).pack(padx=5, pady=5)

        height = MySW.get_widgets_height(self)
        self.geometry(f"{self.im_logo.width()}x{height}+575+150")

        self.resizable(False, False)
        self.mainloop()

    def log_in(self, event=None):
        username = self.user_text.get().strip(" \n").upper()
        password = self.password_text.get().strip(" \n")
        result = ""
        if username == "":
            result += "-No username \n"
        if password == "":
            result += "-No password \n"
        if result:
            messagebox.Message(
                self, title=f"{self.name}", message=f"Error:\n{result}", parent=self
            ).show()
            self.user_text.delete(0, END)
            self.password_text.delete(0, END)
            self.user_text.focus_set()
            return

        result = login_main_loop(username, password)
        if result != True:
            messagebox.Message(
                self, title=f"{self.name}", message=f"Error: {result}", parent=self
            ).show()
            self.user_text.delete(0, END)
            self.password_text.delete(0, END)
            self.user_text.focus_set()
        else:
            self.password_text.unbind("<return>")
            self.destroy()
            MyGUI(username)


class MyGUI(Tk):
    with open(".config\config_database.json", "r") as f:
        config_data = json.load(f)
    conexion = config_data["CONEXION"]

    create_connection(
        conexion["host"],
        conexion["user"],
        conexion["password"],
        conexion["port"],
        conexion["database"],
    )
    conexion = config_data["CONEXION"]
    info = config_data["INFO"]
    name = info["name"]

    mydb = mysql.connector.connect(
        host=conexion["host"],
        user=conexion["user"],
        password=conexion["password"],
        port=conexion["port"],
        database=name,
    )
    mycursor = mydb.cursor()

    images = config_data["RESOURCES"]

    c_Register_Frame = info["c_Register_Frame"]
    c_SW_Label_Args = info["c_SW_Label_Args"]
    c_SW_Table_Header = info["c_SW_Table_Header"]
    c_SW_Font = info["c_SW_Font"]
    c_SW_Frame_1 = info["c_SW_Frame_1"]
    c_SW_Frame_2 = info["c_SW_Frame_2"]
    c_SW_Labels = info["c_SW_Labels"]
    c_SW_Labels_Options = info["c_SW_Labels_Options"]
    c_SW_Letters_Options = info["c_SW_Letters_Options"]
    c_Main_Labels = info["c_Main_Labels"]
    c_SW_Letters = info["c_SW_Letters"]
    c_Log_Letters = info["c_Log_Letters"]
    c_Main_LFrame = info["c_Main_LFrame"]
    c_Main_Text = info["c_Main_Text"]
    c_Main_Bg = info["c_Main_Bg"]
    c_SW_Bg = info["c_SW_Bg"]
    c_SW_Textbox1 = info["c_SW_Textbox1"]
    c_SW_Textbox2 = info["c_SW_Textbox2"]
    c_Log_F1 = info["c_Log_F1"]
    c_Log_F2 = info["c_Log_F2"]

    f_option_label = info["font_option_label"]
    f_text = info["font_text"]
    f_label = info["font_label"]
    f_button = info["font_button"]

    f1_radius = info["f1_radius"]
    f2_radius = info["f2_radius"]

    def __init__(self, USER) -> None:
        super().__init__()
        self.username = USER

        self.secondary_windows = []
        self.sw_counter = 0
        self.iconbitmap(MyGUI.images["windowIcon"])
        conexion = MyGUI.config_data["CONEXION"]
        self.name = MyGUI.config_data["INFO"]["name"]
        self.mydb = mysql.connector.connect(
            host=conexion["host"],
            user=conexion["user"],
            password=conexion["password"],
            port=conexion["port"],
            database=self.name,
        )
        self.max_num_windows = 3
        self.mycursor = self.mydb.cursor()
        self.config(background=MyGUI.c_Main_Bg)
        self.focus_force()
        self.entry_point()

    def entry_point(self):
        self.title(f"{self.name}")
        self.geometry("720x720")
        self.minsize(width=500, height=500)

        # ORDER - MOVE - INFO
        self.im_order = ImageTk.PhotoImage(Image.open(MyGUI.images["orderIcon"]))
        self.im_move = ImageTk.PhotoImage(Image.open(MyGUI.images["moveIcon"]))
        self.im_info = ImageTk.PhotoImage(Image.open(MyGUI.images["infoIcon"]))
        self.im_icon = ImageTk.PhotoImage(
            Image.open(MyGUI.images["background"]).resize(size=(1380, 620))
        )
        self.im_trailer = ImageTk.PhotoImage(Image.open(MyGUI.images["trailerIcon"]))
        self.im_reset = ImageTk.PhotoImage(Image.open(MyGUI.images["resetIcon"]))
        self.im_logo = ImageTk.PhotoImage(
            Image.open(MyGUI.images["logo"]).resize(size=(600, 120))
        )

        # Menu definition
        menu = Menu(self)
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label="Exit", command=exit)
        menu.add_cascade(menu=file_menu, label="File")

        option_menu = Menu(menu, tearoff=0)
        option_menu.add_command(label="Exit", command=exit)
        option_menu.add_command(label="Register", command=self.create_register_window)
        option_menu.add_command(label="New Products", command=self.new_skus)
        option_menu.add_command(
            label="Read New Loc Information", command=self.reshape_all
        )
        option_menu.add_command(label="New Clients", command=self.add_clients)
        option_menu.add_command(
            label="Allocate Boxes from Products bufe", command=self.allocate_boxes_wrap
        )

        menu.add_cascade(menu=option_menu, label="Options")
        self.config(menu=menu)

        # TOP FRAME
        frame_top = Frame(self, width=70, height=100)
        frame_top.pack(side=TOP, fill="both", expand=FALSE, padx=20, pady=5)

        frame_top.config(background=MyGUI.c_Main_Bg)

        top_label = Label(frame_top, image=self.im_logo, borderwidth=0)
        top_label.pack(side=TOP)
        ttk.Separator(self, orient="horizontal").pack()

        # FRAMES
        frame_left = CTkFrame(self, width=70, height=70, corner_radius=10)
        frame_left.pack(side=LEFT, fill="both", expand=FALSE, padx=20, pady=0)
        frame_left.configure(fg_color=MyGUI.c_Main_LFrame)

        frame_mid = Frame(self, width=250, height=70)
        frame_mid.pack(side=LEFT, fill="both", expand=TRUE, padx=0, pady=0)
        frame_mid.config(background=MyGUI.c_Main_Bg)

        ord_label = Label(
            frame_left, image=self.im_order, cursor="hand2", bd=4, relief=GROOVE
        )
        ord_label.pack(padx=10, pady=10)
        ord_lT = CTkLabel(
            frame_left, text="Orders", font=(MyGUI.f_label, 18, "bold"), corner_radius=7
        )
        ord_lT.pack(fill="x")
        ord_lT.configure(fg_color=MyGUI.c_Main_Labels, text_color=MyGUI.c_Main_Text)
        ord_label.bind(
            "<Button-1>",
            lambda event: (MyGUI.on_label_click(ord_label), self.open_second_window(1)),
        )

        move_label = Label(
            frame_left, image=self.im_move, cursor="hand2", bd=4, relief=GROOVE
        )
        move_label.pack(padx=10, pady=10)
        move_lT = CTkLabel(
            frame_left, text="Moves", font=(MyGUI.f_label, 18, "bold"), corner_radius=7
        )
        move_lT.pack(fill="x")
        move_label.bind(
            "<Button-1>",
            lambda event: (
                MyGUI.on_label_click(move_label),
                self.open_second_window(2),
            ),
        )
        move_lT.configure(fg_color=MyGUI.c_Main_Labels, text_color=MyGUI.c_Main_Text)

        info_label = Label(
            frame_left, image=self.im_info, cursor="hand2", bd=4, relief=GROOVE
        )
        info_label.pack(padx=10, pady=10)
        info_lT = CTkLabel(
            frame_left, text="Info", font=(MyGUI.f_label, 18, "bold"), corner_radius=7
        )
        info_lT.pack(fill="x")
        info_label.bind(
            "<Button-1>",
            lambda event: (
                MyGUI.on_label_click(info_label),
                self.open_second_window(3),
            ),
        )
        info_lT.configure(fg_color=MyGUI.c_Main_Labels, text_color=MyGUI.c_Main_Text)

        trailer_label = Label(
            frame_left, image=self.im_trailer, cursor="hand2", bd=4, relief=GROOVE
        )
        trailer_label.pack(padx=10, pady=10)
        trailer_lT = CTkLabel(
            frame_left,
            text="Inbound",
            font=(MyGUI.f_label, 18, "bold"),
            corner_radius=7,
        )
        trailer_lT.pack(fill="x")
        trailer_label.bind(
            "<Button-1>",
            lambda event: (
                MyGUI.on_label_click(trailer_label),
                self.open_second_window(4),
            ),
        )
        trailer_lT.configure(fg_color=MyGUI.c_Main_Labels, text_color=MyGUI.c_Main_Text)

        res_label = Label(
            frame_left, image=self.im_reset, cursor="hand2", bd=4, relief=GROOVE
        )
        res_label.pack(padx=10, pady=10)
        res_lT = CTkLabel(
            frame_left, text="Reset", font=(MyGUI.f_label, 18, "bold"), corner_radius=7
        )
        res_lT.pack(fill="x")
        res_label.bind(
            "<Button-1>",
            lambda event: (MyGUI.on_label_click(res_label), self.open_second_window(5)),
        )
        res_lT.configure(fg_color=MyGUI.c_Main_Labels, text_color=MyGUI.c_Main_Text)

        Label(frame_mid, image=self.im_icon).place(x=0, y=0)

    def open_second_window(self, mode: int):
        for sw in self.secondary_windows:
            if sw.mode == mode:
                sw.focus_force()
                return None
        if self.sw_counter >= self.max_num_windows:
            msg = "Limit Reached You can only open up 3 windows at a time."
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=msg,
                parent=self,
            ).show()
            return None
        else:
            self.sw_counter += 1
            self.secondary_windows.append(MySW(self, mode))

    def create_register_window(self):
        self.registration_window = Toplevel(self)
        self.registration_window.config(bg=MyGUI.c_Main_Bg)

        self.registration_window.geometry(f"{self.im_logo.width()}x500")

        self.registration_window.title("Register new user")
        self.registration_window.iconbitmap(MyGUI.images["windowIcon"])

        self.register_top_frame = Frame(
            self.registration_window,
            width=self.im_logo.width(),
            height=self.im_logo.height(),
        )
        self.registration_logo = Label(
            self.register_top_frame, image=self.im_logo, borderwidth=0
        )

        self.registration_logo.pack(side=RIGHT, anchor=CENTER)
        self.register_top_frame.pack(side=TOP, fill="x", expand=False, pady=20)
        ttk.Separator(
            self.registration_window,
            orient="horizontal",
        ).pack(padx=10, pady=5, fill="x")

        description_Input_frame = CTkLabel(
            self.registration_window,
            text="Register a new user\nInsert username and password.",
            font=(MyGUI.f_label, 22, "bold"),
            text_color=MyGUI.c_Main_LFrame,
            fg_color=MyGUI.c_SW_Frame_1,
            corner_radius=MyGUI.f2_radius,
        )
        description_Input_frame.pack(pady=10)

        self.register_frame = CTkFrame(
            self.registration_window,
            width=200,
            height=200,
            fg_color=MyGUI.c_SW_Frame_1,
            corner_radius=MyGUI.f1_radius,
        )
        self.register_frame.pack(side=TOP, fill=None, expand=True, padx=5, pady=5)

        self.user = Label(
            self.register_frame, text="Username", font=(MyGUI.f_label, 12, "bold")
        )
        self.user.pack(padx=5, pady=5)
        self.user_text = ttk.Entry(
            self.register_frame, width=40, font=(MyGUI.f_label, 12)
        )
        self.user_text.focus()
        self.user_text.pack(padx=5, pady=5)

        self.password = Label(
            self.register_frame, text="Password", font=(MyGUI.f_label, 12, "bold")
        )
        self.password.pack(padx=5, pady=5)
        self.password_text = ttk.Entry(
            self.register_frame, width=40, font=(MyGUI.f_label, 12), show="*"
        )
        self.password_text.pack(padx=5, pady=5)

        self.user_text.bind(
            "<Return>", lambda e: self.password_text.focus_set() or "break"
        )
        self.password_text.bind("<Return>", lambda e: self.register())

        self.button = Button(
            self.register_frame,
            text="Register",
            font=(MyGUI.f_button, 12),
            command=self.register,
        )
        self.button.pack(padx=5, pady=10)

        self.registration_window.resizable(False, False)
        self.registration_window.grab_release()

    def register(self):
        username = self.user_text.get().strip(" \n").upper()
        password = self.password_text.get().strip(" \n")
        result = register(username, password)
        messagebox.Message(
            self.registration_window, title=f"{self.name}", message=result
        ).show()
        self.user_text.delete(0, END)
        self.password_text.delete(0, END)

    def new_skus(self):
        self.mycursor.execute("SELECT sku FROM Products")
        actual_skus = [x[0] for x in self.mycursor.fetchall()]
        try:
            with open(r".config\config_database.json", "r") as f:
                config_data = json.load(f)
        except json.decoder.JSONDecodeError as err:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=err,
                parent=self,
            ).show()
        except FileNotFoundError as err:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=err,
                parent=self,
            ).show()
        new_products = [x for x in config_data["PRODUCTS"] if x[0] not in actual_skus]

        if new_products:
            msg = "The next products were added to the system:\n"
            for product in new_products:
                msg += f"    {product[1]} sku->{product[0]}\n"

            sql = "INSERT INTO Products (sku, name, num_boxes_per_pallet, company_code, benefit, ADR) VALUES (%s, %s, %s, %s, %s, %s)"
            self.mycursor.executemany(sql, new_products)
            self.mydb.commit()
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=msg,
                parent=self,
            ).show()
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="There is no new products.\n Add new products to '.config'",
                parent=self,
            ).show()

    def reshape_all(self):
        try:
            with open(r".config\config_database.json", "r") as f:
                config_data = json.load(f)
        except json.decoder.JSONDecodeError as err:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=err,
                parent=self,
            ).show()
        except FileNotFoundError as err:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=err,
                parent=self,
            ).show()
        dimensions = config_data["WAREHOUSE_DIMENSIONS"]
        data = [
            (level["Weight"], level["Height"])
            for aisle_data in dimensions.values()
            for level in aisle_data["Levels"].values()
        ]

        for pair in data:
            if not isinstance(pair[0], int) or not isinstance(pair[1], int):
                messagebox.Message(
                    self,
                    title=f"{self.name}",
                    message="Not correct datatype",
                    parent=self,
                ).show()

        result = {}
        for aisle, aisle_data in dimensions.items():
            rows = aisle_data["Rows"]
            levels = aisle_data["Levels"]
            for row in range(1, rows + 1):
                for level, level_data in levels.items():
                    key = f"{aisle}/{row}/{level}"
                    value = f"{level_data['Height']}:{level_data['Weight']}"
                    result[key] = value

        try:
            for position, data in result.items():
                height, weight = data.split(":")
                self.mycursor.execute(
                    f"UPDATE Locations SET max_weight = {weight}, max_height = {height} WHERE position = '{position}'"
                )
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=f"{position}", parent=self
            ).show()
        else:
            self.mydb.commit()

    def add_clients(self):
        with open(r".config\config_database.json", "r") as f:
            data = json.load(f)
        clients = data["CLIENTS"]
        set_clients_json = set()

        try:
            for client in clients:
                set_clients_json.add((client[1], client[0]))
            self.mycursor.execute("SELECT company_code, name FROM Providers")
            old_clients = self.mycursor.fetchall()
            set_clients_db = set()
            for client in old_clients:
                set_clients_db.add((client[0], client[1]))
            set_new_clients = set_clients_json.difference(set_clients_db)

            list_new_clients = []
            while set_new_clients:
                list_new_clients.append(set_new_clients.pop())

            if not list_new_clients:
                raise ValueError
            for client in list_new_clients:
                order_files(
                    [
                        (client[1], client[0]),
                    ]
                )
                querie = f"INSERT INTO Providers (company_code, name) VALUES ('{client[0]}', '{client[1]}')"
                self.mycursor.execute(querie)
                self.mydb.commit()

        except ValueError:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="There is no new clients.",
                parent=self,
            ).show()
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        except:
            messagebox.Message(
                self, title=f"{self.name}", message="ERROR", parent=self
            ).show()
        else:
            messagebox.Message(
                self, title=f"{self.name}", message=f"New Clients added.", parent=self
            ).show()

    def on_label_click(widget):
        widget.config(relief="sunken")
        widget.after(200, lambda: widget.config(relief=GROOVE))

    def allocate_boxes_wrap(self):
        msg = allocate_boxes()
        messagebox.Message(
                    self,
                    title=f"{self.name}",
                    message=msg,
                    parent=self,
                ).show()
class MySW(Toplevel):
    def __init__(self, og_window: Tk, mode: str):
        super().__init__()
        self.logo_image = ImageTk.PhotoImage(
            Image.open(MyGUI.images["logo"]).resize(size=(350, 70))
        )

        self.im_ddmenu_off = ImageTk.PhotoImage(
            Image.open(MyGUI.images["dropdownMenu"])
        )

        self.mode = mode
        self.father = og_window
        self.username = self.father.username
        self.mydb = og_window.mydb
        self.mycursor = og_window.mycursor
        self.name = og_window.name
        self.dd_active_color = loc.increase_hex(MyGUI.c_SW_Bg, -5)
        self.open_second_window(og_window, mode)

    def open_second_window(self, og_window: Tk, mode: int):
        self.resizable(True, True)
        self.geometry("700x250")
        self.minsize(550, 250)
        self.maxsize(700, 800)
        self.config(background=MyGUI.c_SW_Bg)
        match mode:
            case 1:
                self.title("Orders")
            case 2:
                self.title("Moves")
            case 3:
                self.title("Information")
            case 4:
                self.title("Inbound")
            case 5:
                self.title("Reset")
            case _:
                self.title("Warehouse Information")

        self.iconbitmap(MyGUI.images["windowIcon"])
        self.resizable(True, True)

        self.protocol("WM_DELETE_WINDOW", lambda: self.on_del_sw(self.father))

        match mode:
            case 1:
                self.info_scripts = (
                    "Add Orders",
                    "Delete Order",
                    "Show Wave Pre-release",
                    "Release Orders",
                    "Pick Order",
                    "Release Back Order",
                )

            case 2:
                self.info_scripts = (
                    "Assign Moves",
                    "Partial Move",
                    "Complete Move",
                    "Picking Move",
                )

            case 3:
                self.info_scripts = (
                    "Info Location",
                    "Info LP",
                    "Info Product",
                    "Search Sku",
                    "Info Order",
                    "Info Trailer",
                    "Container Location",
                    "Reshape Locations",
                )

            case 4:
                self.info_scripts = (
                    "Get Trailer",
                    "Check In",
                    "Delete Trailer",
                )

            case 5:
                self.info_scripts = (
                    "Reset Move Assignment",
                    "Reset Order Assignment",
                )

            case _:
                raise ValueError

        self.info_options_var = StringVar(self)
        self.focus_force()
        self.create_dropdown_menu()
        self.grab_release()

    def create_dropdown_menu(self):
        try:
            frame_options.destroy()
            label_options.destroy()
            option_menu.destroy()
        except UnboundLocalError:
            pass
        finally:
            frame_options = Frame(
                self,
                width=self.winfo_width() / 10,
                height=self.winfo_height() / 10,
            )
            frame_options.config(background=MyGUI.c_SW_Bg)
            option_menu = OptionMenu(
                frame_options,
                self.info_options_var,
                *self.info_scripts,
                command=lambda e: self.draw_screen_script(),
            )

            option_menu.config(
                bg=None,
                fg="BLACK",
                activebackground=self.dd_active_color,
                background=MyGUI.c_SW_Bg,
                border=0,
                highlightthickness=0,
                indicatoron=0,
                image=self.im_ddmenu_off,
                cursor="hand2",
                bd=4,
                relief=GROOVE,
            )
            frame_options.pack(fill="both", expand=True, padx=20, pady=20)

            label_options = CTkLabel(
                frame_options,
                text="OPTIONS:",
                font=(MyGUI.f_option_label, 20, "bold"),
                compound="left",
                corner_radius=10,
                height=50,
            )
            label_options.configure(
                fg_color=MyGUI.c_SW_Labels_Options,
                text_color=MyGUI.c_SW_Letters_Options,
            )
            sw_logo = Label(frame_options, image=self.logo_image, borderwidth=0)

            sw_logo.pack(side=LEFT, anchor=NW)
            option_menu.pack(side=RIGHT, anchor=NE, padx=5, pady=20)
            label_options.pack(side=RIGHT, anchor=NE, padx=5, pady=20)

    def draw_screen_script(self):
        try:
            self.del_children(self)
            self.geometry("500x700")

        except AttributeError as ERROR:
            return ERROR
        else:
            self.create_dropdown_menu()
        finally:
            self.frame_0 = CTkFrame(
                self,
                width=self.winfo_width() / 2,
                height=self.winfo_height() / 2,
                fg_color=MyGUI.c_SW_Frame_2,
                corner_radius=MyGUI.f1_radius,
            )
            self.frame_1 = CTkFrame(
                self,
                width=self.winfo_width() / 2,
                height=self.winfo_height() / 2,
                fg_color="transparent",
                corner_radius=MyGUI.f2_radius,
            )
            self.frame_0.pack(fill="both", expand=True, padx=20, pady=15)
            self.frame_1.pack(fill="both", expand=True, padx=20, pady=15)
            self.frame_1.columnconfigure(1, weight=1)
            title = self.info_options_var.get()
            args, args2 = [], []
            match title:
                case "Release Orders":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.release_order,
                    )
                    text_button = [
                        f"Insert company code {[cc[1] for cc in MyGUI.config_data['CLIENTS']]} "
                    ]

                case "Info Trailer":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_check_trailer,
                    )
                    text_button = ["Insert trailer number"]

                case "Pick Order":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.pick_order,
                    )
                    text_button = ["Insert Order Number"]

                case "Info Location":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_list_loc_info,
                    )
                    args = (
                        "Aisle ",
                        "Row   ",
                        "Level ",
                        "Weight",
                        "Height",
                        "ADR   ",
                    )
                    text_button = ["Insert Location"]

                case "Info Product":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_product_info,
                    )
                    args = (
                        "Sku         ",
                        "Company Code",
                        "Name        ",
                        "Benefit     ",
                        "Each/Pallet ",
                        "ADR         ",
                    )
                    text_button = ["Insert Product SKU"]

                case "Container Location":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_list_loc,
                    )
                    args = (
                        "Location       ",
                        "Sku            ",
                        "LP             ",
                        "Boxes          ",
                        "Allocated boxes",
                    )
                    text_button = ["Insert Location"]

                case "Info LP":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_list_lp,
                    )
                    args = (
                        "LP             ",
                        "SKU            ",
                        "Name           ",
                        "Location       ",
                        "Client         ",
                        "Boxes          ",
                        "Allocated boxes",
                        "ADR            ",
                    )
                    text_button = ["Insert LP"]

                case "Search Sku":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.search_sku,
                    )
                    text_button = ["Insert sku"]

                case "Info Order":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_info_order,
                    )
                    text_button = ["Insert order"]

                case "Assign Moves":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_moves,
                    )
                    text_button = [
                        f"Insert Company Code:\n{[cc[1] for cc in MyGUI.config_data['CLIENTS']]} or 'WA' for all.\n Unselect all cells after writing on them."
                    ]

                case "Partial Move":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_partial_move,
                    )

                    text_button = [
                        "Insert LP",
                        "Insert recieving LP",
                        "Number of boxes to move",
                    ]

                case "Get Trailer":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.get_trailer,
                    )

                    text_button = [
                        "Insert Trailer number",
                    ]

                case "Delete Trailer":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.delete_trailer,
                    )

                    text_button = [
                        "Insert Trailer number to delete",
                    ]

                case "Check In":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.check_in,
                    )

                    text_button = [
                        "Insert Trailer number",
                        "Sku",
                        "New LP",
                        "Number of boxes to move",
                    ]

                case "Add Orders":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.add_orders,
                    )

                    text_button = [
                        "Insert Wave Number",
                        "Insert Client ID",
                        "Insert Order Number (optional)",
                    ]

                case "Delete Order":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.delete_order,
                    )

                    text_button = [
                        "Insert Order Number",
                    ]

                case "Show Wave Pre-release":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.show_orders,
                    )

                    text_button = [
                        "Insert Wave Number",
                        "Insert Order Number",
                    ]

                case "Complete Move":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_complete_move,
                    )

                    text_button = ["Which LP you want to move?", "To which Location?"]

                case "Picking Move":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.print_picking_move,
                    )

                    text_button = ["Which is your User?"]

                case "Reset Move Assignment":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.reset_move_assign,
                    )

                    text_button = ["Which Move you want to reset? (Insert LP)"]

                case "Reset Order Assignment":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.reset_order_assign,
                    )

                    text_button = ["Which order you want to reset?"]

                case "Release Back Order":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.release_back_order,
                    )

                    text_button = [
                        "Insert Sku",
                        "Insert Order Number (optional)",
                    ]

                case "Reshape Locations":
                    sw_button = ttk.Button(
                        self.frame_0,
                        text=self.info_options_var.get(),
                        command=self.reshape_locations,
                    )

                    args = (
                        "Max Weight",
                        "Max Height",
                    )

                    args2 = ("New Max Weight", "New Max Height")

                    text_button = ["Which location would you like to reshape?"]

            # Primer Frame
            label_get_info = Label(
                self.frame_0,
                text=title,
                font=(MyGUI.f_label, 18, "bold"),
                foreground=MyGUI.c_SW_Letters,
                background=MyGUI.c_SW_Frame_2,
            )
            label_get_info.pack(padx=0, pady=5)
            ttk.Separator(
                self.frame_0,
                orient="horizontal",
            ).pack(padx=5, pady=5, fill="x")

            ff_text = []
            for row, val in enumerate(text_button):
                pair = (
                    Text(
                        self.frame_0,
                        height=1,
                        font=(MyGUI.f_text, 12),
                        foreground=MyGUI.c_SW_Letters,
                        background=MyGUI.c_SW_Labels,
                    ),
                    CTkLabel(
                        self.frame_0,
                        text=val,
                        font=(MyGUI.f_label, 14, "bold"),
                        text_color=MyGUI.c_SW_Letters,
                        fg_color=MyGUI.c_SW_Textbox1,
                        corner_radius=MyGUI.f1_radius,
                    ),
                )
                pair[0].bind("<Return>", sw_button["command"])
                pair[1].pack(padx=5, pady=5, fill="x")
                pair[0].pack(padx=5, pady=5)

                ff_text.append(pair)
            self.ff_text = ff_text
            self.ff_text[0][0].focus()
            sw_button.pack(padx=5, pady=5)
        sw_button

        try:
            if args:
                pass
        except UnboundLocalError:
            pass
        else:
            text_cells = []
            row = 0

            if not args2:
                colors = [MyGUI.c_SW_Textbox1, MyGUI.c_SW_Textbox2]
                for name in args:
                    frame = Frame(self.frame_1, width=200, height=100)
                    frame.config(background=colors[0])
                    frame.pack(fill="both", expand=FALSE)
                    colors[0], colors[1] = colors[1], colors[0]
                    Label(
                        frame,
                        text=name,
                        font=(MyGUI.f_label, 12),
                        bg=MyGUI.c_SW_Label_Args,
                        borderwidth=1,
                        relief="solid",
                        foreground=MyGUI.c_SW_Font,
                        width=14,
                        justify="left",
                        anchor="w",
                    ).grid(row=row, column=0, padx=5, pady=10, sticky=EW)

                    text = Text(
                        frame,
                        height=1,
                        font=(MyGUI.f_text, 8),
                        width=self.winfo_width() - 300,
                    )
                    text_cells.append(text)
                    text.grid(row=row, column=1, padx=5, pady=5, sticky=EW)
                    row += 1
            else:
                for name in args:
                    Label(
                        self.frame_1,
                        text=name,
                        font=(MyGUI.f_label, 12),
                        bg=MyGUI.c_SW_Label_Args,
                        borderwidth=1,
                        relief="solid",
                        foreground=MyGUI.c_SW_Font,
                    ).grid(row=row, column=0, padx=5, pady=10, sticky=EW)
                    text = Text(self.frame_1, height=1, font=(MyGUI.f_text, 8))
                    row += 1
                    text_cells.append(text)
                    text.grid(row=row, column=0, padx=5, pady=5, sticky=EW)
                    row += 1

                row = 0
                for name in args2:
                    Label(
                        self.frame_1,
                        text=name,
                        font=(MyGUI.f_label, 12),
                        bg=MyGUI.c_SW_Label_Args,
                        borderwidth=1,
                        relief="solid",
                        foreground=MyGUI.c_SW_Font,
                    ).grid(row=row, column=1, padx=5, pady=10, sticky=EW)
                    text = Text(self.frame_1, height=1, font=(MyGUI.f_text, 8))
                    row += 1
                    text_cells.append(text)
                    text.grid(row=row, column=1, padx=5, pady=5, sticky=EW)
                    row += 1
                self.frame_1.grid_columnconfigure(0, weight=1)
                self.frame_1.grid_columnconfigure(1, weight=1)

            self.text_cells = text_cells

    def decorator_factory(frame):
        def change_frame_color(f):
            def wrapper(self, *args, **kwargs):
                attr = getattr(self, frame)
                attr.configure(fg_color=MyGUI.c_SW_Frame_1)
                return f(self, *args, **kwargs)

            return wrapper

        return change_frame_color

    @staticmethod
    def del_children(widget: Widget) -> None:
        for child in widget.winfo_children():
            child.unbind("<Return>")
            child.destroy()

    @staticmethod
    def get_widgets_height(widget: Widget) -> int:
        widget.update_idletasks()
        count = 0

        for child in widget.winfo_children():
            count += child.winfo_height()
        return count

    def on_del_sw(self, og_window: Tk):
        if self in og_window.secondary_windows:
            og_window.secondary_windows.remove(self)
            og_window.sw_counter -= 1
        self.destroy()


    def release_order(self, test=None):
        company_code = self.ff_text[0][0].get("1.0", END).strip().upper()
        if company_code in [cc[1] for cc in MyGUI.config_data["CLIENTS"]] and not test:
            self.release_order_db(company_code)
        elif test:
            if company_code in [cc[1] for cc in MyGUI.config_data["CLIENTS"]]:
                return True
            else:
                return False
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Client dosnt exist",
                parent=self,
            ).show()
        self.ff_text[0][0].delete("1.0", END)

    def release_order_db(self, company_code):
        try:
            self.mycursor.callproc("pr_release_orders", (company_code,))
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            messagebox.Message(
                self, title=f"{self.name}", message="Success!!", parent=self
            ).show()
            self.mydb.commit()

    def pick_order(self, test=None):
        self.order = self.ff_text[0][0].get("1.0", END).strip()
        try:
            self.mycursor.callproc(
                "pr_check_order_employee", (self.order, self.username)
            )
            self.mycursor.execute("SELECT @result_o")
            canBe = self.mycursor.fetchone()[0]
            if canBe == "ISEMPTY" or canBe == self.username or canBe == None:
                self.mycursor.execute(
                    f"""SELECT sku, 
                                    num_boxes, 
                                    loc,
                                    state 
                                FROM Pick_list 
                                WHERE Pick_list.order_number = '{self.order}'"""
                )
                self.lines = self.mycursor.fetchall()
                self.pick_order_db()
            elif canBe != self.username:
                self.ff_text[0][0].delete("1.0", END)
                messagebox.Message(
                    self,
                    title=f"{self.name}",
                    message=f"User: {canBe} already on it!",
                    parent=self,
                ).show()
                return
        except mysql.connector.Error as err:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"That is not an order number. ",
                parent=self,
            ).show()
            return

    def pick_order_db(self, test=None):
        try:
            if not self.lines:
                raise AttributeError
            elif all([i[3] == "NR" for i in self.lines]) or all(
                [i[3] == "P" for i in self.lines]
            ):
                raise ValueError
        except AttributeError:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f'The order "{self.order}" is not in the system.',
                parent=self,
            ).show()
            return -1
        except ValueError:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"The state of the order is {self.lines[0][3]}",
                parent=self,
            ).show()
            return -2

        else:
            self.lines = [x for x in self.lines if x[3] != "P"]
            if test:
                return self.lines

            self.del_children(self.frame_0)
            self.draw_order()

    def draw_order(self, event=None):
        try:
            self.mycursor.execute(
                f"""UPDATE Pick_list SET Pick_list.Employee = '{self.username}' 
                                   WHERE Pick_list.order_number = '{self.order}'"""
            )
            self.mydb.commit()

            sku, num_boxes, location = self.lines[-1][:3]
            location = location.upper()
        except IndexError:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Order Complete!!",
                parent=self,
            ).show()
            self.draw_screen_script()

        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            self.del_children(self.frame_0)

            self.mycursor.execute(
                f"SELECT lp FROM lp_location_data WHERE position = '{location}'"
            )
            lp = self.mycursor.fetchall()[0][0]
            self.pick_data = (sku, num_boxes, location, lp)
            self.scan_label = Label(
                self.frame_0, text=f"Scan {location} or LP", font=(MyGUI.f_label, 12)
            )
            self.scan_label.pack(padx=5, pady=5, fill=Y)
            self.scan_text = Text(self.frame_0, height=1, font=(MyGUI.f_text, 12))
            self.scan_text.pack(padx=5, pady=5, fill=Y)

            self.scan_button = Button(
                self.frame_0, text="Check", command=self.check_picking
            )
            self.scan_button.pack(padx=5, pady=5, fill=Y)
            self.scan_text.bind("<Return>", self.check_picking)

    def check_picking(self, event=None):
        lp_or_loc = self.scan_text.get("1.0", END).strip().upper()
        if lp_or_loc in (self.pick_data[2], self.pick_data[3]):
            self.scan_text.unbind("<Return>")

            self.scan_label.destroy()
            self.scan_text.destroy()
            self.scan_button.destroy()

            self.scan_label = Label(
                self.frame_0,
                font=MyGUI.f_label,
                text=f"Put {self.pick_data[1]} boxes of SKU {self.pick_data[0]}\nIn order {self.order}\nPress Enter.",
            )
            self.scan_label.pack(padx=5, pady=5)
            self.scan_text = Text(self.frame_0, height=1, font=(MyGUI.f_label, 12))
            self.scan_text.pack(padx=5, pady=5)
            self.scan_button = Button(
                self.frame_0,
                text="Check",
                command=self.call_picking,
                font=MyGUI.f_button,
            )
            self.scan_button.pack(padx=5, pady=5)
            self.scan_text.bind("<Return>", self.call_picking)
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Not correct Location/LP",
                parent=self,
            ).show()
            self.scan_text.delete("1.0", END)

    def call_picking(self, event=None):
        self.mycursor.callproc(
            "pr_picking", (self.order, self.pick_data[2], self.pick_data[1])
        )
        self.mydb.commit()
        self.lines.pop()
        self.draw_order()

    @decorator_factory("frame_1")
    def search_sku(self):
        sku = self.ff_text[0][0].get("1.0", END).upper().strip(" \n")
        self.ff_text[0][0].delete("1.0", END)
        self.geometry("500x500")
        try:
            self.sheet.pack_forget()
        except AttributeError:
            pass
        try:
            sql = f"""SELECT position, sku, lp, num_boxes, num_allocated_boxes
                    FROM lp_location_data
                    WHERE sku = '{sku}'"""
            self.mycursor.execute(sql)
            data = self.mycursor.fetchall()
            if not data:
                raise AttributeError
        except mysql.connector.Error as err:
            self.frame_1.configure(fg_color="transparent")
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()

        except AttributeError:
            self.frame_1.configure(fg_color="transparent")
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"SKU: {sku} not in the system.",
                parent=self,
            ).show()

        else:
            header = ("Position", "Sku", "Lp", "Boxes", "Allocated boxes")
            self.geometry("750x700")
            displayed_data = [[i for i in data[j]] for j in range(len(data))]
            self.sheet = Sheet(
                self.frame_1,
                data=displayed_data,
                headers=header,
                header_bg=MyGUI.c_SW_Table_Header,
                align=CENTER,
                total_columns=len(header),
                height=250,
                column_width=400,
                auto_resize_columns=50,
            )
            self.sheet.hide_columns(range(len(self.sheet.headers()), 600))

            self.sheet.config(highlightbackground="BLACK")
            self.sheet.pack(fill="both", padx=20, pady=20)

    @decorator_factory("frame_1")
    def print_info_order(self):
        order = self.ff_text[0][0].get("1.0", END).strip().upper()
        self.ff_text[0][0].delete("1.0", END)
        try:
            self.sheet.pack_forget()
        except AttributeError:
            pass
        try:
            order = order.replace("*", "%")
            orders = [(x.strip(",")) for x in order.split(",")]

            sql = """SELECT order_number, sku, num_boxes, loc, state, employee
                        FROM Pick_list
                        WHERE order_number LIKE %s"""

            data = []
            for i in orders:
                self.mycursor.execute(sql, (i,))
                data.append(self.mycursor.fetchall())

            if len(data) > 1:
                data_var = []
                for i in data:
                    for j in i:
                        data_var.append(j)
                data = [data_var]
            if not data[0]:
                raise AttributeError
        except mysql.connector.Error as err:
            self.frame_1.configure(fg_color="transparent")
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        except AttributeError:
            self.frame_1.configure(fg_color="transparent")
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"Order: {order} not in the system.",
                parent=self,
            ).show()
        else:
            self.geometry("750x700")
            header = ("Order", "Sku", "Boxes", "Location", "State", "Employee")
            displayed_data = [[i for i in data[0][j]] for j in range(len(data[0]))]
            self.sheet = Sheet(
                self.frame_1,
                data=displayed_data,
                headers=header,
                header_bg=MyGUI.c_SW_Table_Header,
                align=CENTER,
                total_columns=len(header),
                column_width=400,
                auto_resize_columns=50,
            )

            self.sheet.hide_columns(range(len(self.sheet.headers()), 600))

            self.sheet.config(highlightbackground="BLACK")
            self.sheet.pack(fill="both", side=TOP, padx=20)

    @decorator_factory("frame_1")
    def print_moves(self):
        company_code = self.ff_text[0][0].get("1.0", END).strip().upper()
        self.ff_text[0][0].delete("1.0", END)
        if not company_code:
            return None
        try:
            self.sheet.pack_forget()
            self.update_button_employees.pack_forget()
        except AttributeError:
            pass
        try:
            sql = ""
            if company_code == "WA":
                sql = """SELECT company_code, 
                                Locations.position, 
                                Moves.future_position,
                                Moves.lp,
                                employee
                        FROM Moves LEFT JOIN Locations ON Moves.lp = Locations.lp"""
            elif company_code in [cc[1] for cc in MyGUI.config_data["CLIENTS"]]:
                sql = f"""SELECT company_code, 
                                Locations.position, 
                                Moves.future_position,
                                Moves.lp,
                                employee
                        FROM Moves LEFT JOIN Locations ON Moves.lp = Locations.lp
                        WHERE Moves.company_code = '{company_code}'"""
            self.mycursor.execute(sql)
            data = self.mycursor.fetchall()
            if not data:
                raise mysql.connector.Error
        except mysql.connector.Error:
            self.frame_1.configure(fg_color="transparent")
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"No moves for {company_code}",
                parent=self,
            ).show()
        else:
            header = ("Company Code", "Location", "Future Location", "LP", "Employee")
            self.geometry("700x700")
            display_data = [[i for i in data[j]] for j in range(len(data))]
            self.sheet = Sheet(
                self.frame_1,
                data=display_data,
                headers=header,
                header_bg=MyGUI.c_SW_Table_Header,
                align=CENTER,
                height=150,
                width=len(header) + 30,
                total_columns=len(header),
                column_width=400,
                auto_resize_columns=50,
            )

            self.sheet.enable_bindings(
                "copy",
                "arrowkeys",
                "column_select",
                "row_select",
                "single_select",
                "select_all",
                "edit_cell",
            )
            self.sheet.readonly(self.sheet.span("A:D", header=True), readonly=True)
            self.sheet.config(highlightbackground="BLACK")
            self.sheet.pack(fill="both", side=TOP, padx=20, pady=10)
            self.update_button_employees = Button(
                self.frame_1,
                text="Update database with Employees",
                command=self.moves_send_to_employee,
            )
            self.update_button_employees.pack(fill="both", side=TOP, padx=20, pady=20)

    @decorator_factory("frame_1")
    def print_partial_move(self):
        old_lp = self.ff_text[0][0].get("1.0", END).strip(" \n")
        new_lp = self.ff_text[1][0].get("1.0", END).strip(" \n")
        num_boxes = self.ff_text[2][0].get("1.0", END).strip(" \n")
        self.ff_text[0][0].delete("1.0", END)
        self.ff_text[1][0].delete("1.0", END)
        self.ff_text[2][0].delete("1.0", END)
        try:
            args = (old_lp, new_lp, num_boxes)
            self.mycursor.callproc("pr_partial_move", args)

        except mysql.connector.Error as err:
            self.frame_1.configure(fg_color="transparent")
            if str(err)[:4] == "1452":
                msg = "LP does not exist. "
            else:
                msg = err
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Partial move done successfully!",
                parent=self,
            ).show()
            self.mydb.commit()

    def print_complete_move(self):
        pos = self.ff_text[1][0].get("1.0", END).strip().upper()
        lp = self.ff_text[0][0].get("1.0", END).strip()
        self.ff_text[1][0].delete("1.0", END)
        self.ff_text[0][0].delete("1.0", END)
        try:
            aisle = pos[:3] + "%"
            self.mycursor.execute(
                f"SELECT ADR FROM Locations WHERE Position LIKE '{aisle}' LIMIT 1"
            )
            is_adr = self.mycursor.fetchone()[0]

            self.mycursor.execute(
                f"SELECT ADR FROM Products LEFT JOIN Lps ON Products.sku = Lps.sku WHERE Lps.lp = '{lp}' LIMIT 1"
            )
            is_product_adr = self.mycursor.fetchone()[0]

            if is_product_adr == "Y" and is_adr == "N":
                messagebox.Message(
                    self,
                    title=f"{self.name}",
                    message="Movement Not Allowed. Not ADR Location.",
                    parent=self,
                ).show()
                return None

            args = (pos, lp)
            self.mycursor.callproc("pr_complete_move", args)

        except mysql.connector.Error as err:
            if str(err)[:4] == "1452":
                msg = "LP does not exist. "
            if not pos:
                msg = "No location specified"
            else:
                msg = err
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
            self.mydb.commit()

        else:
            self.mycursor.execute(
                f"""SELECT sku, num_boxes, num_allocated_boxes 
                FROM lp_location_data
                WHERE lp = '{lp}' """
            )
            sku, num_boxes, num_alloc_boxes = self.mycursor.fetchall()[0]
            message = f"""LP: {lp} was moved to Location {pos}\n\t
                                                    -Sku:{sku}\n\t
                                                    -Number of boxes: {num_boxes}\n\t
                                                    -Number allocated boxes: {num_alloc_boxes}"""

            messagebox.Message(
                self, title=f"{self.name}", message=message, parent=self
            ).show()
            self.mydb.commit()

    @decorator_factory("frame_1")
    def print_picking_move(self):
        self.user = self.ff_text[0][0].get("1.0", END).strip()
        self.frame_1.configure(fg_color="transparent")
        try:
            self.mycursor.execute(
                f"""SELECT Moves.lp, 
                                    future_position, 
                                    Locations.position 
                                FROM Moves LEFT JOIN Locations
                                ON Moves.lp = Locations.lp
                                WHERE Employee = '{self.user}'"""
            )
            self.moves = self.mycursor.fetchall()
            if not self.moves:
                raise AttributeError
        except mysql.connector.Error as err:
            if str(err)[:4] == "1452":
                msg = "LP does not exist. "
            else:
                msg = err
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        except AttributeError:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"On user {self.user}, we have 0 moves.",
                parent=self,
            ).show()
            self.on_del_sw(self.father)
            self.destroy()
        else:
            self.del_children(self.frame_0)
            self.ask_lp_loc()

    def ask_lp_loc(self, event=None):
        try:
            if not self.moves:
                raise AttributeError
        except AttributeError:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"On user {self.user}, we have 0 moves.",
                parent=self,
            ).show()
        else:
            lp, self.future_location, self.location = self.moves[0]
            self.lp_and_loc = (lp, self.location)
            self.scan_label = Label(
                self.frame_0,
                text=f"Scan Location {self.location} or LP",
                font=MyGUI.f_label,
                background=MyGUI.c_SW_Labels,
            )
            self.scan_label.pack(padx=5, pady=5, fill=Y)
            self.scan_text = Text(self.frame_0, height=1, font=(MyGUI.f_text, 12))
            self.scan_text.pack(padx=5, pady=5, fill=Y)
            self.scan_button = Button(
                self.frame_0,
                text="Check",
                command=self.check_lp_loc,
                font=MyGUI.f_button,
            )
            self.scan_button.pack(padx=5, pady=5, fill=Y)
            self.scan_text.bind("<Return>", self.check_lp_loc)

    def check_lp_loc(self, event=None):
        lp_and_loc = self.lp_and_loc
        user_input = self.scan_text.get("1.0", END).strip().upper()
        if user_input in lp_and_loc:
            self.scan_text.unbind("<Return>")
            self.scan_label.destroy()
            self.scan_text.destroy()
            self.scan_button.destroy()

            self.mycursor.execute(
                f"SELECT adr FROM Products WHERE Products.sku = (SELECT sku FROM Lps WHERE Lp = '{lp_and_loc[0]}' LIMIT 1)"
            )
            is_adr = self.mycursor.fetchall()[0][0]
            self.mycursor.execute(
                f"SELECT position FROM Locations WHERE Locations.level = 'A' AND ADR = '{is_adr}' AND Locations.lp IS NULL LIMIT 1"
            )

            try:
                future_location = self.mycursor.fetchall()[0][0]
            except IndexError:
                messagebox.Message(
                    self,
                    title=f"{self.name}",
                    message="Not Enough 'A' level locations.",
                    parent=self,
                ).show()
                self.scan_text.delete("1.0", END)

            self.scan_label = Label(
                self.frame_0,
                text=f"Where to put Lp-> {lp_and_loc[0]}?\n{future_location} is free.",
                font=MyGUI.f_label,
            )
            self.scan_label.pack(padx=5, pady=5)
            self.scan_text = Text(self.frame_0, height=1, font=(MyGUI.f_text, 8))
            self.scan_text.pack(padx=5, pady=5)
            self.scan_button = Button(
                self.frame_0,
                text="Check",
                command=self.check_future_pos,
                font=MyGUI.f_button,
            )
            self.scan_button.pack(padx=5, pady=5)
            self.scan_text.bind("<Return>", self.check_future_pos)
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Not correct Location/LP",
                parent=self,
            ).show()
            self.scan_text.delete("1.0", END)

    def check_future_pos(self, event=None):
        future_loc = self.scan_text.get("1.0", END).strip(" \n")
        sql = f"SELECT Moves.lp FROM Moves LEFT JOIN Locations ON Moves.lp = Locations.lp WHERE Locations.position = '{self.location}'"

        try:
            self.mycursor.execute(sql)
            checker = self.mycursor.fetchall()[0][0]
            self.mycursor.callproc("pr_picking_move", (future_loc, checker))

            self.mydb.commit()

        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
            self.scan_text.delete("1.0", END)
        except IndexError as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
            self.scan_text.delete("1.0", END)
        else:
            self.scan_text.unbind("<Return>")
            self.del_children(self.frame_0)
            self.moves.pop(0)
            messagebox.Message(
                self, title=f"{self.name}", message="Success!", parent=self
            ).show()
            self.ask_lp_loc()

    @decorator_factory("frame_1")
    def print_check_trailer(self):
        trailer_id = self.ff_text[0][0].get("1.0", END).strip(" \n")
        self.ff_text[0][0].delete("1.0", END)
        try:
            self.mycursor.execute(
                f"""SELECT trailer_number,
                            company_code,
                            sku, 
                            num_boxes
                            FROM Trailers 
                            WHERE trailer_number like '{trailer_id}'"""
            )
            data = self.mycursor.fetchall()
            if not data:
                raise mysql.connector.Error
        except mysql.connector.Error:
            self.frame_1.configure(fg_color="transparent")
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Trailer not found.",
                parent=self,
            ).show()

        try:
            self.sheet.pack_forget()
        except AttributeError:
            pass
        finally:
            if data:
                header = (
                    "Trailer Number",
                    "Company Code",
                    "Sku",
                    "Number Of Boxes",
                )
                displayed_data = [[i for i in data[j]] for j in range(len(data))]
                self.sheet = Sheet(
                    self.frame_1,
                    data=displayed_data,
                    headers=header,
                    header_bg=MyGUI.c_SW_Table_Header,
                    align=CENTER,
                    total_columns=len(header),
                    column_width=400,
                    auto_resize_columns=50,
                )

                self.sheet.hide_columns(range(len(self.sheet.headers()), 600))
                self.sheet.enable_bindings("column_height_resize", False)
                self.sheet.enable_bindings("column_select", False)
                self.sheet.enable_bindings("column_width_resize", False)
                self.sheet.enable_bindings("column_drag_and_drop", False)
                self.sheet.set_options(table_layout="fixed")
                self.sheet.config(highlightbackground="BLACK")
                self.sheet.pack(fill="both", side=TOP, padx=20, pady=20)

                self.sheet.enable_bindings(
                    "copy",
                    "arrowkeys",
                    "column_select",
                    "row_select",
                    "single_select",
                    "select_all",
                )

    @decorator_factory("frame_1")
    def print_list_lp(self):
        self.text_cells[0].delete("1.0", END)
        self.text_cells[1].delete("1.0", END)
        self.text_cells[2].delete("1.0", END)
        self.text_cells[3].delete("1.0", END)
        self.text_cells[4].delete("1.0", END)
        self.text_cells[5].delete("1.0", END)
        self.text_cells[6].delete("1.0", END)
        self.text_cells[7].delete("1.0", END)
        lp = self.ff_text[0][0].get("1.0", END).strip()
        try:
            self.mycursor.execute(
                f"""SELECT 
                        lp_location_data.lp, 
                        Products.sku, 
                        Products.name,
                        lp_location_data.position, 
                        Products.company_code,
                        lp_location_data.num_boxes, 
                        lp_location_data.num_allocated_boxes,
                        Products.ADR 
                    FROM lp_location_data 
                    LEFT JOIN Products 
                    ON lp_location_data.sku = Products.sku
                    WHERE lp_location_data.lp =  '{lp}'"""
            )
            data = self.mycursor.fetchall()[0]
        except mysql.connector.Error:
            self.text_cells[0].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[4].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[5].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[6].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[7].insert(END, "ERROR, LP NOT FOUND")
        except IndexError:
            self.text_cells[0].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[4].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[5].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[6].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[7].insert(END, "ERROR, LP NOT FOUND")
        else:
            self.text_cells[0].insert(END, lp)
            self.text_cells[1].insert(END, data[1])
            self.text_cells[2].insert(END, data[2])
            self.text_cells[3].insert(END, data[3])
            self.text_cells[4].insert(END, data[4])
            self.text_cells[5].insert(END, data[6])
            self.text_cells[6].insert(END, data[5])
            self.text_cells[7].insert(END, data[7])
        self.ff_text[0][0].delete("1.0", END)

    @decorator_factory("frame_1")
    def print_list_loc(self):
        self.text_cells[0].delete("1.0", END)
        self.text_cells[1].delete("1.0", END)
        self.text_cells[2].delete("1.0", END)
        self.text_cells[3].delete("1.0", END)
        self.text_cells[4].delete("1.0", END)
        loc_code = self.ff_text[0][0].get("1.0", END).strip(" \n").upper()
        try:
            self.mycursor.execute(
                f"""SELECT *
                                FROM Lp_location_data  
                                WHERE position = '{loc_code}'"""
            )
            data = self.mycursor.fetchall()[0]

            if data[0] is None:
                raise FileNotFoundError
        except IndexError:
            self.text_cells[0].insert(END, "ERROR, LOC NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LOC NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LOC NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LOC NOT FOUND")
            self.text_cells[4].insert(END, "ERROR, LOC NOT FOUND")
        except mysql.connector.Error:
            self.text_cells[0].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LP NOT FOUND")
            self.text_cells[4].insert(END, "ERROR, LP NOT FOUND")
        except FileNotFoundError:
            self.text_cells[0].insert(END, "Empty location")
            self.text_cells[1].insert(END, "Empty location")
            self.text_cells[2].insert(END, "Empty location")
            self.text_cells[3].insert(END, "Empty location")
            self.text_cells[4].insert(END, "Empty location")

        else:
            self.text_cells[0].insert(END, loc_code)
            self.text_cells[1].insert(END, data[1])
            self.text_cells[2].insert(END, data[0])
            self.text_cells[3].insert(END, data[2])
            self.text_cells[4].insert(END, data[3])

    @decorator_factory("frame_1")
    def print_list_loc_info(self):
        self.text_cells[0].delete("1.0", END)
        self.text_cells[1].delete("1.0", END)
        self.text_cells[2].delete("1.0", END)
        self.text_cells[3].delete("1.0", END)
        self.text_cells[4].delete("1.0", END)
        self.text_cells[5].delete("1.0", END)

        try:
            location = self.ff_text[0][0].get("1.0", END).strip(" \n").upper()
            self.mycursor.execute(
                f"SELECT * FROM Locations WHERE position = '{location}'"
            )
            position, level, _, kg, cm, adr = self.mycursor.fetchall()[0]
            aisle, column, level = position.split("/")
        except ValueError:
            self.text_cells[0].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[4].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[5].insert(END, "ERROR, LOCATION NOT FOUND")
        else:
            self.text_cells[0].insert(END, aisle)
            self.text_cells[1].insert(END, column)
            self.text_cells[2].insert(END, level)
            self.text_cells[3].insert(END, f"{kg} Kg")
            self.text_cells[4].insert(END, f"{cm} Cm")
            self.text_cells[5].insert(END, adr)

    @decorator_factory("frame_1")
    def print_product_info(self):
        self.text_cells[0].delete("1.0", END)
        self.text_cells[1].delete("1.0", END)
        self.text_cells[2].delete("1.0", END)
        self.text_cells[3].delete("1.0", END)
        self.text_cells[4].delete("1.0", END)
        self.text_cells[5].delete("1.0", END)

        try:
            sku = self.ff_text[0][0].get("1.0", END).strip(" \n").upper()
            self.mycursor.execute(f"SELECT * FROM Products WHERE sku = '{sku}'")
            sku, name, boxes_pallet, cc, benefit, adr = self.mycursor.fetchall()[0]
        except ValueError:
            self.text_cells[0].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[4].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[5].insert(END, "ERROR, LOCATION NOT FOUND")
        else:
            self.text_cells[0].insert(END, sku)
            self.text_cells[1].insert(END, cc)
            self.text_cells[2].insert(END, name)
            self.text_cells[3].insert(END, f"{benefit:.2f}")
            self.text_cells[4].insert(END, boxes_pallet)
            self.text_cells[5].insert(END, adr)

    @decorator_factory("frame_1")
    def reshape_locations(self):
        location = self.ff_text[0][0].get("1.0", END).strip().upper()
        new_weight = self.text_cells[2].get("1.0", END).strip()
        new_height = self.text_cells[3].get("1.0", END).strip()
        self.text_cells[0].bind("<Return>", lambda event: "break")
        self.text_cells[1].bind("<Return>", lambda event: "break")
        self.text_cells[2].bind("<Return>", lambda event: "break")
        self.text_cells[3].bind("<Return>", lambda event: "break")
        self.text_cells[0].delete("1.0", END)
        self.text_cells[1].delete("1.0", END)
        self.text_cells[2].delete("1.0", END)
        self.text_cells[3].delete("1.0", END)

        if (new_height or new_weight) and location:
            if new_height.isnumeric() and new_weight.isnumeric():
                sql = f"""UPDATE Locations SET max_weight = {new_weight}, max_height = {new_height} 
                                WHERE Locations.position = '{location}'"""
            elif new_height.isnumeric():
                sql = f"""UPDATE Locations SET max_height = {new_height} 
                                WHERE Locations.position = '{location}'"""
            elif new_weight.isnumeric():
                sql = f"""UPDATE Locations SET max_weight = {new_weight} 
                                WHERE Locations.position = '{location}'"""

            self.mycursor.execute(sql)
            self.mydb.commit()

            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"Changes applied to location {location}",
                parent=self,
            ).show()

        try:
            self.mycursor.execute(
                f"""SELECT max_weight,
                            max_height FROM Locations
                            WHERE position = '{location}'"""
            )
            data = self.mycursor.fetchall()[0]
        except IndexError:
            self.text_cells[0].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LOCATION NOT FOUND")
        except ValueError:
            self.text_cells[0].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[1].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[2].insert(END, "ERROR, LOCATION NOT FOUND")
            self.text_cells[3].insert(END, "ERROR, LOCATION NOT FOUND")
        except mysql.connector.Error as err:
            self.text_cells[0].insert(END, err)
            self.text_cells[1].insert(END, err)
            self.text_cells[2].insert(END, err)
            self.text_cells[3].insert(END, err)
        else:
            self.text_cells[0].insert(END, data[0])
            self.text_cells[1].insert(END, data[1])

    def get_trailer(self):
        trailer_number = self.ff_text[0][0].get("1.0", END)
        data = trailer_in(trailer_number[:-1])
        self.ff_text[0][0].delete("1.0", END)
        if len(data) != 2:
            messagebox.Message(
                self, title=f"{self.name}", message=data, parent=self
            ).show()
        else:
            data, trailer_number = data
            try:
                update_trailer_info(data, trailer_number, self.mycursor, self.mydb)
            except mysql.connector.Error as err:
                messagebox.Message(
                    self, title=f"{self.name}", message=err, parent=self
                ).show()

            else:
                messagebox.Message(
                    self,
                    title=f"{self.name}",
                    message=f"Trailer: '{trailer_number} has arrived!'",
                    parent=self,
                ).show()
                data[0][-1] = "IN"
                with open(rf"trailer\{trailer_number}.csv", "w", newline="") as f:
                    writer = csv.writer(f, delimiter=",")
                    writer.writerows(data)

    def delete_trailer(self):
        trailer_number = self.ff_text[0][0].get("1.0", END).strip(" \n")
        self.ff_text[0][0].delete("1.0", END)
        try:
            self.mycursor.execute(
                f"SELECT id FROM Trailers WHERE Trailers.trailer_number = '{trailer_number}' LIMIT 1"
            )
            data = self.mycursor.fetchall()
            if data:
                self.mycursor.callproc("pr_delete_trailer", (trailer_number,))
                self.mydb.commit()
                msg = (f"Trailer {trailer_number} has been deleted.",)
            else:
                msg = (f"Trailer {trailer_number} not in the system.",)
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=msg,
                parent=self,
            ).show()

    def check_in(self):
        trailer_number = self.ff_text[0][0].get("1.0", END)
        sku = self.ff_text[1][0].get("1.0", END)
        new_lp = self.ff_text[2][0].get("1.0", END)
        num_boxes = self.ff_text[3][0].get("1.0", END)

        try:
            values = trailer_number[:-1], int(sku), new_lp[:-1], int(num_boxes)
            self.mycursor.callproc("pr_check_in", (values))
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        except ValueError as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            message = f"""LP: {new_lp}
                                -Sku:{sku}
                                -Number of boxes: {num_boxes}
            """

            messagebox.Message(
                self, title=f"{self.name}", message=message, parent=self
            ).show()
            self.mydb.commit()

    def add_orders(self):
        try:
            wave_number = self.ff_text[0][0].get("1.0", END).strip(" \n")
            client_id = self.ff_text[1][0].get("1.0", END).strip(" \n")
            order_number = self.ff_text[2][0].get("1.0", END).strip(" \n")
        except NameError:
            error = orders_in(
                self.mycursor, self.mydb, client_id=client_id, wave_number=wave_number
            )
        else:
            error = orders_in(
                self.mycursor, self.mydb, order_number, client_id, wave_number
            )
        self.ff_text[0][0].delete("1.0", END)
        self.ff_text[1][0].delete("1.0", END)
        if error:
            messagebox.Message(
                self, title=f"{self.name}", message=error, parent=self
            ).show()
        else:
            msg = f"Ordere/s from wave: {wave_number} added to the system."
            messagebox.Message(
                self, title=f"{self.name}", message=msg, parent=self
            ).show()

    def delete_order(self):
        order = self.ff_text[0][0].get("1.0", END).strip(" \n")
        self.ff_text[0][0].delete("1.0", END)
        try:
            self.mycursor.execute(
                f"""SELECT order_number FROM Products_bufe
            WHERE order_number = {order}"""
            )
            data = self.mycursor.fetchone()
            if not data:
                raise ValueError

            self.mycursor.callproc("pr_delete_order", (order,))
            self.mydb.commit()
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()

        except ValueError:
            err = f"Order '{order}' not in the system."
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"Order {order} has been taken out of the system.",
                parent=self,
            ).show()

    @decorator_factory("frame_1")
    def show_orders(self):
        wave_number = self.ff_text[0][0].get("1.0", END).strip(" \n").replace("*", "%")
        order_number = self.ff_text[1][0].get("1.0", END).strip(" \n").replace("*", "%")
        self.ff_text[0][0].delete("1.0", END)
        self.ff_text[1][0].delete("1.0", END)
        try:
            if wave_number and order_number:
                self.mycursor.execute(
                    f"""SELECT wave_number,
                                order_number,
                                sku, 
                                num_boxes
                                FROM Products_bufe 
                                WHERE Products_bufe.wave_number
                                LIKE '{wave_number}' AND 
                                Products_bufe.order_number LIKE {order_number}"""
                )
            elif order_number:
                self.mycursor.execute(
                    f"""SELECT wave_number,
                                order_number,
                                sku, 
                                num_boxes
                                FROM Products_bufe 
                                WHERE Products_bufe.order_number
                                LIKE '{order_number}'"""
                )
            elif wave_number:
                self.mycursor.execute(
                    f"""SELECT wave_number,
                                order_number,
                                sku, 
                                num_boxes
                                FROM Products_bufe 
                                WHERE Products_bufe.wave_number
                                LIKE '{wave_number}'"""
                )

            data = self.mycursor.fetchall()
            if not data:
                raise mysql.connector.Error
            self.sheet.pack_forget()
        except mysql.connector.Error as err:
            self.frame_1.configure(fg_color="transparent")
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        except AttributeError:
            pass
        finally:
            if data:
                header = (
                    "Wave Number",
                    "Order_number",
                    "Sku",
                    "Number Of Boxes",
                )
                displayed_data = [[i for i in data[j]] for j in range(len(data))]

                self.sheet = Sheet(
                    self.frame_1,
                    data=displayed_data,
                    headers=header,
                    header_bg=MyGUI.c_SW_Table_Header,
                    align=CENTER,
                    total_columns=len(header),
                    column_width=400,
                    auto_resize_columns=50,
                )

                self.sheet.enable_bindings(
                    "copy",
                    "arrowkeys",
                    "column_select",
                    "row_select",
                    "single_select",
                    "select_all",
                )

                self.sheet.hide_columns(range(len(self.sheet.headers()), 600))
                self.sheet.config(highlightbackground="BLACK")
                self.sheet.pack(fill="both", side=TOP, padx=20, pady=20)

    def reset_order_assign(self):
        order_num = self.ff_text[0][0].get("1.0", END).strip(" \n")

        try:
            self.mycursor.execute(
                f"""UPDATE Pick_list SET Pick_list.Employee = NULL 
                                   WHERE Pick_list.order_number = '{order_num}'"""
            )
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"Order with number {order_num} reseted.",
                parent=self,
            ).show()
            self.mydb.commit()

    def moves_send_to_employee(self):
        span_employees = self.sheet["E"].data
        span_lps = self.sheet["D"].data
        if not span_employees:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="No employees were updated. ",
                parent=self,
            ).show()
            return

        if isinstance(span_lps, str):
            unfiltered_list = []
            unfiltered_list.append((span_employees, span_lps))
        else:
            unfiltered_list = list(zip(span_employees, span_lps))
        filtered_list = [i for i in unfiltered_list if i[0] is not None]
        moves_taken = []
        for index, lp in list(enumerate(filtered_list)):
            self.mycursor.callproc("pr_check_move_employee", (lp[1], lp[0].upper()))
            self.mycursor.execute("SELECT @result_m")
            current_emp = self.mycursor.fetchone()

            if current_emp[0] != "ISEMPTY":
                moves_taken.append((index, lp))

            upper_item = list(filtered_list[index])
            upper_item[0] = upper_item[0].upper()
            filtered_list.remove(filtered_list[index])
            filtered_list.insert(index, tuple(upper_item))

        if moves_taken:
            msg = "The following moves are already taken: \n"
            moves_taken.reverse()
            for move in moves_taken:
                msg += f"-Move LP {move[1][1]} by {move[1][0]}\n"
                filtered_list.pop(move[0])
            messagebox.Message(
                self, title=f"{self.name}", message=msg, parent=self
            ).show()

        sql = "UPDATE Moves SET Moves.employee = %s WHERE Moves.lp = %s"
        self.mycursor.executemany(sql, filtered_list)
        self.mydb.commit()
        messagebox.Message(
            self,
            title=f"{self.name}",
            message="Moves Sended to their users.",
            parent=self,
        ).show()

    def reset_move_assign(self):
        move_lp = self.ff_text[0][0].get("1.0", END).strip(" \n")

        try:
            self.mycursor.execute(
                f"""UPDATE Moves SET Moves.Employee = NULL 
                                   WHERE Moves.lp = '{move_lp}'"""
            )
        except mysql.connector.Error as err:
            messagebox.Message(
                self, title=f"{self.name}", message=err, parent=self
            ).show()
        else:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message=f"Move with lp {move_lp} updated.",
                parent=self,
            ).show()
            self.mydb.commit()

    def release_back_order(self):
        sku = self.ff_text[0][0].get("1.0", END).strip(" \n")
        order_number = self.ff_text[1][0].get("1.0", END).strip(" \n")

        data = []
        if order_number:
            self.mycursor.execute(
                f"SELECT sku FROM back_orders WHERE backorder_number = '{order_number}' LIMIT 1"
            )
            data = self.mycursor.fetchall()[0][0]
            sku = data

        elif sku:
            self.mycursor.execute(
                f"SELECT id FROM back_orders WHERE sku = '{sku}' LIMIT 1"
            )
            data = self.mycursor.fetchall()

        if not data:
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="No data found.",
                parent=self,
            ).show()
            self.ff_text[0][0].delete("1.0", END)
            self.ff_text[1][0].delete("1.0", END)
            return

        if not order_number:
            order_number = 0
        self.mycursor.callproc(
            "pr_check_enough_boxes",
            (
                sku,
                order_number,
            ),
        )
        self.mycursor.execute("SELECT @can_be_picked")
        respose = self.mycursor.fetchone()[0]

        if respose == "Y":
            if order_number != 0:
                self.mycursor.execute(
                    f"""
                    INSERT INTO Products_bufe (order_number, sku, num_boxes)              
                        SELECT Back_orders.backorder_number, Back_orders.sku, Back_orders.num_boxes FROM
                            Back_orders WHERE Back_orders.backorder_number = {order_number}
                                AND Back_orders.sku = {sku};
                """
                )
                self.mycursor.execute(
                    f"""
                    DELETE FROM Back_orders WHERE Back_orders.backorder_number = {order_number}
                        AND Back_orders.sku = {sku};
                
                """
                )
            else:
                self.mycursor.execute(
                    f"""
                    INSERT INTO Products_bufe (order_number, sku, num_boxes)              
                        SELECT Back_orders.backorder_number, Back_orders.sku, Back_orders.num_boxes FROM
                            Back_orders WHERE Back_orders.sku = {sku};
                """
                )
                self.mycursor.execute(
                    f"""
                    DELETE FROM Back_orders WHERE Back_orders.sku = {sku};
                """
                )
            self.mydb.commit()

            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Back orders released, let`s pick!!",
                parent=self,
            ).show()

        elif respose == "N":
            messagebox.Message(
                self,
                title=f"{self.name}",
                message="Not enough boxes to satisfy all the orders.",
                parent=self,
            ).show()


# Warehouse Creation
def mfwh_db(mydb, mycursor, providers, products, level_range):
    clients = ""
    for i in providers:
        clients += f"'{i[1]}', "
    levels = ""
    for i in level_range:
        levels += f"'{i}',"
    # Proveedores e info
    tables = [
        f"""CREATE TABLE Providers ( 
                company_code VARCHAR(10) PRIMARY KEY UNIQUE,
                name VARCHAR(30))""",
        f"""CREATE TABLE Contact_Providers(
                company_code VARCHAR(10),
                telefono VARCHAR(15), 
                email VARCHAR(75), 
                CONSTRAINT FK_contactP FOREIGN KEY(company_code) references Providers(company_code))""",
        """CREATE TABLE Customers (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                country VARCHAR(30), 
                postal_code VARCHAR(12))""",
        """CREATE TABLE Contact_Customers (
                contact_id INT, 
                telefono VARCHAR(15), 
                email VARCHAR(75), 
                CONSTRAINT FK_contactC FOREIGN KEY(contact_id) references Customers(id))""",
        f"""CREATE TABLE Products (
                sku INT PRIMARY KEY, 
                name VARCHAR(40), 
                num_boxes_per_pallet INT, 
                company_code VARCHAR(10),
                benefit FLOAT, 
                ADR ENUM('Y','N'), 
                CONSTRAINT FK_prod_cc_prov FOREIGN KEY(company_code) references Providers(company_code))""",
        """CREATE TABLE Lps (
                lp VARCHAR(12) PRIMARY KEY, 
                sku INT,
                num_boxes INT DEFAULT 0,
                num_allocated_boxes INT DEFAULT 0,
                on_loc ENUM('Y','N'), 
                employee VARCHAR(20),
                CONSTRAINT FK_lps_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        """CREATE TABLE Sales (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                date DATE, 
                sku INT,
                num_boxes INT, 
                CONSTRAINT FK_sales_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        """CREATE TABLE Locations ( 
                position VARCHAR(8) PRIMARY KEY, 
                level CHAR,
                lp VARCHAR(12),
                max_weight INT,
                max_height INT,
                ADR ENUM('Y','N'),
                CONSTRAINT FK_loc_lp_lps FOREIGN KEY(lp) references Lps(lp) 
                ON DELETE SET NULL)""",
        f"""CREATE TABLE Moves (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lp VARCHAR(12) UNIQUE, 
                future_position VARCHAR(8), 
                employee VARCHAR(20),
                company_code VARCHAR(10),
                CONSTRAINT FK_mv_lp_lps FOREIGN KEY(lp) references Lps(lp),
                CONSTRAINT FK_mv_cc_prov FOREIGN KEY(company_code) references Providers(company_code),
                CONSTRAINT FK_mv_fpos_loc FOREIGN KEY(future_position) references Locations(position))""",
        """CREATE TABLE Products_bufe (
                id INT AUTO_INCREMENT PRIMARY KEY,
                wave_number VARCHAR(16),
                order_number VARCHAR(12),
                sku INT,
                num_boxes INT,
                fecha DATE,
                added VARCHAR(1),
                CONSTRAINT FK_pb_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        f"""CREATE TABLE Back_orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku INT,  
                num_boxes INT, 
                backorder_number VARCHAR(12), 
                fecha DATE,
                CONSTRAINT FK_bord_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        f"""CREATE TABLE Pick_list (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                company_code VARCHAR(10), 
                order_number VARCHAR(12), 
                sku INT, 
                num_boxes INT, 
                state ENUM('NR','WM','NP', 'P') DEFAULT 'NR', 
                loc VARCHAR(8),
                lp VARCHAR(12),
                employee VARCHAR(20),
                CONSTRAINT FK_pickl_cc_prov FOREIGN KEY(company_code) references Providers(company_code),
                CONSTRAINT FK_pickl_sku_prod FOREIGN KEY(sku) references Products(sku),
                CONSTRAINT FK_pickl_loc_locs FOREIGN KEY(loc) references Locations(position))""",
        f"""CREATE TABLE Trailers(
                id INT AUTO_INCREMENT PRIMARY KEY,
                trailer_number VARCHAR(16),
                sku INT,
                num_boxes INT,
                company_code VARCHAR(10),
                fecha DATE,
                CONSTRAINT FK_tr_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        """CREATE VIEW Lp_location_data AS 
                SELECT Lps.lp AS lp, 
                    Lps.sku AS sku, 
                    Lps.num_boxes AS num_boxes, 
                    Lps.num_allocated_boxes AS num_allocated_boxes,
                    Locations.position AS position, 
                    Locations.level AS level
                FROM Lps RIGHT JOIN Locations 
                ON Lps.lp = Locations.lp;""",
        """CREATE VIEW Sales_info AS 
                SELECT Sales.id AS Order_id, 
                    Sales.date AS Date, 
                    Sales.sku AS SKU, 
                    Sales.num_boxes AS Num_boxes,
                    ROUND(Products.benefit, 2) AS Single_unit_benefit,
                    ROUND(Sales.num_boxes * Products.benefit, 2) as Total_benefit,
                    Products.company_code 
                FROM Sales LEFT JOIN Products 
                ON Sales.sku = Products.sku;""",
    ]

    for table in tables:
        mycursor.execute(table)

    # Triggers
    mycursor.execute(
        """CREATE TRIGGER tr_write_lp_on_loc
                AFTER INSERT ON Lps 
                FOR EACH ROW 
                BEGIN 
                    DECLARE check_on_location INT;
                    DECLARE random_position VARCHAR(8);
                    
                    SELECT COUNT(position) INTO check_on_location
                    FROM Locations WHERE Locations.lp = NEW.lp LIMIT 1;

                    IF (NEW.on_loc = 'Y' AND check_on_location != 1) THEN
                        SELECT Locations.position INTO random_position FROM Locations
                        WHERE Locations.lp IS NULL
                        ORDER BY RAND()
                        LIMIT 1; 

                        UPDATE Locations SET Locations.lp = NEW.lp
                        WHERE Locations.position = random_position;
                    END IF;
                END;"""
    )

    mycursor.execute(
        """CREATE TRIGGER tr_write_lp
                BEFORE INSERT ON Lps 
                FOR EACH ROW 
                BEGIN 
                    DECLARE last_id INT;
                    SELECT COUNT(lp) INTO last_id FROM Lps;
                    IF (NEW.lp IS NULL) THEN 
                        SET NEW.lp = CONCAT(last_id, '-', NEW.sku);
                    END IF;
                END;"""
    )
    """
    mycursor.execute(
        f CREATE TRIGGER tr_check_moves
            BEFORE UPDATE ON Lps
            FOR EACH ROW 
            BEGIN 
                DECLARE level_var ENUM({levels[:-1]});
                SELECT level INTO level_var 
                    FROM Locations 
                    WHERE Locations.Lp = NEW.lp;

                IF (level_var != '{level_range[0]}' AND NEW.num_allocated_boxes > 0) THEN
                    CALL pr_create_move(NEW.lp);
                END IF;
            END;
    )
    """
    mycursor.execute(
        """CREATE TRIGGER tr_assign_cc 
            BEFORE INSERT ON Pick_list
            FOR EACH ROW
            BEGIN
                DECLARE new_company_code VARCHAR(10);
                SELECT company_code INTO new_company_code
                FROM Products 
                WHERE SKU = NEW.sku;
                SET NEW.company_code = new_company_code;
            END;"""
    )

    mycursor.execute(
        """CREATE TRIGGER tr_assign_cc_moves
            BEFORE INSERT ON Moves
            FOR EACH ROW
            BEGIN
                DECLARE new_company_code VARCHAR(10);
                SELECT company_code INTO new_company_code
                FROM Products RIGHT JOIN Lps
                ON Products.Sku = Lps.sku
                WHERE Lps.lp = NEW.lp;
                SET NEW.company_code = new_company_code;
            END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_complete_move(
                IN new_position VARCHAR(8),
                IN lp_to_move VARCHAR(12))
                BEGIN    
                    CALL pr_check_lp_exists(lp_to_move);
                    CALL pr_check_empty(new_position);
                    CALL pr_check_allocated_boxes(lp_to_move, @allocated_boxes);
                    IF (@allocated_boxes > 0) THEN
                        SIGNAL SQLSTATE '47000' SET MESSAGE_TEXT = 'NOT POSSIBLE MOVE ALLOCATED PRODUCTS';
                    END IF;

                    UPDATE Locations SET Locations.lp = NULL WHERE Locations.lp = lp_to_move;
                    UPDATE Locations SET Locations.lp = lp_to_move WHERE Locations.position = new_position;
                    UPDATE Lps SET Lps.on_loc = 'Y' WHERE Lps.lp = lp_to_move;
                END;"""
    )

    mycursor.execute(
        f"""CREATE PROCEDURE IF NOT EXISTS pr_picking_move(
                IN new_position VARCHAR(8),
                IN lp_to_move VARCHAR(12))
                BEGIN    
                    DECLARE level_var CHAR;
                    DECLARE old_loc VARCHAR(8);
                    SELECT level INTO level_var FROM Locations WHERE position = new_position;  
                    SELECT position INTO old_loc FROM Locations WHERE lp = lp_to_move;
                    CALL pr_check_empty(new_position);
                    
                    IF (level_var != '{level_range[0]}') THEN    
                        SIGNAL SQLSTATE '47000' SET MESSAGE_TEXT = 'NOT "A" LEVEL LOCATION';
                    END IF;

                    UPDATE Locations SET Locations.lp = NULL WHERE Locations.lp = lp_to_move;
                    UPDATE Locations SET Locations.lp = lp_to_move WHERE Locations.position = new_position;
                    DELETE FROM Moves WHERE lp = lp_to_move;
                END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_partial_move(
                IN old_lp VARCHAR(12),
                IN new_lp VARCHAR(12),
                IN num_boxes_to_move INT)
                BEGIN    
                    DECLARE not_alloc_boxes INT;
                    DECLARE pm_sku INT;
                    DECLARE boxes_lp INT;
                    SELECT num_boxes INTO not_alloc_boxes FROM Lps WHERE Lps.lp = old_lp;
                    SELECT sku INTO pm_sku FROM Lps WHERE Lps.lp = old_lp;

                    CALL pr_check_lp_exists(old_lp);
                    IF (num_boxes_to_move > not_alloc_boxes) THEN
                        SIGNAL SQLSTATE '49000' SET MESSAGE_TEXT = 'NOT ENOUGH MOVABLE BOXES';
                    END IF;

                    INSERT INTO Lps (lp, sku, num_boxes) 
                    VALUES (new_lp, pm_sku, num_boxes_to_move);
                    UPDATE Lps SET Lps.num_boxes = Lps.num_boxes - num_boxes_to_move WHERE Lps.lp = old_lp;

                    CALL pr_delete_empty_lp();
                END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_in(
                IN trailer_number VARCHAR(16),
                IN var_sku INT,
                IN new_lp VARCHAR(12),
                IN num_boxes_to_move INT)
                BEGIN    
                    DECLARE total_boxes INT;

                    SELECT num_boxes INTO total_boxes FROM Trailers 
                        WHERE Trailers.trailer_number = trailer_number AND Trailers.sku = var_sku;

                    CALL pr_check_lp_not_exists(new_lp);
                    
                    IF (total_boxes IS NULL) THEN
                        SIGNAL SQLSTATE '85000' SET MESSAGE_TEXT = 'TRAILER NOT FOUND';
                    END IF;

                    IF (num_boxes_to_move > total_boxes) THEN
                        SIGNAL SQLSTATE '85000' SET MESSAGE_TEXT = 'NOT ENOUGH BOXES';
                    END IF;

                    UPDATE Trailers SET Trailers.num_boxes = total_boxes - num_boxes_to_move 
                        WHERE Trailers.trailer_number = trailer_number AND Trailers.sku = var_sku;
                        
                    IF (num_boxes_to_move = total_boxes) THEN
                        DELETE FROM Trailers WHERE Trailers.num_boxes = 0;
                    END IF;


                    INSERT INTO Lps (lp, sku, num_boxes) 
                    VALUES (new_lp, var_sku, num_boxes_to_move);


                END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_allocated_boxes(
                    IN lp VARCHAR(12),
                    OUT return_value INT)
                        BEGIN    
                            DECLARE allocated_boxes INT;
                            SELECT num_allocated_boxes INTO allocated_boxes FROM Lps WHERE Lps.lp = lp;
                            SET return_value = allocated_boxes;
                            SELECT return_value;
                        END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_delete_empty_lp()
            BEGIN
                DELETE FROM Lps WHERE num_boxes = 0 AND num_allocated_boxes = 0;
            END; """
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_delete_trailer(
                    IN trailer VARCHAR(16)
                    )
                        BEGIN    
                            DELETE FROM Trailers WHERE Trailers.trailer_number = trailer;
                        END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_delete_order(
                    IN order_number VARCHAR(12)
                    )
                        BEGIN    
                            DELETE FROM Products_bufe WHERE Products_bufe.order_number= order_number;
                            DELETE FROM Pick_list WHERE Pick_list.order_number= order_number;
                        END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_empty(
                IN check_position VARCHAR(8))
                    BEGIN   
                        DECLARE check_empty VARCHAR(12);
                        SELECT lp INTO check_empty 
                        FROM lp_location_data
                        WHERE position = check_position;
                                
                        IF (check_empty IS NOT NULL) THEN
                            SIGNAL SQLSTATE '46000' SET MESSAGE_TEXT = 'LOCATION NOT EMPTY';
                        END IF;
                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_order_employee(
                IN check_order VARCHAR(8),
                IN employee VARCHAR(20))
                    BEGIN   
                        DECLARE check_empty VARCHAR(20);
                        SELECT Pick_list.employee INTO check_empty 
                        FROM Pick_list
                        WHERE Pick_list.order_number = check_order LIMIT 1;
                        
                        IF check_empty IS NULL THEN
                            SET @result_o = 'ISEMPTY';
                        ELSE 
                            SET @result_o = check_empty;
                        END IF;

                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_move_employee(
                IN lp VARCHAR(12),
                IN employee VARCHAR(20))
                    BEGIN   
                        DECLARE check_empty VARCHAR(20);
                        SELECT Moves.employee INTO check_empty 
                        FROM Moves
                        WHERE Moves.lp = lp LIMIT 1;

                        IF check_empty IS NULL THEN
                            SET @result_m = 'ISEMPTY';
                        ELSEIF check_empty = employee THEN
                            SET @result_m = 'ISEMPTY';
                        ELSE 
                            SET @result_m = check_empty;
                        END IF;

                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_released(
                IN order_number VARCHAR(12))
                    BEGIN   
                        DECLARE check_var ENUM('NR','NP','P');
                        DECLARE _message_var VARCHAR(128);
                        SELECT state INTO check_var 
                        FROM Pick_list
                        WHERE Pick_list.order_number = order_number LIMIT 1;
                                
                        IF (check_var <> 'NP') THEN
                            SELECT CONCAT('ERROR,  STATE: ', check_var) INTO _message_var;
                            SIGNAL SQLSTATE '40000' SET MESSAGE_TEXT = _message_var;
                        END IF;
                    END;"""
    )
    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_lp_exists(
                IN check_lp VARCHAR(12))
                    BEGIN   
                        DECLARE check_empty VARCHAR(12);
                        SELECT lp INTO check_empty 
                        FROM Lps
                        WHERE lp = check_lp;
                                
                        IF (check_empty IS NULL) THEN
                            SIGNAL SQLSTATE '50000' SET MESSAGE_TEXT = 'LP DOES NOT EXIST';
                        END IF;
                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_lp_not_exists(
                IN check_lp VARCHAR(12))
                    BEGIN   
                        DECLARE check_empty VARCHAR(12);
                        SELECT lp INTO check_empty 
                        FROM Lps
                        WHERE lp = check_lp;
                                
                        IF (check_empty IS NOT NULL) THEN
                            SIGNAL SQLSTATE '50000' SET MESSAGE_TEXT = 'LP DOES EXIST';
                        END IF;
                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_picking(
                IN order_number VARCHAR(12),
                IN pick_location VARCHAR(8),
                IN num_boxes INT)
                    BEGIN
                        DECLARE lp_from_location VARCHAR(12);
                        DECLARE order_num_state VARCHAR(2);
                        SELECT state INTO order_num_state FROM Pick_list WHERE Pick_list.order_number = order_number LIMIT 1;

                        SELECT lp INTO lp_from_location FROM lp_location_data WHERE position = pick_location;
                        UPDATE Pick_list SET Pick_list.state = 'P' WHERE Pick_list.order_number = order_number AND Pick_list.loc = pick_location;
                        UPDATE Lps SET Lps.num_allocated_boxes = Lps.num_allocated_boxes - num_boxes  WHERE Lps.lp = lp_from_location;

                        CALL pr_delete_empty_lp();
                    END;"""
    )

    mycursor.execute(
        f"""CREATE PROCEDURE IF NOT EXISTS pr_release_orders(
            IN client ENUM({clients[:-2]}, 'WA')
        )
                    BEGIN
                        DECLARE checker INT;
                        DECLARE _error_message VARCHAR(128);
                        DECLARE orders_left INT;

                        IF client = 'WA' THEN
                            SELECT COUNT(id) INTO checker FROM Moves;
                        ELSE
                            SELECT COUNT(id) INTO checker FROM Moves WHERE Moves.company_code = client;
                        END IF;

                        SELECT id INTO orders_left FROM Pick_list 
                            WHERE Pick_list.company_code = client AND 
                            Pick_list.state = 'NR' LIMIT 1;
                        
                        IF orders_left IS NULL THEN 
                            SELECT CONCAT('The client ', client, ' does not have orders left to release' ) INTO _error_message;
                            SIGNAL SQLSTATE '41000'
                            SET MESSAGE_TEXT = _error_message; 
                        END IF;
                        
                        CASE
                            WHEN (checker != 0) THEN
                                SELECT CONCAT('STILL HAVE ', checker, ' MOVES TO DO FOR ', client) INTO _error_message;
                                SIGNAL SQLSTATE '41000' SET MESSAGE_TEXT = _error_message;
                            WHEN (checker = 0) THEN
                                IF client = 'WA' THEN
                                    UPDATE Pick_list SET state = 'NP';
                                ELSE
                                    UPDATE Pick_list SET state = 'NP'
                                    WHERE Pick_list.company_code = client;
                                END IF;
                            END CASE;
                    END;"""
    )

    mycursor.execute(
        f"""CREATE PROCEDURE IF NOT EXISTS pr_check_enough_boxes(
            IN new_sku INT,
            IN new_order INT )
          
                    BEGIN
                        DECLARE total_boxes_in_wh INT;
                        DECLARE total_boxes_to_pick INT;

                        SELECT SUM(num_boxes) INTO total_boxes_in_wh
                            FROM lp_location_data WHERE lp_location_data.sku = new_sku;
                        
                        IF new_order = 0 THEN
                            SELECT SUM(num_boxes) INTO total_boxes_to_pick
                                FROM back_orders WHERE back_orders.sku = new_sku;
                        ELSE
                            SELECT SUM(num_boxes) INTO total_boxes_to_pick
                                FROM back_orders WHERE back_orders.sku = new_sku 
                                    AND back_orders.backorder_number = new_order;
                        END IF;

                        IF total_boxes_in_wh < total_boxes_to_pick THEN
                            SET @can_be_picked = 'N';
                        ELSE 
                            SET @can_be_picked = 'Y';
                        END IF;
                    END;
    """
    )


def mfwh_db_insert_providers_products(mydb, mycursor, providers, products):
    sql = "INSERT INTO Providers (name, company_code) VALUES (%s, %s)"
    mycursor.executemany(sql, providers)
    mydb.commit()

    sql = "INSERT INTO Products (sku, name, num_boxes_per_pallet, company_code, benefit, ADR) VALUES (%s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql, products)
    mydb.commit()


def mfwh_digital_warehouse(AISLES, ROWS, LEVELS):
    # Location (aisle, position, level, state )
    warehouse = {}
    AISLE_INFO = list(zip(zip(AISLES, ROWS), LEVELS))
    for row_info in AISLE_INFO:
        warehouse[row_info[0][0]] = []
        for _ in range(1, row_info[0][1] + 1):
            row = [f"{row_info[0][0][0]}/{_}/{level}" for level in row_info[1]]
            warehouse[row_info[0][0]].append(row)
    return warehouse


def insert_digital_warehouse(warehouse, mydb, levels):
    aisle_count = 0
    mycursor = mydb.cursor()
    sql = "INSERT INTO locations (position, level, max_weight, max_height, ADR) VALUES (%s, %s, %s, %s, %s)"
    for aisle in warehouse:
        for col in warehouse[aisle]:
            for loc in col:
                level = loc[-1]
                mycursor.execute(
                    sql,
                    (
                        loc,
                        level,
                        levels[aisle_count][level]["Weight"],
                        levels[aisle_count][level]["Height"],
                        aisle[1],
                    ),
                )
        aisle_count += 1

    mydb.commit()


def fill_locations(mydb):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT sku, num_boxes_per_pallet FROM Products")
    result = mycursor.fetchall()
    products = [i[0] for i in result]
    num_boxes = [i[1] for i in result]
    products.append(None)

    mycursor.execute("SELECT COUNT(position) FROM Locations")
    count = mycursor.fetchall()[0][0] + 2

    total = [
        i
        for i in numpy.random.choice(
            products,
            p=[
                0.1,
                0.07,
                0.07,
                0.04,
                0.05,
                0.05,
                0.05,
                0.02,
                0.06,
                0.12,
                0.12,
                0.04,
                0.02,
                0.02,
                0.05,
                0.02,
                0.10,
            ],
            size=count - 20,
        )
    ]

    for product in products:
        if product not in total:
            for index, _ in enumerate(total):
                if total[index] == None:
                    total[index] = product
                break

    for _, sku in enumerate(total):
        if sku is not None:
            mycursor.execute(
                "INSERT INTO Lps(sku, num_boxes, on_loc) VALUES(%s, %s, %s)",
                (sku, num_boxes[products.index(sku)], "Y"),
            )
    mydb.commit()


def get_orders(mydb, loop):
    mycursor = mydb.cursor()
    orders_k, orders_j, orders_r, orders_s = [
        random.randint(30, 60),
        random.randint(10, 30),
        random.randint(80, 90),
        random.randint(0, 2),
    ]
    clients_data = [
        ("KD", orders_k),
        ("JW", orders_j),
        ("RC", orders_r),
        ("SCP", orders_s),
    ]

    all_orders = {"KD": {}, "JW": {}, "RC": {}, "SCP": {}}
    count = 1112

    while loop:
        for client in clients_data:
            mycursor.execute(
                "SELECT sku, num_boxes_per_pallet FROM Products WHERE company_code = %s",
                (client[0],),
            )
            result = mycursor.fetchall()
            products = [i[0] for i in result]
            num_boxes = [i[1] for i in result]
            for _ in range(client[1]):
                match client[0]:
                    case "KD":
                        num_lines = random.randint(1, 4)
                    case "JW":
                        num_lines = random.randint(1, 2)
                    case "RC":
                        num_lines = random.randint(1, 4)
                    case "SCP":
                        num_lines = 1
                all_orders[client[0]][count] = {}
                for _ in range(num_lines):
                    choice = random.randint(0, len(products) - 1)
                    if products[choice] not in all_orders[client[0]][count]:
                        all_orders[client[0]][count][products[choice]] = random.randint(
                            max(1, int(num_boxes[choice] / 10)),
                            max(1, int(num_boxes[choice] / 2)),
                        )
                    else:
                        all_orders[client[0]][count][
                            products[choice]
                        ] += random.randint(
                            max(1, int(num_boxes[choice] / 10)),
                            max(1, int(num_boxes[choice] / 2)),
                        )

                count += 1
        loop -= 1
    return all_orders


def get_orders_date(mydb, dates):
    mycursor = mydb.cursor()
    orders_k, orders_j, orders_r, orders_s = [
        random.randint(10, 20),
        random.randint(1, 3),
        random.randint(8, 14),
        random.randint(0, 2),
    ]
    clients_data = [
        ("KD", orders_k),
        ("JW", orders_j),
        ("RC", orders_r),
        ("SCP", orders_s),
    ]

    all_orders = {}
    count = 1112

    for date in dates:
        all_orders[date] = {"KD": {}, "JW": {}, "RC": {}, "SCP": {}}
        for client in clients_data:
            mycursor.execute(
                "SELECT sku, num_boxes_per_pallet FROM Products WHERE company_code = %s",
                (client[0],),
            )
            result = mycursor.fetchall()
            products = [i[0] for i in result]
            num_boxes = [i[1] for i in result]
            for _ in range(client[1]):
                match client[0]:
                    case "KD":
                        num_lines = random.randint(1, 4)
                    case "JW":
                        num_lines = random.randint(1, 2)
                    case "RC":
                        num_lines = random.randint(1, 4)
                    case "SCP":
                        num_lines = 1

                all_orders[date][client[0]][count] = {}
                for _ in range(num_lines):
                    choice = random.randint(0, len(products) - 1)
                    if products[choice] not in all_orders[date][client[0]][count]:
                        all_orders[date][client[0]][count][
                            products[choice]
                        ] = random.randint(
                            max(1, int(num_boxes[choice] / 10)),
                            max(1, int(num_boxes[choice] / 2)),
                        )
                    else:
                        all_orders[date][client[0]][count][
                            products[choice]
                        ] += random.randint(
                            max(1, int(num_boxes[choice] / 10)),
                            max(1, int(num_boxes[choice] / 2)),
                        )
                count += 1
    return all_orders


def fill_orders(mydb, orders: dict) -> None:
    mycursor = mydb.cursor()
    for _, v in orders.items():
        for order_num, products in v.items():
            for i in products:
                sku = i
                num_boxes = products[i]
                sql = "INSERT INTO Products_bufe (order_number, sku, num_boxes, added) VALUES(%s, %s, %s, %s)"
                values = (order_num, sku, num_boxes, "N")
                mycursor.execute(sql, values)
                mydb.commit()


def filling():
    dates = pandas.date_range(start="20210101", end="20220101", freq="D")
    return dates.date


def insert_dates(mycursor, mydb, orders):
    sql = "INSERT INTO Sales (date, sku, num_boxes) VALUES (%s,%s,%s)"
    for date, company_code in orders.items():
        for company_code, order_info in company_code.items():
            for order_number, lines in order_info.items():
                for sku, num_boxes in lines.items():
                    mycursor.execute(sql, (date, sku, num_boxes))
    mydb.commit()


def trailer_in(trailer_number):
    data = []
    try:
        with open(rf"trailer\{trailer_number}.csv", newline="") as f:
            spamreader = csv.reader(f, delimiter=",")
            for row in spamreader:
                data.append(row)

    except FileNotFoundError:
        return f"Error, trailer '{trailer_number}' not found."
    else:
        trailer_state = data[0][-1].strip()
        if trailer_state == "NOT IN":
            return data, trailer_number
        elif trailer_state == "IN":
            return f"Already in the system"
        else:
            return f"Trailer state: '{trailer_state}' not in expected states."


def order_files(client_ids):
    for client_id in client_ids:
        path = rf"orders\{client_id[1]}_orders"
        if not os.path.exists(path):
            os.makedirs(path)
            os.makedirs(rf"{path}\to_be_done")
            os.makedirs(rf"{path}\done")
        with open(
            rf"orders/{client_id[1]}_orders/{client_id[1]}_orders_TEST.csv",
            "w",
            newline="",
        ) as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Client ID", "Order Number", "SKU", "Num Boxes", "Status"])


def orders_in(mycursor, mydb, order_number=None, client_id=None, wave_number=None):
    try:
        data = []
        path = rf"orders/{client_id}_orders/to_be_done/{client_id}_orders_{wave_number}.csv"
        with open(path, newline="") as f:
            spamreader = csv.reader(f, delimiter=",")
            for row in spamreader:
                data.append(row)

    except FileNotFoundError:
        return f"Error, file with '{client_id}' orders not found."
    else:
        indexed_data = list(enumerate(data))

    if order_number:
        values = [
            order
            for order in indexed_data
            if order[1][1] == str(order_number) and len(order[1][1]) < 12
        ]
    else:
        values = indexed_data[1:]
        values = [order for order in values if len(order[1][1]) < 12]
    checker = [x for x in values if x[1][4] == "NP"]
    if not checker:
        return "Not orders with correct status"

    sql = "INSERT INTO Products_bufe (order_number, wave_number, sku, num_boxes, fecha, added) VALUES(%s, %s, %s, %s, %s, %s)"

    for index, order in checker:
        mycursor.execute(
            sql, (order[1], wave_number, order[2], order[3], datetime.date.today(), "N")
        )
        mydb.commit()
        data[index][4] = "P"

    update_orders_csv(data, wave_number, path)


def update_orders_csv(new_data, wave_number, path):
    if all([order for order in new_data[1:] if order[4] == "P"]):
        os.remove(path)
        client_id = new_data[1][0]
        path = rf"orders/{client_id}_orders/done/{client_id}_orders_{wave_number}.csv"

    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerows(new_data)


def update_trailer_info(data, trailer_number, mycursor, mydb):
    sql = "INSERT INTO Trailers(sku, num_boxes, company_code, fecha, trailer_number) VALUES(%s, %s, %s, %s, %s)"
    for i in data[1:]:
        mycursor.execute(sql, (i[1], i[2], i[0], datetime.date.today(), trailer_number))
    mydb.commit()


def warehouse_mainloop():
    with open(r".config\config_database.json", "r") as f:
        config_data = json.load(f)

    conexion = config_data["CONEXION"]
    providers = config_data["CLIENTS"]
    products = config_data["PRODUCTS"]
    warehouse_name = config_data["INFO"]["name"]
    level_range = list(
        max(
            ([x["Levels"].keys() for x in config_data["WAREHOUSE_DIMENSIONS"].values()])
        )
    )

    mydb, mycursor = create_connection(
        host=conexion["host"],
        user=conexion["user"],
        password=conexion["password"],
        port=conexion["port"],
        name=warehouse_name,
    )

    mfwh_db(mydb, mycursor, providers, products, level_range)
    mfwh_db_insert_providers_products(mydb, mycursor, providers, products)
    aisles = [x for x in config_data["WAREHOUSE_DIMENSIONS"].keys()]
    adr = [x["ADR"] for x in config_data["WAREHOUSE_DIMENSIONS"].values()]
    aisles = list(zip(aisles, adr))
    rows = [x["Rows"] for x in config_data["WAREHOUSE_DIMENSIONS"].values()]
    levels = [x["Levels"] for x in config_data["WAREHOUSE_DIMENSIONS"].values()]

    digital_warehouse = mfwh_digital_warehouse(aisles, rows, levels)
    insert_digital_warehouse(digital_warehouse, mydb, levels)

    fill_locations(mydb)
    orders = get_orders(mydb, 1)

    fill_orders(mydb, orders)
    #allocate_boxes()


def allocate_boxes():
    with open(r".config\config_database.json", "r") as f:
        config_data = json.load(f)
    conexion = config_data["CONEXION"]

    mydb = mysql.connector.connect(
        host=conexion["host"],
        user=conexion["user"],
        password=conexion["password"],
        port=conexion["port"],
        database=conexion["database"],
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT COALESCE((SELECT id FROM Moves LIMIT 1), 0)")
    moves = mycursor.fetchall()[0][0]

    if moves != 0:
        return "Still moves to be done!"




    mycursor.execute(
        "SELECT order_number, sku, num_boxes FROM Products_bufe WHERE added = 'N'"
    )
    data = mycursor.fetchall()

    groups = {}
    singles = []

    # First, combine tuples with the same order number and SKU
    for order, sku, boxes in data:
        key = (order, sku)
        if key in groups:
            groups[key] = [order, sku, groups[key][2] + boxes]
        else:
            groups[key] = [order, sku, boxes]

    # Now, group by order number
    order_groups = {}
    for (order, sku), value in groups.items():
        if order in order_groups:
            order_groups[order].append(value)
        else:
            order_groups[order] = [value]

    # Separate into grouped and single tuples
    grouped = []
    for order, items in order_groups.items():
        if len(items) > 1:
            grouped.append(list(items))
        else:
            singles.extend(items)
  
    for order in grouped:
        data_locations = []
        for line in order:
            mycursor.execute(
                f"SELECT COALESCE((SELECT position FROM lp_location_data WHERE sku = {line[1]} AND lp_location_data.num_boxes > {line[2]} AND level = 'A'  LIMIT 1), 0)"
            )
            data = mycursor.fetchone()

            try:
                mycursor.execute(
                    f"SELECT COALESCE((SELECT lp FROM lp_location_data WHERE position = '{data[0]}'), 0)"
                )
                lp = mycursor.fetchone()
                print("LP: ", lp)

                if lp[0] == '0':
                    raise TypeError
                info_position = (data[0], lp[0])

                data_locations.append(info_position)
            except TypeError:
                mycursor.execute(f"SELECT COALESCE((SELECT SUM(num_boxes) FROM lp_location_data WHERE sku = {line[1]}  AND level = 'A'), 0)")
                total_boxes_A_level = mycursor.fetchall()
                if len(total_boxes_A_level) > 0 and total_boxes_A_level[0][0] > line[2]:
                    while line[2] > 0:
                        mycursor.execute(
                            f"SELECT position, lp, num_boxes FROM lp_location_data WHERE sku = {line[1]} AND level = 'A'  AND num_boxes != 0 ORDER BY num_boxes LIMIT 1"
                        )
                        total_info = mycursor.fetchall()
                        print(total_info, line[2])
                        position, lp, num_boxes = total_info[0]
                        if line[2] >= num_boxes:
                            order.append([line[0], line[1], num_boxes])
                            line[2] -= num_boxes
                        else:
                            order.append([line[0], line[1], line[2]])
                            line[2] = 0
                            order = [order for order in order if order[2]>0]
                    continue
                else:
                    mycursor.execute(
                        f"SELECT COALESCE((SELECT lp FROM lp_location_data WHERE sku = {line[1]} AND level != 'A' ORDER BY num_boxes DESC LIMIT 1), 0)"
                    )
                    lp_from_bulk = mycursor.fetchall()
                    print("lp from the bulk", lp_from_bulk)
                    if lp_from_bulk [0][0] != "0":
                        mycursor.execute(f"UPDATE Lps SET num_boxes = num_boxes - {line[2]}, num_allocated_boxes = num_allocated_boxes + {line[2]} WHERE Lp = '{lp_from_bulk[0][0]}'")
                        mydb.commit()
                        try:
                            print(lp_from_bulk, " premove")
                            mycursor.execute( f"INSERT INTO pick_list(order_number, sku, num_boxes, state,  lp) VALUES ({line[0]}, {line[1]}, {line[2]}, 'WM', '{lp_from_bulk[0][0]}')"
                            )
                            mydb.commit()
                            mycursor.execute(
                                f"INSERT INTO Moves (lp) VALUES ('{lp_from_bulk[0][0]}')"
                            )
                            print(lp_from_bulk, " Postmove")
                            mydb.commit()

                        #This error is if there is a move already done for that. 
                        except mysql.connector.Error as err:
                            print(err)
                            pass
                        break

                    sql = "INSERT INTO back_orders(backorder_number, sku, num_boxes) VALUES (%s,%s,%s)"
                    mycursor.executemany(sql, order)
                    mydb.commit()
                    groups = [x for x in groups if x[0] != order[0]]
                    break

            # Means we have everything in A level.
            if line == order[-1]:
                sql = "INSERT INTO pick_list(order_number, sku, num_boxes, state, loc, lp) VALUES (%s,%s,%s,%s,%s,%s)"
                info_line = list(zip(order, data_locations))
                for data in info_line:
                    print(data)
                    mycursor.execute(
                        sql, (data[0][0], data[0][1], data[0][2], "NR", data[1][0], data[1][1])
                    )
                    mydb.commit()
                    mycursor.execute(
                        f"UPDATE Lps SET num_boxes = num_boxes - {data[0][2]}, num_allocated_boxes = num_allocated_boxes + {data[0][2]} WHERE Lp = '{data[1][1]}'"
                    )
                    mydb.commit()
                    
                    mycursor.execute(
                        f"UPDATE Products_bufe SET added = 'Y 'WHERE order_number = '{data[0][0]}'"
                    )
                    mydb.commit()

    print("before singles")
    for order in singles:
        mycursor.execute(f"SELECT SUM(num_boxes) FROM lp_location_data WHERE sku = {order[1]}  AND level = 'A'")
        try:
            total_boxes_A_level = int(mycursor.fetchall()[0][0])
        except: 
            sql = "INSERT INTO back_orders(backorder_number, sku, num_boxes) VALUES (%s,%s,%s)"
            mycursor.execute(sql, order)
            mydb.commit()
            continue
        if total_boxes_A_level < order[2]:
            #print(f"Total boxes: {total_boxes_A_level} and orderboxes {order[2]}")
            sql = "INSERT INTO back_orders(backorder_number, sku, num_boxes) VALUES (%s,%s,%s)"
            mycursor.execute(sql, order)
            mydb.commit()
            continue
        print(f"Total boxes: {total_boxes_A_level} and boxes to pick {order[2]}, sku = {order[1]}")
        while order[2] > 0:
            mycursor.execute(
                f"SELECT position, lp, num_boxes FROM lp_location_data WHERE sku = {order[1]} AND level = 'A'  AND num_boxes != 0 ORDER BY num_boxes LIMIT 1"
            )
            try:
                total_info = mycursor.fetchall()
                print("Total info ", total_info)
                position, lp, num_boxes = total_info[0]
            except IndexError as err:
                print(err)
                print(order)

            if num_boxes <= order[2]:

                sql = "INSERT INTO pick_list(order_number, sku, num_boxes, state, loc) VALUES (%s,%s,%s,%s,%s)"
                mycursor.execute(
                        sql, (order[0], order[1], num_boxes, "NR", position)
                    )
                mydb.commit()

                mycursor.execute(
                    f"UPDATE Lps SET num_boxes = 0, num_allocated_boxes = num_allocated_boxes + {num_boxes} WHERE Lp = '{lp}'"
                    )
                mydb.commit()
                order[2] -= num_boxes
            else:
                sql = "INSERT INTO pick_list(order_number, sku, num_boxes, state, loc) VALUES (%s,%s,%s,%s,%s)"
                mycursor.execute(
                        sql, (order[0], order[1], order[2], "NR", position)
                    )
                mydb.commit()

                mycursor.execute(
                    f"UPDATE Lps SET num_boxes = 0, num_allocated_boxes = num_allocated_boxes + {order[2]} WHERE Lp = '{lp}'"
                    )
                mydb.commit()
                order[2] = 0
        
    return "Orders Released."

        

def main():
    with open(r".config\config_database.json", "r") as f:
        config_data = json.load(f)

    warehouse_mainloop()
    MyGUI("lmao").mainloop()


if __name__ == "__main__":
    main()
