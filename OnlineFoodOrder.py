from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime

registered_users = []
kurir_terdaftar = []

menu_resto = {}

pesanan_queue = deque()
pesanan_history = {}
daftar_semua_pesanan = []
pesanan_kurir = {}


class user(ABC): 
    def __init__(self, userID, nama, email, password, alamat, noHp):
        self.userID = userID
        self.nama = nama
        self.email = email
        self.password = password
        self.alamat = alamat
        self.noHp = noHp

    @abstractmethod
    def login(self):
        pass

    def logout(self):
        print(f"{self.nama} telah logout.")

    def update_profile(self, nama=None, email=None):
        if nama:
            self.nama = nama
        if email:
            self.email = email



class restoran(user):
    def __init__(self, userID, nama, email, password, alamat, noHp, namaResto, lokasi):
    super().__init__(userID, nama, email, password, alamat, noHp)
        self.namaResto = namaResto
        self.lokasi = lokasi

        if self.userID not in menu_resto:
            menu_resto[self.userID] = [
                menuMakanan("M001", "Nasi Goreng", "Nasi goreng spesial", 15000, True, self.userID),
                menuMakanan("M002", "Mie Ayam", "Mie ayam dengan topping lengkap", 12000, True, self.userID),
                menuMakanan("M003", "Sate Ayam", "Sate ayam dengan bumbu kacang", 20000, True, self.userID),
                menuMakanan("M004", "Es Teh Manis", "Es teh manis segar", 5000, True, self.userID)
            ]    

    def login(self):
        email = input("Masukkan Email: ")
        password = input("Password: ")
        if self.email == email and self.password == password:
            print(f"Restoran {self.namaResto} diakses oleh {self.nama}")
            print(F"Selamat datang")
            return True
        else:
            print("Email atau password salah!")
            return False
    
    def kelolaMenu(self):
        if self.userID not in menu_resto:
            menu_resto[self.userID] = []
            
        print(f"\nDaftar menu untuk restoran {self.namaResto}:")
        for idx, menu in enumerate(menu_resto[self.userID], 1):
            status = "Tersedia" if menu.ketersediaan else "Tidak Tersedia"
            print(f"{idx}. {menu.namaMakanan} | Rp{menu.harga:,} | {status}")
            print(f"   Deskripsi: {menu.deskripsi}")
        
    def prosesPesanan(self):
        if pesanan_queue:
            pesanan = pesanan_queue.popleft()
            pesanan.updateStatusPesanan("Siap Diambil")
            # Move to temporary queue for couriers
            if "pending_kurir" not in pesanan_kurir:
                pesanan_kurir["pending_kurir"] = deque()
                pesanan_kurir["pending_kurir"].append(pesanan)
                print(f"Pesanan {pesanan.pesananID} untuk pelanggan {pesanan.idPelanggan} telah diproses dan siap diambil kurir.")
            else:
                print("Tidak ada pesanan dalam antrian.")
            
    def lihatpesanan(self):
        print(f"Daftar semua pesanan untuk restoran {self.namaResto}:")
        if not daftar_semua_pesanan:
            print("Tidak ada pesanan.")
            return
        for i, pesanan in enumerate(daftar_semua_pesanan, 1):
            print(f"{i}. {pesanan}")
            
    def logout(self):
        print(f"Restoran {self.namaResto} telah logout.")
        return super().logout()
    
