import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from collections import deque

# Core classes and data from UASPBOKEL1.py adapted for GUI (simplified slightly for integration)

registered_users = []
kurir_terdaftar = []
menu_resto = {}
pesanan_queue = deque()
pesanan_history = {}
daftar_semua_pesanan = []
pesanan_kurir = {}

class user:
    def __init__(self, userID='', nama='', email='', password='', alamat='', noHp=''):
        self.userID = userID
        self.nama = nama
        self.email = email
        self.password = password
        self.alamat = alamat
        self.noHp = noHp

class restoran(user):
    def __init__(self, userID, nama, email, password, alamat, noHp, namaResto, lokasi):
        super().__init__(userID, nama, email, password, alamat, noHp)
        self.namaResto = namaResto
        self.lokasi = lokasi
        if self.userID not in menu_resto:
            menu_resto[self.userID] = [
                MenuMakanan("M001", "Nasi Goreng", "Nasi goreng spesial", 15000, True, self.userID),
                MenuMakanan("M002", "Mie Ayam", "Mie ayam dengan topping lengkap", 12000, True, self.userID),
                MenuMakanan("M003", "Sate Ayam", "Sate ayam dengan bumbu kacang", 20000, True, self.userID),
                MenuMakanan("M004", "Es Teh Manis", "Es teh manis segar", 5000, True, self.userID)
            ]  
    
    def check_login(self, email, password):
        return self.email == email and self.password == password

    def get_menu(self):
        return menu_resto.get(self.userID, [])

    def add_menu_item(self, menu_item):
        if self.userID not in menu_resto:
            menu_resto[self.userID] = []
        menu_resto[self.userID].append(menu_item)

    def update_menu_item(self, index, namaMakanan=None, deskripsi=None, harga=None, ketersediaan=None):
        menu_list = menu_resto.get(self.userID, [])
        if 0 <= index < len(menu_list):
            menu_list[index].updateMenu(namaMakanan, deskripsi, harga, ketersediaan)
            return True
        return False

    def delete_menu_item(self, index):
        menu_list = menu_resto.get(self.userID, [])
        if 0 <= index < len(menu_list):
            del menu_list[index]
            return True
        return False

    def list_orders(self):
        # Return list of orders for this restaurant from daftar_semua_pesanan
        return [p for p in daftar_semua_pesanan if p.idRestoran == self.userID]

    def process_next_order(self):
        if pesanan_queue:
            pesanan = pesanan_queue.popleft()
            pesanan.updateStatusPesanan("Siap Diambil")
            if "pending_kurir" not in pesanan_kurir:
                pesanan_kurir["pending_kurir"] = deque()
            pesanan_kurir["pending_kurir"].append(pesanan)
            return pesanan
        return None

class pelanggan(user):
    def register(self, nama, email, password, alamat, noHp):
        self.nama = nama
        self.email = email
        self.password = password
        self.alamat = alamat
        self.noHp = noHp
        self.userID = f"P{len(registered_users) + 1:03d}"

        new_user = {
            'userID': self.userID,
            'nama': self.nama,
            'email': self.email,
            'password': self.password,
            'alamat': self.alamat,
            'noHp': self.noHp
        }
        registered_users.append(new_user)
        return True

    def login(self, email, password):
        for user in registered_users:
            if user['email'] == email and user['password'] == password:
                self.userID = user['userID']
                self.nama = user['nama']
                self.email = user['email']
                self.password = user['password']
                self.alamat = user['alamat']
                self.noHp = user['noHp']
                return True
        return False

    def pesan_makanan(self, namaResto, pilihan_idx, jumlah, restoran_list):
        for resto in restoran_list:
            if resto.namaResto == namaResto:
                if resto.userID not in menu_resto or not menu_resto[resto.userID]:
                    return None, "Menu tidak tersedia di restoran ini."
                if not (0 <= pilihan_idx < len(menu_resto[resto.userID])):
                    return None, "Nomor menu tidak valid!"
                menu_dipilih = menu_resto[resto.userID][pilihan_idx]
                if not menu_dipilih.ketersediaan:
                    return None, "Maaf, menu ini sedang tidak tersedia."
                if jumlah <= 0:
                    return None, "Jumlah pesanan harus lebih dari 0!"
                total_harga = jumlah * menu_dipilih.harga
                pesanan = Pesanan(
                    idPelanggan=self.userID,
                    idRestoran=resto.userID,
                    makanan=menu_dipilih.namaMakanan,
                    harga=total_harga,
                )
                pesanan_queue.append(pesanan)
                daftar_semua_pesanan.append(pesanan)
                if self.nama not in pesanan_history:
                    pesanan_history[self.nama] = []
                pesanan_history[self.nama].append(pesanan)
                return pesanan, None
        return None, "Restoran tidak ditemukan."

    def list_orders(self):
        return [p for p in daftar_semua_pesanan if p.idPelanggan == self.userID]

    def bayar_pesanan(self, pesanan_id, metode_pembayaran):
        orders_to_pay = pesanan_history.get("pending_payment", [])
        for pesanan in orders_to_pay:
            if pesanan.idPelanggan == self.userID and pesanan.pesananID == pesanan_id:
                pembayaran = Pembayaran(
                    pembayaranID=f"PAY{len(orders_to_pay):03d}",
                    metode=metode_pembayaran,
                    status="Pending",
                    tanggalBayar=datetime.now(),
                    idPesanan=pesanan.pesananID,
                )
                pembayaran.konfirmasiPembayaran()
                pesanan.updateStatusPesanan("Sudah Dibayar")
                orders_to_pay.remove(pesanan)
                return True, pesanan
        return False, None