def menuRestoran(restoran_list):
    active_resto = None

    print("\nPilih restoran untuk login:")
    for idx, resto in enumerate(restoran_list, 1):
        print(f"{idx}. {resto.namaResto}")
            
    try:
        resto_choice = int(input("\nMasukkan nomor restoran (1-3): "))
        if 1 <= resto_choice <= len(restoran_list):
            active_resto = restoran_list[resto_choice-1]
            if not active_resto.login():
                return
        else:
            print("Nomor restoran tidak valid!")
    except ValueError:
        print("Input harus berupa angka!")
        return

    while True:
        print(f"\n==== MENU RESTORAN: {active_resto.namaResto} ====")
        print("1. Daftar menu")
        print(f"2. Manajemen resto {active_resto.namaResto}")
        print("3. lihat pesanan masuk")
        print("4. Proses pesanan")
        print("5. Keluar")

        pilihan = input("Masukkan pilihan (1/2/3): ")
        if pilihan == '1':
            active_resto.kelolaMenu()
            continue
        elif pilihan == '2':
            manageMenu = menuMakanan("", "", "", 0, True, active_resto.userID)
            manageMenu.updateMenu(restoran_list)
            return
        elif pilihan == '3':
            active_resto.lihatpesanan()
            return
        elif pilihan == '4':
            active_resto.prosesPesanan()
            return
        elif pilihan == '5':
            active_resto.logout()
            return
        else:
            print("Pilihan tidak valid!")

 

class pelanggan(user):
    def __init__(self, userID, nama, email, password, alamat, noHp):
        super().__init__(userID, nama, email, password, alamat, noHp)
        self.selectedResto = None

    def register(self):
        print("\n=== REGISTRASI PELANGGAN ===")
        self.nama = input("Masukkan nama: ")
        self.email = input("Masukkan email: ")
        self.password = input("Masukkan password: ")
        self.alamat = input("Masukkan alamat: ")
        self.noHp = input("Masukkan no. hp: ")
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
        print(f"\nRegistrasi berhasil! ID Anda: {self.userID}")
        return True

    def login(self):
        print("\n=== LOGIN PELANGGAN ===")
        email = input("Masukkan email: ")
        password = input("Masukkan password: ")

        for user in registered_users:
            if user['email'] == email and user['password'] == password:
                self.userID = user['userID']
                self.nama = user['nama']
                self.email = user['email']
                self.password = user['password']
                self.alamat = user['alamat']
                self.noHp = user['noHp']
                print(f"\nLogin berhasil! Selamat datang {self.nama}")
                return True
        print("\nLogin gagal! Email atau password salah.")
        return False

    def pesan_makanan(self, restoran_list):
        namaResto = input("\nMasukkan nama restoran: ")
        for resto in restoran_list:
            if resto.namaResto == namaResto:
                self.selectedResto = resto
                print(f"Restoran {namaResto} ditemukan!")
                resto.kelolaMenu()
            
                if resto.userID not in menu_resto or not menu_resto[resto.userID]:
                    print("Menu tidak tersedia di restoran ini.")
                    return
            
                try:
                    pilihan = int(input(f"Pilih nomor makanan yang ingin dipesan (1-{len(menu_resto[resto.userID])}): "))
                    if 1 <= pilihan <= len(menu_resto[resto.userID]):
                        menu_dipilih = menu_resto[resto.userID][pilihan-1]
                    
                        if not menu_dipilih.ketersediaan:
                            print("Maaf, menu ini sedang tidak tersedia.")
                            return
                        
                        jumlah = int(input("Masukkan jumlah pesanan: "))
                        if jumlah <= 0:
                            print("Jumlah pesanan harus lebih dari 0!")
                            return
                        
                        ItemPesanan.hitungSubTotal = jumlah * menu_dipilih.harga

                        pesanan = Pesanan(
                            idPelanggan=self.userID,
                            idRestoran=resto.userID,
                            makanan=menu_dipilih.namaMakanan,
                            harga=ItemPesanan.hitungSubTotal,
                        )

                        pesanan_queue.append(pesanan)
                        daftar_semua_pesanan.append(pesanan)

                        if self.nama not in pesanan_history:
                            pesanan_history[self.nama] = []
                        pesanan_history[self.nama].append(pesanan)

                        print(f"\nPesanan berhasil dibuat dan dimasukkan ke dalam antrian.")
                        print(f"ID Pesanan: {pesanan.pesananID}")
                        print(f"Menu: {menu_dipilih.namaMakanan}")
                        print(f"Jumlah: {jumlah}")
                        print(f"Total Harga: Rp{ItemPesanan.hitungSubTotal:,}")
                        return
                    else:
                        print("Nomor menu tidak valid!")
                        return
                except ValueError:
                    print("Input harus berupa angka!")
                    return  
        print(f"Restoran {namaResto} tidak ditemukan.")

    def bayar_pesanan(self):
        if "pending_payment" not in pesanan_history or not pesanan_history["pending_payment"]:
            print("Tidak ada pesanan yang perlu dibayar.")
            return

        for pesanan in pesanan_history["pending_payment"]:
            if pesanan.idPelanggan == self.userID:
                print(f"\nDetail pesanan yang perlu dibayar:")
                print(pesanan)
                print(f"Total yang harus dibayar: Rp{pesanan.totalHarga:,}")
            
            metode = input("\nPilih metode pembayaran (CASH/TRANSFER): ").upper()
            if metode in ["CASH", "TRANSFER"]:
                pembayaran = Pembayaran(
                    pembayaranID=f"PAY{len(pesanan_history['pending_payment']):03d}",
                    metode=metode,
                    status="Pending",
                    tanggalBayar=datetime.now(),
                    idPesanan=pesanan.pesananID
                )
                
                pembayaran.konfirmasiPembayaran()
                pesanan.updateStatusPesanan("Sudah Dibayar")
                
                # Remove from pending payment
                pesanan_history["pending_payment"].remove(pesanan)
                
                # Prompt for review
                self.beri_ulasan(pesanan)
                return
            else:
                print("Metode pembayaran tidak valid!")
                return
                
        print("Tidak ditemukan pesanan yang perlu dibayar untuk akun ini.")

    def beri_ulasan(self, pesanan):
        print("\n=== ULASAN PESANAN ===")
        try:
            rating = int(input("Berikan rating (1-5): "))
            if not 1 <= rating <= 5:
                print("Rating harus antara 1-5!")
                return
            
            komentar = input("Berikan komentar: ")
        
            ulasan = Ulasan(
                ulasanID=f"ULS{len(pesanan_history):03d}",
                rating=rating,
                komentar=komentar,
                idPelanggan=self.userID,
                idRestoran=pesanan.idRestoran,
                idPesanan=pesanan.pesananID
            )
        
            ulasan.tulisUlasan()
            print("Terima kasih atas ulasan Anda!")
        
        except ValueError:
            print("Rating harus berupa angka!")
        
    def statusPesanan(self):
        print("\n=== STATUS PESANAN ===")
        if not daftar_semua_pesanan:
            print("Tidak ada pesanan yang dibuat.")
            return
        for pesanan in daftar_semua_pesanan:
            if pesanan.idPelanggan == self.userID:
                print(f"Pesanan ID: {pesanan.pesananID}, Status: {pesanan.statusPesanan}, Tanggal: {pesanan.tanggalPesan.strftime('%d-%m-%Y %H:%M')}")
                
def menuPelanggan(restoran_list):
    pelanggan1 = pelanggan(userID='', nama='', email='', password='', alamat='', noHp='')
    while True:
        print("\n==== MENU PELANGGAN ====")
        print("1. Register")
        print("2. Login")
        print("3. Pesan Makanan")
        print("4. Cek Status Pesanan")
        print("5. Bayar pesanan")
        print("6. Keluar")

        pilihan = input("Masukkan pilihan (1/2/3/4/5/6): ")
        if pilihan == '1':
            pelanggan1.register()
        elif pilihan == '2':
            login_sukses = pelanggan1.login()
            if not login_sukses:
                print("Email atau password tidak ditemukan")
                print("Silahkan registrasi terlebih dahulu")
        elif pilihan == '3':
            if not pelanggan1.nama:
                print("Silakan login terlebih dahulu!")
                continue
            pelanggan1.pesan_makanan(restoran_list)
        elif pilihan == '4':
            if not pelanggan1.nama:
                print("Silakan login terlebih dahulu!")
                continue
            pelanggan1.statusPesanan()
        elif pilihan == '5':
            if not pelanggan1.nama:
                print("Silakan login terlebih dahulu!")
                continue
            pelanggan1.bayar_pesanan()
        elif pilihan == '6':
            return
        else:
            print("Pilihan tidak valid!")