class kurir(user):
    def register(self, nama, email, password, alamat, noHp):
        self.nama = nama
        self.email = email
        self.password = password
        self.alamat = alamat
        self.noHp = noHp
        self.userID = f"K{len(kurir_terdaftar) + 1:03d}"

        new_kurir = {
            'userID': self.userID,
            'nama': self.nama,
            'email': self.email,
            'password': self.password,
            'alamat': self.alamat,
            'noHp': self.noHp
        }
        kurir_terdaftar.append(new_kurir)
        return True

    def login(self, nama, idKurir):
        for k in kurir_terdaftar:
            if k['nama'] == nama and k['userID'] == idKurir:
                self.userID = k['userID']
                self.nama = k['nama']
                self.email = k['email']
                self.password = k['password']
                self.alamat = k['alamat']
                self.noHp = k['noHp']
                return True
        return False

    def ambil_pesanan(self):
        if "pending_kurir" in pesanan_kurir and pesanan_kurir["pending_kurir"]:
            if self.nama not in pesanan_kurir:
                pesanan_kurir[self.nama] = deque()
            pesanan = pesanan_kurir["pending_kurir"].popleft()
            pesanan.idKurir = self.userID
            pesanan.updateStatusPesanan("Diantar")
            pesanan_kurir[self.nama].append(pesanan)
            return pesanan
        return None

    def selesaikan_pesanan(self):
        if self.nama not in pesanan_kurir or not pesanan_kurir[self.nama]:
            return None
        pesanan = pesanan_kurir[self.nama].popleft()
        pesanan.updateStatusPesanan("Menunggu pembayaran")
        if "pending_payment" not in pesanan_history:
            pesanan_history["pending_payment"] = []
        pesanan_history["pending_payment"].append(pesanan)
        return pesanan

class MenuMakanan:
    def __init__(self, menuID, namaMakanan, deskripsi, harga, ketersediaan, idRestoran):
        self.menuID = menuID
        self.namaMakanan = namaMakanan
        self.deskripsi = deskripsi
        self.harga = harga
        self.ketersediaan = ketersediaan
        self.idRestoran = idRestoran
    def updateMenu(self, namaMakanan=None, deskripsi=None, harga=None, ketersediaan=None):
        if namaMakanan:
            self.namaMakanan = namaMakanan
        if deskripsi:
            self.deskripsi = deskripsi
        if harga:
            self.harga = harga
        if ketersediaan is not None:
            self.ketersediaan = ketersediaan
    def __str__(self):
        return f"{self.menuID}: {self.namaMakanan} - Rp{self.harga}, {'Tersedia' if self.ketersediaan else 'Tidak Tersedia'}"

class Pesanan:
    id_counter = 1
    def __init__(self, idPelanggan, idRestoran, makanan, harga, idKurir=None):
        self.pesananID = f"PSN{Pesanan.id_counter:03d}"
        Pesanan.id_counter += 1
        self.tanggalPesan = datetime.now()
        self.totalHarga = harga
        self.statusPesanan = "Menunggu"
        self.idPelanggan = idPelanggan
        self.idRestoran = idRestoran
        self.idKurir = idKurir
        self.makanan = makanan
    def updateStatusPesanan(self, statusBaru):
        self.statusPesanan = statusBaru
    def __str__(self):
        tanggal = self.tanggalPesan.strftime("%d-%m-%Y %H:%M")
        return f"{self.pesananID} | {self.makanan} | Restoran {self.idRestoran} | {tanggal} | Status: {self.statusPesanan}"