class kurir(user):
    def __init__(self, userID, nama, email, password, alamat, noHp):
        super().__init__(userID, nama, email, password, alamat, noHp)

    def register(self):
        print("\n=== REGISTRASI KURIR ===")
        self.nama = input("Masukkan nama: ")
        self.email = input("Masukkan email: ")
        self.password = input("Masukkan password: ")
        self.alamat = input("Masukkan alamat: ")
        self.noHp = input("Masukkan no. hp: ")
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
        print(f"\nRegistrasi berhasil! ID Anda: {self.userID}")
        return True

    def login(self):
        print("\n=== LOGIN KURIR ===")
        nama = input("Masukkan nama: ")
        idKurir = input("Masukkan ID Kurir: ")

        for k in kurir_terdaftar:
            if k['nama'] == nama and k['userID'] == idKurir:
                self.userID = k['userID']
                self.nama = k['nama']
                self.email = k['email']
                self.password = k['password']
                self.alamat = k['alamat']
                self.noHp = k['noHp']
                print(f"Login berhasil! Selamat datang, {self.nama}.")
                return True

        print("Login gagal! Periksa kembali nama dan ID Kurir.")
        return False

    def ambil_pesanan(self):
        if "pending_kurir" in pesanan_kurir and pesanan_kurir["pending_kurir"]:
        # Initialize courier's personal queue if not exists
            if self.nama not in pesanan_kurir:
                pesanan_kurir[self.nama] = deque()
            
        # Get order from pending queue
            pesanan = pesanan_kurir["pending_kurir"].popleft()
            pesanan.idKurir = self.userID
            pesanan.updateStatusPesanan("Diantar")
        
        # Add to courier's personal queue
            pesanan_kurir[self.nama].append(pesanan)
        
            print(f"Pesanan {pesanan.pesananID} untuk pelanggan {pesanan.idPelanggan} telah diambil oleh kurir {self.nama}.")
            print(f"Jumlah pesanan yang sedang diantar oleh {self.nama}: {len(pesanan_kurir[self.nama])}")
        else:
            print("Tidak ada pesanan yang siap diambil.")

    def selesaikan_pesanan(self):
        if self.nama not in pesanan_kurir or not pesanan_kurir[self.nama]:
            print(f"Tidak ada pesanan aktif untuk kurir {self.nama}")
            return
        
        pesanan = pesanan_kurir[self.nama].popleft()
        pesanan.updateStatusPesanan("Menunggu pembayaran")

        if "pending_payment" not in pesanan_history:
            pesanan_history["pending_payment"] = []
            pesanan_history["pending_payment"].append(pesanan)
    
        print(f"Pesanan {pesanan.pesananID} telah diselesaikan oleh kurir {self.nama}.")
        print(f"Pesanan siap untuk dibayar oleh pelanggan.")
        print(f"Sisa pesanan yang sedang diantar oleh {self.nama}: {len(pesanan_kurir[self.nama])}")
            
def menuKurir():
    kurir1 = kurir(userID='', nama='', email='', password='', alamat='', noHp='')
    while True:
        print("\n==== MENU KURIR ====")
        print("1. Register")
        print("2. Login")
        print("3. Ambil Pesanan")
        print("4. Update Status Pesanan ke Selesai")
        print("5. Keluar")
        pilihan = input("Masukkan pilihan (1/2/3/4/5): ")
        if pilihan == '1':
            kurir1.register()
        elif pilihan == '2':
            login_sukses = kurir1.login()
            if not login_sukses:
                print("nama atau ID kurir tidak ditemukan")
                print("Silahkan registrasi terlebih dahulu")
                continue
        elif pilihan == '3':
            if not kurir1.nama:
                print("Silakan login terlebih dahulu!")
                continue
            kurir1.ambil_pesanan()
        elif pilihan == '4':
            if not kurir1.nama:
                print("Silakan login terlebih dahulu!")
                continue
            kurir1.selesaikan_pesanan()
        elif pilihan == '5':
            return
        else:
            print("Pilihan tidak valid!")



class menuMakanan:
    def __init__(self, menuID, namaMakanan, deskripsi, harga, ketersediaan, idRestoran):
        self.menuID = menuID
        self.namaMakanan = namaMakanan
        self.deskripsi = deskripsi
        self.harga = harga
        self.ketersediaan = ketersediaan
        self.idRestoran = idRestoran

    def updateMenu(self, restoran_list):
        print("\n=== MANAJEMEN MENU RESTORAN ===")
        email = input("Masukkan email restoran: ")
        passResto = input("Masukkan password restoran: ")

        for resto in restoran_list:
            if resto.email == email and resto.password == passResto:
                if resto.userID not in menu_resto:
                    menu_resto[resto.userID] = []
                
                menu_list = menu_resto[resto.userID]

                while True:
                    print("\n=== MENU MANAJEMEN ===")
                    print("1. Tambah Menu")
                    print("2. Update Menu")
                    print("3. Hapus Menu")
                    print("4. Kembali")

                    pilihan = input("Pilih operasi (1-4): ")

                    if pilihan == "1":
                    # Tambah Menu
                        print("\n=== TAMBAH MENU BARU ===")
                        menuID = f"M{len(menu_list) + 1:03d}"
                        nama = input("Nama menu: ")
                        deskripsi = input("Deskripsi menu: ")
                        try:
                            harga = int(input("Harga menu: "))
                            ketersediaan = input("Tersedia? (y/n): ").lower() == 'y'
                            menu_baru = menuMakanan(menuID, nama, deskripsi, harga, ketersediaan, resto.userID)
                            menu_list.append(menu_baru)
                            print("Menu berhasil ditambahkan!")
                        except ValueError:
                            print("Harga harus berupa angka!")

                    elif pilihan == "2":
                    # Update Menu
                        print("\nDaftar menu saat ini:")
                        for idx, menu in enumerate(menu_list, 1):
                            status = "Tersedia" if menu.ketersediaan else "Tidak Tersedia"
                            print(f"{idx}. {menu.namaMakanan} | Rp{menu.harga:,} | {status}")
                            print(f"   Deskripsi: {menu.deskripsi}")

                        try:
                            menu_idx = int(input("\nPilih nomor menu yang ingin diupdate: ")) - 1
                            if 0 <= menu_idx < len(menu_list):
                                menu = menu_list[menu_idx]
                                print(f"\n=== UPDATE MENU {menu.namaMakanan} ===")
                            
                                nama_baru = input("Nama baru (kosongkan jika tidak ingin mengubah): ")
                                deskripsi_baru = input("Deskripsi baru (kosongkan jika tidak ingin mengubah): ")
                                harga_baru = input("Harga baru (kosongkan jika tidak ingin mengubah): ")
                                status_baru = input("Status ketersediaan (y/n, kosongkan jika tidak ingin mengubah): ").lower()

                                if nama_baru: menu.namaMakanan = nama_baru
                                if deskripsi_baru: menu.deskripsi = deskripsi_baru
                                if harga_baru: menu.harga = int(harga_baru)
                                if status_baru: menu.ketersediaan = status_baru == 'y'

                                print("Menu berhasil diupdate!")
                            else:
                                print("Nomor menu tidak valid!")
                        except ValueError:
                            print("Input harus berupa angka!")

                    elif pilihan == "3":
                    # Hapus Menu
                        print("\nDaftar menu saat ini:")
                        for idx, menu in enumerate(menu_list, 1):
                            print(f"{idx}. {menu.namaMakanan}")

                        try:
                            menu_idx = int(input("\nPilih nomor menu yang ingin dihapus: ")) - 1
                            if 0 <= menu_idx < len(menu_list):
                                menu_hapus = menu_list.pop(menu_idx)
                                print(f"Menu {menu_hapus.namaMakanan} berhasil dihapus!")
                            else:
                                print("Nomor menu tidak valid!")
                        except ValueError:
                            print("Input harus berupa angka!")

                    elif pilihan == "4":
                        print("Kembali ke menu utama...")
                        return

                    else:
                        print("Pilihan tidak valid!")
                        return
                    
        print("Restoran tidak ditemukan atau password salah!")
        return 

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
        print(f"Status pesanan {self.pesananID} diperbarui menjadi: {statusBaru}")

    def __str__(self):
        tanggal = self.tanggalPesan.strftime("%d-%m-%Y %H:%M")
        return f"{self.pesananID} | {self.makanan} | {self.idRestoran} | {tanggal} | Status: {self.statusPesanan}"
    