class Pembayaran:
    def __init__(self, pembayaranID, metode, status, tanggalBayar, idPesanan):
        self.pembayaranID = pembayaranID
        self.metode = metode
        self.status = status
        self.tanggalBayar = tanggalBayar
        self.idPesanan = idPesanan
    def konfirmasiPembayaran(self):
        self.status = "Terkonfirmasi"


# Predefined restaurants
restoran_list = [
    restoran("R001", "Admin Padang", "resto@Padang", "pass123", "Sumut", "03222323", "RM Padang", "Lokasi A"),
    restoran("R002", "Admin Aero", "restoB@Aero", "pass456", "Ketintang", "03222324", "RM Aero", "Lokasi B"),
    restoran("R003", "Admin JayaBakti", "restoC@JBakti", "pass789", "Surabaya", "03222325", "RM JayaBakti", "Lokasi C")
]

# GUI implementation using tkinter
class EFoodApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Pemesanan E-Food")
        self.geometry("720x1560")
        self.resizable(False, False)
        self.active_pelanggan = None
        self.active_restoran = None
        self.active_kurir = None

        self.create_main_menu()

    def create_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Sistem Pemesanan E-Food", font=("Arial", 24)).pack(pady=20)
        tk.Label(self, text="Pilih login:", font=("Arial", 16)).pack(pady=10)

        btn_pelanggan = tk.Button(self, text="Login Pelanggan", width=20, command=self.pelanggan_login_screen)
        btn_pelanggan.pack(pady=5)
        btn_restoran = tk.Button(self, text="Login Restoran", width=20, command=self.restoran_login_screen)
        btn_restoran.pack(pady=5)
        btn_kurir = tk.Button(self, text="Login Kurir", width=20, command=self.kurir_login_screen)
        btn_kurir.pack(pady=5)
        btn_exit = tk.Button(self, text="Keluar", width=20, command=self.destroy)
        btn_exit.pack(pady=20)

    # ======= Pelanggan Screens =============
    def pelanggan_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Login Pelanggan", font=("Arial", 20)).pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Email:").grid(row=0, column=0, sticky="e")
        entry_email = tk.Entry(frame, width=30)
        entry_email.grid(row=0, column=1, pady=5)
        tk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e")
        entry_password = tk.Entry(frame, show="*", width=30)
        entry_password.grid(row=1, column=1, pady=5)

        def do_login():
            email = entry_email.get().strip()
            password = entry_password.get().strip()
            user_obj = pelanggan()
            if user_obj.login(email, password):
                self.active_pelanggan = user_obj
                messagebox.showinfo("Sukses", f"Login Berhasil! Selamat datang {user_obj.nama}")
                self.pelanggan_menu()
            else:
                messagebox.showerror("Gagal", "Email atau password salah.")

        btn_login = tk.Button(self, text="Login", command=do_login)
        btn_login.pack(pady=10)

        btn_register = tk.Button(self, text="Register", command=self.pelanggan_register_screen)
        btn_register.pack(pady=5)

        btn_back = tk.Button(self, text="Kembali", command=self.create_main_menu)
        btn_back.pack(pady=10)

    def pelanggan_register_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Registrasi Pelanggan", font=("Arial", 20)).pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        lbl_nama = tk.Label(frame, text="Nama:")
        lbl_nama.grid(row=0, column=0, sticky="e")
        ent_nama = tk.Entry(frame, width=30)
        ent_nama.grid(row=0, column=1, pady=5)

        lbl_email = tk.Label(frame, text="Email:")
        lbl_email.grid(row=1, column=0, sticky="e")
        ent_email = tk.Entry(frame, width=30)
        ent_email.grid(row=1, column=1, pady=5)

        lbl_pass = tk.Label(frame, text="Password:")
        lbl_pass.grid(row=2, column=0, sticky="e")
        ent_pass = tk.Entry(frame, show="*", width=30)
        ent_pass.grid(row=2, column=1, pady=5)

        lbl_alamat = tk.Label(frame, text="Alamat:")
        lbl_alamat.grid(row=3, column=0, sticky="e")
        ent_alamat = tk.Entry(frame, width=30)
        ent_alamat.grid(row=3, column=1, pady=5)

        lbl_nohp = tk.Label(frame, text="No HP:")
        lbl_nohp.grid(row=4, column=0, sticky="e")
        ent_nohp = tk.Entry(frame, width=30)
        ent_nohp.grid(row=4, column=1, pady=5)

        def do_register():
            n = ent_nama.get().strip()
            e = ent_email.get().strip()
            p = ent_pass.get().strip()
            a = ent_alamat.get().strip()
            h = ent_nohp.get().strip()

            if not (n and e and p and a and h):
                messagebox.showerror("Error", "Semua field harus diisi!")
                return
            user_obj = pelanggan()
            user_obj.register(n, e, p, a, h)
            messagebox.showinfo("Sukses", f"Registrasi berhasil! Silakan login.")
            self.pelanggan_login_screen()

        btn_register = tk.Button(self, text="Register", command=do_register)
        btn_register.pack(pady=10)

        btn_back = tk.Button(self, text="Kembali", command=self.pelanggan_login_screen)
        btn_back.pack(pady=10)

    def pelanggan_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text=f"Selamat datang, {self.active_pelanggan.nama}", font=("Arial", 18)).pack(pady=15)

        btn_pesan = tk.Button(self, text="Pesan Makanan", width=20, command=self.pelanggan_pesan_makanan)
        btn_pesan.pack(pady=6)

        btn_status = tk.Button(self, text="Cek Status Pesanan", width=20, command=self.pelanggan_cek_status)
        btn_status.pack(pady=6)

        btn_bayar = tk.Button(self, text="Bayar Pesanan", width=20, command=self.pelanggan_bayar_pesanan)
        btn_bayar.pack(pady=6)

        btn_logout = tk.Button(self, text="Logout", width=20, command=self.pelanggan_logout)
        btn_logout.pack(pady=20)

    def pelanggan_logout(self):
        self.active_pelanggan = None
        messagebox.showinfo("Logout", "Anda telah logout.")
        self.create_main_menu()

    def pelanggan_pesan_makanan(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Pilih Restoran", font=("Arial", 16)).pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(pady=5, fill="x")

        tk.Label(frame, text="Restoran:").pack(anchor="w")
        resto_names = [r.namaResto for r in restoran_list]
        combo_resto = ttk.Combobox(frame, values=resto_names, state="readonly")
        combo_resto.pack(pady=5, fill="x")

        tk.Label(frame, text="Pilih Menu:").pack(anchor="w")
        lst_menus = tk.Listbox(frame, height=8)
        lst_menus.pack(pady=5, fill="both")

        tk.Label(frame, text="Jumlah:").pack(anchor="w")
        spin_jumlah = tk.Spinbox(frame, from_=1, to=100, width=5)
        spin_jumlah.pack(pady=5)

        def load_menu(event):
            lst_menus.delete(0, tk.END)
            sel = combo_resto.get()
            for r in restoran_list:
                if r.namaResto == sel:
                    menus = menu_resto.get(r.userID, [])
                    for m in menus:
                        avail = "✓" if m.ketersediaan else "✗"
                        lst_menus.insert(tk.END, f"{m.namaMakanan} - Rp{m.harga} [{avail}]")
                    break

        combo_resto.bind("<<ComboboxSelected>>", load_menu)

        def submit_order():
            resto_name = combo_resto.get()
            menu_idx = lst_menus.curselection()
            if not resto_name:
                messagebox.showerror("Error", "Silakan pilih restoran.")
                return
            if not menu_idx:
                messagebox.showerror("Error", "Silakan pilih menu.")
                return
            jumlah = int(spin_jumlah.get())
            pel = self.active_pelanggan
            pesanan, err = pel.pesan_makanan(resto_name, menu_idx[0], jumlah, restoran_list)
            if err:
                messagebox.showerror("Error", err)
            else:
                messagebox.showinfo("Sukses", f"Pesanan berhasil dibuat! ID Pesanan: {pesanan.pesananID}")
                self.pelanggan_menu()

        btn_order = tk.Button(frame, text="Pesan", command=submit_order)
        btn_order.pack(pady=10)

        btn_back = tk.Button(self, text="Kembali", command=self.pelanggan_menu)
        btn_back.pack(pady=10)

    def pelanggan_cek_status(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Status Pesanan Anda", font=("Arial", 16)).pack(pady=15)

        orders = self.active_pelanggan.list_orders()
        if not orders:
            tk.Label(self, text="Anda belum membuat pesanan apapun.").pack(pady=20)
        else:
            frame = tk.Frame(self)
            frame.pack(pady=5, fill="both", expand=True)
            lb = tk.Listbox(frame, height=15, width=80)
            lb.pack(side="left", fill="both", expand=True)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=lb.yview)
            scrollbar.pack(side="right", fill="y")
            lb.config(yscrollcommand=scrollbar.set)
            for p in orders:
                lb.insert(tk.END, str(p))

        btn_back = tk.Button(self, text="Kembali", command=self.pelanggan_menu)
        btn_back.pack(pady=15)

    def pelanggan_bayar_pesanan(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Bayar Pesanan", font=("Arial", 16)).pack(pady=15)

        pending_payments = pesanan_history.get("pending_payment", [])
        my_pending = [p for p in pending_payments if p.idPelanggan == self.active_pelanggan.userID]

        if not my_pending:
            tk.Label(self, text="Tidak ada pesanan yang perlu dibayar.").pack(pady=20)
            btn_back = tk.Button(self, text="Kembali", command=self.pelanggan_menu)
            btn_back.pack(pady=15)
            return

        frame = tk.Frame(self)
        frame.pack(pady=5)

        tk.Label(frame, text="Pilih Pesanan yang Ingin Dibayar:").pack(anchor="w")
        combo_pesanan = ttk.Combobox(frame, values=[p.pesananID + " - " + p.makanan for p in my_pending], state="readonly")
        combo_pesanan.pack(pady=5)

        tk.Label(frame, text="Metode Pembayaran:").pack(anchor="w")
        combo_metode = ttk.Combobox(frame, values=["CASH", "TRANSFER"], state="readonly")
        combo_metode.current(0)
        combo_metode.pack(pady=5)

        def konfirmasi_bayar():
            pesanan_sel = combo_pesanan.get()
            metode = combo_metode.get()
            if not pesanan_sel or not metode:
                messagebox.showerror("Error", "Semua field harus diisi!")
                return
            pesanan_id = pesanan_sel.split(" ")[0]
            res, pesanan_obj = self.active_pelanggan.bayar_pesanan(pesanan_id, metode)
            if res:
                messagebox.showinfo("Sukses", f"Pembayaran pesanan {pesanan_id} berhasil.")
                self.pelanggan_menu()
            else:
                messagebox.showerror("Error", "Pesanan tidak ditemukan atau sudah dibayar.")

        btn_bayar = tk.Button(frame, text="Bayar", command=konfirmasi_bayar)
        btn_bayar.pack(pady=15)

        btn_back = tk.Button(self, text="Kembali", command=self.pelanggan_menu)
        btn_back.pack(pady=10)

    # ======= Restoran Screens =============
    def restoran_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Login Restoran", font=("Arial", 20)).pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Email:").grid(row=0, column=0, sticky="e")
        entry_email = tk.Entry(frame, width=30)
        entry_email.grid(row=0, column=1, pady=5)
        tk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e")
        entry_password = tk.Entry(frame, show="*", width=30)
        entry_password.grid(row=1, column=1, pady=5)

        def do_login():
            email = entry_email.get().strip()
            password = entry_password.get().strip()
            for r in restoran_list:
                if r.check_login(email, password):
                    self.active_restoran = r
                    messagebox.showinfo("Sukses", f"Login Berhasil! Restoran {r.namaResto}")
                    self.restoran_menu()
                    return
            messagebox.showerror("Gagal", "Email atau password salah.")

        btn_login = tk.Button(self, text="Login", command=do_login)
        btn_login.pack(pady=10)

        btn_back = tk.Button(self, text="Kembali", command=self.create_main_menu)
        btn_back.pack(pady=10)

    def restoran_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text=f"Selamat datang, {self.active_restoran.namaResto}", font=("Arial", 18)).pack(pady=15)

        btn_lihat_menu = tk.Button(self, text="Lihat Menu", width=20, command=self.restoran_lihat_menu)
        btn_lihat_menu.pack(pady=5)

        btn_manage_menu = tk.Button(self, text="Kelola Menu", width=20, command=self.restoran_kelola_menu)
        btn_manage_menu.pack(pady=5)

        btn_lihat_pesanan = tk.Button(self, text="Lihat Pesanan", width=20, command=self.restoran_lihat_pesanan)
        btn_lihat_pesanan.pack(pady=5)

        btn_proses_pesanan = tk.Button(self, text="Proses Pesanan", width=20, command=self.restoran_proses_pesanan)
        btn_proses_pesanan.pack(pady=5)

        btn_logout = tk.Button(self, text="Logout", width=20, command=self.restoran_logout)
        btn_logout.pack(pady=20)

    def restoran_logout(self):
        self.active_restoran = None
        messagebox.showinfo("Logout", "Restoran telah logout.")
        self.create_main_menu()

    def restoran_lihat_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text=f"Menu Restoran {self.active_restoran.namaResto}", font=("Arial", 16)).pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(pady=5, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=80, height=20)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        menus = self.active_restoran.get_menu()
        if not menus:
            listbox.insert(tk.END, "Tidak ada menu tersedia.")
        else:
            for menu in menus:
                listbox.insert(tk.END, f"{menu.namaMakanan} - Rp{menu.harga} ({'Tersedia' if menu.ketersediaan else 'Tidak Tersedia'}) - {menu.deskripsi}")

        btn_back = tk.Button(self, text="Kembali", command=self.restoran_menu)
        btn_back.pack(pady=15)

    def restoran_kelola_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Kelola Menu", font=("Arial", 16)).pack(pady=10)

        menus = self.active_restoran.get_menu()

        frame = tk.Frame(self)
        frame.pack(pady=5)

        listbox = tk.Listbox(frame, width=80, height=15)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        def refresh_menu_list():
            listbox.delete(0, tk.END)
            for idx, menu in enumerate(menus):
                listbox.insert(tk.END, f"{idx+1}. {menu.namaMakanan} - Rp{menu.harga} ({'Tersedia' if menu.ketersediaan else 'Tidak Tersedia'})")

        refresh_menu_list()

        def add_menu():
            add_win = tk.Toplevel(self)
            add_win.title("Tambah Menu")

            tk.Label(add_win, text="Nama Menu:").grid(row=0, column=0)
            entry_nama = tk.Entry(add_win)
            entry_nama.grid(row=0, column=1)

            tk.Label(add_win, text="Deskripsi:").grid(row=1, column=0)
            entry_desc = tk.Entry(add_win)
            entry_desc.grid(row=1, column=1)

            tk.Label(add_win, text="Harga:").grid(row=2, column=0)
            entry_harga = tk.Entry(add_win)
            entry_harga.grid(row=2, column=1)

            tk.Label(add_win, text="Ketersediaan (y/n):").grid(row=3, column=0)
            entry_avail = tk.Entry(add_win)
            entry_avail.grid(row=3, column=1)

            def submit_add():
                nama = entry_nama.get().strip()
                desc = entry_desc.get().strip()
                harga_str = entry_harga.get().strip()
                avail_str = entry_avail.get().strip().lower()
                if not (nama and desc and harga_str and avail_str in ['y', 'n']):
                    messagebox.showerror("Error", "Semua field harus diisi dengan benar!")
                    return
                try:
                    harga = int(harga_str)
                    avail = avail_str == 'y'
                except:
                    messagebox.showerror("Error", "Harga harus angka dan ketersediaan y/n.")
                    return
                menuID = f"M{len(menus) + 1:03d}"
                new_menu = MenuMakanan(menuID, nama, desc, harga, avail, self.active_restoran.userID)
                self.active_restoran.add_menu_item(new_menu)
                menus.append(new_menu)
                refresh_menu_list()
                add_win.destroy()
                messagebox.showinfo("Sukses", "Menu berhasil ditambahkan!")

            btn_submit = tk.Button(add_win, text="Tambah", command=submit_add)
            btn_submit.grid(row=4, column=0, columnspan=2)

        def update_menu():
            try:
                idx = int(simpledialog.askstring("Update Menu", "Masukkan nomor menu yang ingin diupdate:", parent=self))
                if not (1 <= idx <= len(menus)):
                    messagebox.showerror("Error", "Nomor menu tidak valid!")
                    return
                idx -= 1
            except:
                messagebox.showerror("Error", "Input harus angka!")
                return

            update_win = tk.Toplevel(self)
            update_win.title("Update Menu")

            menu_item = menus[idx]

            tk.Label(update_win, text="Nama Menu (kosongkan jika tidak diubah):").grid(row=0, column=0)
            entry_nama = tk.Entry(update_win)
            entry_nama.insert(0, menu_item.namaMakanan)
            entry_nama.grid(row=0, column=1)

            tk.Label(update_win, text="Deskripsi (kosongkan jika tidak diubah):").grid(row=1, column=0)
            entry_desc = tk.Entry(update_win)
            entry_desc.insert(0, menu_item.deskripsi)
            entry_desc.grid(row=1, column=1)

            tk.Label(update_win, text="Harga (kosongkan jika tidak diubah):").grid(row=2, column=0)
            entry_harga = tk.Entry(update_win)
            entry_harga.insert(0, str(menu_item.harga))
            entry_harga.grid(row=2, column=1)

            tk.Label(update_win, text="Ketersediaan (y/n, kosongkan jika tidak diubah):").grid(row=3, column=0)
            entry_avail = tk.Entry(update_win)
            entry_avail.grid(row=3, column=1)

            def submit_update():
                nama = entry_nama.get().strip() or None
                desc = entry_desc.get().strip() or None
                harga_val = entry_harga.get().strip()
                harga = None
                if harga_val:
                    try:
                        harga = int(harga_val)
                    except:
                        messagebox.showerror("Error", "Harga harus berupa angka!")
                        return
                avail_val = entry_avail.get().strip().lower()
                avail = None
                if avail_val in ['y', 'n']:
                    avail = avail_val == 'y'
                elif avail_val != '':
                    messagebox.showerror("Error", "Ketersediaan harus y, n, atau kosongkan!")
                    return

                self.active_restoran.update_menu_item(idx, nama, desc, harga, avail)
                refresh_menu_list()
                update_win.destroy()
                messagebox.showinfo("Sukses", "Menu berhasil diupdate!")

            btn_submit = tk.Button(update_win, text="Update", command=submit_update)
            btn_submit.grid(row=4, column=0, columnspan=2)

        def delete_menu():
            try:
                idx = int(simpledialog.askstring("Hapus Menu", "Masukkan nomor menu yang ingin dihapus:", parent=self))
                if not (1 <= idx <= len(menus)):
                    messagebox.showerror("Error", "Nomor menu tidak valid!")
                    return
                idx -= 1
            except:
                messagebox.showerror("Error", "Input harus angka!")
                return

            confirmed = messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus menu '{menus[idx].namaMakanan}'?")
            if confirmed:
                self.active_restoran.delete_menu_item(idx)
                refresh_menu_list()
                messagebox.showinfo("Sukses", "Menu berhasil dihapus!")

        btn_add = tk.Button(self, text="Tambah Menu", command=add_menu)
        btn_add.pack(pady=5)
        btn_update = tk.Button(self, text="Update Menu", command=update_menu)
        btn_update.pack(pady=5)
        btn_delete = tk.Button(self, text="Hapus Menu", command=delete_menu)
        btn_delete.pack(pady=5)

        btn_back = tk.Button(self, text="Kembali", command=self.restoran_menu)
        btn_back.pack(pady=15)

    def restoran_lihat_pesanan(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text=f"Pesanan Masuk - Restoran {self.active_restoran.namaResto}", font=("Arial", 16)).pack(pady=10)

        orders = self.active_restoran.list_orders()

        if not orders:
            tk.Label(self, text="Tidak ada pesanan.").pack(pady=20)
        else:
            frame = tk.Frame(self)
            frame.pack(pady=5, fill="both", expand=True)

            lb = tk.Listbox(frame, height=20, width=80)
            lb.pack(side="left", fill="both", expand=True)

            scrollbar = tk.Scrollbar(frame, orient="vertical", command=lb.yview)
            scrollbar.pack(side="right", fill="y")

            lb.config(yscrollcommand=scrollbar.set)

            for p in orders:
                lb.insert(tk.END, str(p))

        btn_back = tk.Button(self, text="Kembali", command=self.restoran_menu)
        btn_back.pack(pady=15)

    def restoran_proses_pesanan(self):
        pesanan = self.active_restoran.process_next_order()
        if pesanan:
            messagebox.showinfo("Sukses", f"Pesanan {pesanan.pesananID} telah diproses dan siap diambil oleh kurir.")
        else:
            messagebox.showinfo("Info", "Tidak ada pesanan dalam antrian.")
        self.restoran_menu()

    # ======= Kurir Screens =============

    def kurir_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Login atau Register Kurir", font=("Arial", 20)).pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        btn_login = tk.Button(frame, text="Login Kurir", width=20, command=self.kurir_login_popup)
        btn_login.grid(row=0, column=0, padx=10, pady=10)
        btn_register = tk.Button(frame, text="Register Kurir", width=20, command=self.kurir_register_screen)
        btn_register.grid(row=0, column=1, padx=10, pady=10)

        btn_back = tk.Button(self, text="Kembali", command=self.create_main_menu)
        btn_back.pack(pady=15)

    def kurir_login_popup(self):
        dlg = tk.Toplevel(self)
        dlg.title("Login Kurir")

        tk.Label(dlg, text="Nama Kurir:").grid(row=0, column=0)
        entry_nama = tk.Entry(dlg)
        entry_nama.grid(row=0, column=1)

        tk.Label(dlg, text="ID Kurir:").grid(row=1, column=0)
        entry_id = tk.Entry(dlg)
        entry_id.grid(row=1, column=1)

        def do_login():
            nama = entry_nama.get().strip()
            idKurir = entry_id.get().strip()
            user_obj = kurir()
            if user_obj.login(nama, idKurir):
                self.active_kurir = user_obj
                messagebox.showinfo("Sukses", f"Login berhasil! Selamat datang, {nama}.")
                dlg.destroy()
                self.kurir_menu()
            else:
                messagebox.showerror("Gagal", "Nama atau ID kurir salah.")

        btn_login = tk.Button(dlg, text="Login", command=do_login)
        btn_login.grid(row=2, column=0, columnspan=2)

    def kurir_register_screen(self):
        dlg = tk.Toplevel(self)
        dlg.title("Registrasi Kurir")

        tk.Label(dlg, text="Nama Kurir:").grid(row=0, column=0)
        ent_nama = tk.Entry(dlg)
        ent_nama.grid(row=0, column=1)

        tk.Label(dlg, text="Email Kurir:").grid(row=1, column=0)
        ent_email = tk.Entry(dlg)
        ent_email.grid(row=1, column=1)

        tk.Label(dlg, text="Password:").grid(row=2, column=0)
        ent_pass = tk.Entry(dlg, show="*")
        ent_pass.grid(row=2, column=1)

        tk.Label(dlg, text="Alamat:").grid(row=3, column=0)
        ent_alamat = tk.Entry(dlg)
        ent_alamat.grid(row=3, column=1)

        tk.Label(dlg, text="No HP:").grid(row=4, column=0)
        ent_nohp = tk.Entry(dlg)
        ent_nohp.grid(row=4, column=1)

        def do_register():
            n = ent_nama.get().strip()
            e = ent_email.get().strip()
            p = ent_pass.get().strip()
            a = ent_alamat.get().strip()
            h = ent_nohp.get().strip()
            if not (n and e and p and a and h):
                messagebox.showerror("Error", "Semua field harus diisi!")
                return
            user_obj = kurir()
            user_obj.register(n, e, p, a, h)
            messagebox.showinfo("Sukses", f"Registrasi berhasil! ID Anda: {user_obj.userID}")
            dlg.destroy()

        btn_reg = tk.Button(dlg, text="Register", command=do_register)
        btn_reg.grid(row=5, column=0, columnspan=2)

    def kurir_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text=f"Selamat datang, Kurir {self.active_kurir.nama}", font=("Arial", 18)).pack(pady=15)

        btn_ambil = tk.Button(self, text="Ambil Pesanan", width=20, command=self.kurir_ambil_pesanan)
        btn_ambil.pack(pady=5)

        btn_selesai = tk.Button(self, text="Selesaikan Pesanan", width=20, command=self.kurir_selesaikan_pesanan)
        btn_selesai.pack(pady=5)

        btn_logout = tk.Button(self, text="Logout", width=20, command=self.kurir_logout)
        btn_logout.pack(pady=20)

    def kurir_ambil_pesanan(self):
        pesanan = self.active_kurir.ambil_pesanan()
        if pesanan:
            messagebox.showinfo("Sukses", f"Pesanan {pesanan.pesananID} telah diambil.")
        else:
            messagebox.showinfo("Info", "Tidak ada pesanan yang siap diambil.")
        self.kurir_menu()

    def kurir_selesaikan_pesanan(self):
        pesanan = self.active_kurir.selesaikan_pesanan()
        if pesanan:
            messagebox.showinfo("Sukses", f"Pesanan {pesanan.pesananID} telah diselesaikan dan menunggu pembayaran pelanggan.")
        else:
            messagebox.showinfo("Info", "Tidak ada pesanan aktif untuk diselesaikan.")
        self.kurir_menu()

    def kurir_logout(self):
        self.active_kurir = None
        messagebox.showinfo("Logout", "Kurir telah logout.")
        self.create_main_menu()

if __name__ == "__main__":
    app = EFoodApp()
    app.mainloop()