class ItemPesanan:
    def __init__(self, itemID, jumlah, catatan, idMenu, idPesanan):
        self.itemID = itemID
        self.jumlah = jumlah
        self.catatan = catatan
        self.idMenu = idMenu
        self.idPesanan = idPesanan
        
    def hitungSubTotal(self, harga):    
        return self.jumlah * harga
        
    def __str__(self):
        return f"Item ID: {self.itemID}, Jumlah: {self.jumlah}, Catatan: {self.catatan}, ID Menu: {self.idMenu}, ID Pesanan: {self.idPesanan}"
    
class Ulasan:
    def __init__(self, ulasanID, rating, komentar, idPelanggan, idRestoran, idPesanan):
        self.ulasanID = ulasanID
        self.rating = rating
        self.komentar = komentar
        self.idPelanggan = idPelanggan
        self.idRestoran = idRestoran
        self.idPesanan = idPesanan
        
    def tulisUlasan(self):
        print(f"Ulasan untuk Restoran {self.idRestoran}: {self.komentar} (Rating: {self.rating})")
        
    def __str__(self):  
        return f"Ulasan ID: {self.ulasanID}, Rating: {self.rating}, Komentar: {self.komentar}, ID Pelanggan: {self.idPelanggan}, ID Restoran: {self.idRestoran}, ID Pesanan: {self.idPesanan}"
    
class Pembayaran:
    def __init__(self, pembayaranID, metode, status, tanggalBayar, idPesanan):
        self.pembayaranID = pembayaranID
        self.metode = metode
        self.status = status
        self.tanggalBayar = tanggalBayar
        self.idPesanan = idPesanan
    
    def konfirmasiPembayaran(self):
        self.status = "Terkonfirmasi"
        print(f"Pembayaran {self.pembayaranID} untuk Pesanan {self.idPesanan} telah terkonfirmasi.")





def pilihMenu():
    restoran_list = [
        restoran("R001", "Admin Padang", "resto@Padang", "pass123", "Sumut", "03222323", "RM Padang", "Lokasi A"),
        restoran("R002", "Admin Aero", "restoB@Aero", "pass456", "Ketintang", "03222324", "RM Aero", "Lokasi B"),
        restoran("R003", "Admin JayaBakti", "restoC@JBakti", "pass789", "Surabaya", "03222325", "RM JayaBakti", "Lokasi C")
    ]

    while True:
        print("\n====SISTEM PEMESANAN E-FOOD====\n")
        print("Pilih login:")
        print("1. Login pelanggan")
        print("2. Login restoran")
        print("3. Login kurir")
        print("4. Keluar")

        try:
            pilihan = int(input("Masukkan pilihan (1/2/3/4): "))
            if pilihan == 1:
                menuPelanggan(restoran_list)
            elif pilihan == 2:
                menuRestoran(restoran_list)
            elif pilihan == 3:
                menuKurir()
            elif pilihan == 4:
                print("Terima kasih telah menggunakan sistem ini. Sampai jumpa!")
                break
            else:
                print("Pilihan tidak valid. Silakan coba lagi.")
        except ValueError:
            print("Input tidak valid. Harap masukkan angka 1-4.")

if __name__ == "__main__":
    pilihMenu()
