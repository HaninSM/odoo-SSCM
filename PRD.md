# Product Requirement Document (PRD)
## Odoo Service Supply Chain Management (SSCM)

* **Project Name:** Odoo SSCM (Service Supply Chain Management)
* **Author:** HaninSM & Odoo Expert Assistant
* **Target Version:** Odoo Community / Enterprise (v16 / v17 / v18)
* **Status:** Draft / Alignment Stage
* **Use Cases:**
  1. Bengkel & Carwash (Automotive Workshop & Detailing)
  2. Salon, Barbershop, & Klinik Kecantikan (Beauty & Wellness Clinic)

---

## 1. Executive Summary & Problem Statement

Bisnis berbasis jasa menghadapi tantangan unik dalam rantai pasok: **Kapasitas layanan (waktu kerja, keahlian staf, dan fasilitas fisik) tidak dapat disimpan sebagai persediaan (perishable)**. Jika kapasitas tidak terpakai, potensi pendapatan hilang selamanya. Di saat yang sama, layanan sangat bergantung pada ketersediaan material habis pakai (*consumables* seperti oli atau serum obat).

Sistem Odoo SSCM ini dirancang untuk:
* Mengelola antrean dan reservasi berbasis kapasitas fisik (pit/kursi) dan kapasitas manusia (mekanik/terapis).
* Melacak siklus hidup aset pelanggan (kendaraan bermotor atau rekam kecantikan pelanggan).
* Mengintegrasikan konsumsi bahan habis pakai secara otomatis (*Automated Inventory Depletion*).
* Menyediakan jaminan mutu layanan melalui **Garansi Servis & Penanganan Klaim**.
* Mengotomatisasi perhitungan **Komisi dan Insentif Karyawan** berdasarkan kontribusi riil pengerjaan jasa maupun *cross-selling* produk.
* Memfasilitasi pembayaran non-tunai (QRIS/VA) yang terintegrasi langsung ke jurnal akuntansi dan pembukuan stok.

---

## 2. User Personas & Stakeholders

| Persona | Peran & Tanggung Jawab | Kebutuhan Utama Sistem |
| :--- | :--- | :--- |
| **Pelanggan (Customer)** | Penerima layanan | Kemudahan booking, kepastian antrean, riwayat servis transparan, garansi terjamin, kemudahan bayar via QRIS. |
| **Front Desk / Service Advisor (SA)** | Penerima tamu & perencana servis | Input cepat plat nomor / nama, cek ketersediaan bay/terapis, terbitkan SPK / kartu konsultasi, cek status garansi. |
| **Teknisi / Terapis** | Eksekutor layanan | Melihat antrean kerja di layar/tablet, mencatat part/bahan yang dipakai, mencatat hasil diagnosa/formula, memantau perolehan komisi harian. |
| **Kasir (Cashier)** | Penyelesai transaksi | Panggil order servis dalam 1 klik, tampilkan QRIS dinamis di layar pelanggan, cetak struk/nota digital. |
| **Supervisor / QC** | Pengendali mutu & klaim | Validasi hasil kerja sebelum serah terima, persetujuan klaim garansi servis tanpa biaya ke pelanggan. |
| **Owner / Keuangan** | Pengambil keputusan bisnis | Laporan utilisasi kapasitas, laporan layanan terlaris, akurasi stok bahan/part, rekap komisi karyawan untuk penggajian (*payroll*). |

---

## 3. Scope & Functional Requirements (FR)

### FR-1: Capacity & Dual-Resource Scheduling
* **FR-1.1:** Sistem harus mampu mengalokasikan dua jenis sumber daya sekaligus:
  * **Fisik:** Pit/Bay/Lift (Bengkel) atau Kursi/Bed/Mesin Facial (Salon/Klinik).
  * **Manusia:** Teknisi/Mekanik (Bengkel) atau Terapis/Dokter/Stylist (Salon).
* **FR-1.2:** Sistem harus memiliki validasi backend (`@api.constrains`) untuk mencegah bentrok jadwal (*double-booking*) pada jam dan sumber daya yang sama.
* **FR-1.3:** Tampilan visual antrean berbasis **Kanban Board** dengan tahapan:
  * *Draft/Booking $\rightarrow$ Antrean Masuk $\rightarrow$ Diagnosa/Pengerjaan $\rightarrow$ QC/Finishing $\rightarrow$ Selesai & Siap Bayar*.

### FR-2: Customer & Asset Profiling
* **FR-2.1 (Bengkel):** Modul pencatatan profil kendaraan terhubung ke `res.partner`:
  * Menyimpan Nomor Polisi, Nomor Rangka (VIN), Merek/Model, Odometer Masuk (KM).
  * Rekam histori servis berkala dan log penggantian suku cadang sebelumnya.
* **FR-2.2 (Salon/Klinik):** Modul rekam medis estetika (*Treatment History Card*):
  * Menyimpan catatan keluhan awal, tipe kulit/rambut, riwayat alergi kimiawi.
  * Menyimpan catatan resep formula (campuran cat rambut/peeling) dan dokumentasi foto *Before-After*.

### FR-3: Consumables & Spare Parts Supply Chain Management
* **FR-3.1 (BoM Kit Integration):** Layanan jasa tertentu dapat didefinisikan memiliki *Bill of Materials (BOM) tipe Kit*. Saat jasa dipilih, bahan pendukung (misal: serum, krim, sampo) otomatis dipesan dan dipotong dari stok gudang.
* **FR-3.2 (Stock Picking / Suku Cadang):** Pada pengerjaan servis bengkel, suku cadang (oli, kampas rem, busi) yang ditambahkan oleh teknisi otomatis membuat mutasi pengeluaran barang (`stock.picking`).
* **FR-3.3 (Automated Reordering Rules):** Sistem menjalankan pengadaan otomatis (*Min-Max Reordering Rule*) saat stok barang habis pakai mencapai ambang batas minimum.

### FR-4: Service Warranty & Claim Management (Garansi Servis)
* **FR-4.1 (Masa Garansi Otomatis):** Setiap penyelesaian order servis secara otomatis mencatat masa garansi:
  * *Bengkel:* Garansi jasa (misal: 14 hari atau 1.000 KM) dan garansi suku cadang (misal: aki 12 bulan dengan serial number tracking).
  * *Salon/Klinik:* Garansi revisi/retouch (misal: 3–7 hari untuk warna rambut atau perbaikan kuku).
* **FR-4.2 (Klaim Garansi):** Jika pelanggan komplain dalam masa garansi, Front Desk dapat membuat **Warranty Claim Order**:
  * Terhubung langsung (*traceable*) ke nomor SPK / Invoice aslinya.
  * Nilai tagihan jasa kepada pelanggan adalah **Rp 0 (Free of Charge)**.
  * Tetap mencatat penggunaan bahan/part pengganti sebagai beban biaya penjaminan mutu (*Quality Warranty Expense*).
  * Jika suku cadang cacat pabrik, sistem menyediakan alur retur ke vendor (*Vendor Return & Credit Note*).

### FR-5: Employee Commission & Incentive Engine (Sistem Komisi Karyawan)
* **FR-5.1 (Struktur Komisi Fleksibel):**
  * **Komisi Jasa:** Persentase (%) atau nominal tetap (Rp) dari nilai pengerjaan jasa per mekanik/terapis (misal: 15% dari jasa pengerjaan).
  * **Insentif Penjualan Produk (Retail Up-selling):** Bonus penjualan produk *homecare* / aksesoris kendaraan (misal: 5% dari harga jual).
  * **Komisi Tim / Pool:** Pembagian komisi merata untuk tim cuci mobil (*carwash bay crew*).
* **FR-5.2 (Perhitungan Otomatis):** Perhitungan komisi dihitung seketika saat order servis berstatus lunas (*Paid*).
* **FR-5.3 (Laporan & Integrasi Payroll):**
  * Dashboard transparansi komisi yang bisa dipantau harian oleh masing-masing staf.
  * Akumulasi komisi bulanan otomatis diekspor atau dihubungkan ke slip gaji karyawan (`hr.payslip`).

### FR-6: Digital Payment & Financial Automation
* **FR-6.1 (Kasir Terintegrasi):** Konversi satu klik dari Order Servis yang selesai ke modul `point_of_sale` atau `account.move` (Invoice).
* **FR-6.2 (Pembayaran QRIS & Gateway):** Menampilkan QRIS dinamis atau Virtual Account melalui integrasi Payment Acquirer.
* **FR-6.3 (Automated Settlement):** Webhook dari payment gateway otomatis merekonsiliasi pembayaran: status menjadi *Paid*, stok tervalidasi keluar, dan jurnal pengakuan pendapatan + HPP terbentuk tanpa intervensi manual.

### FR-7: Business Intelligence & Reporting
* **FR-7.1:** Analisa Layanan Terlaris (*Top Selling Services*) via Odoo Pivot & Graph View berdasarkan kuantitas, omzet, dan margin profit.
* **FR-7.2:** Analisa Utilisasi Kapasitas (*Pit/Chair Utilization Rate*) untuk mengukur rasio jam sibuk vs jam kosong.
* **FR-7.3:** Laporan Klaim Garansi untuk evaluasi kualitas kerja teknisi/terapis.

---

## 4. Technical Architecture & Constraints (Prinsip Odoo Development)

* **Code Extensibility:** Menggunakan prinsip *Inheritance* (`_inherit`), tidak mengubah kode dasar Odoo.
* **Security & ACL:** Pemisahan hak akses menggunakan User Groups (`security/security_rules.xml` & `ir.model.access.csv`) untuk peran Kasir, Teknisi, Service Advisor, dan Manager.
* **Convention Over Configuration:** Mengikuti panduan PEP 8, dekorator `@api.depends`, `@api.constrains`, dan penamaan tabel Odoo standar.
* **Audit Trail:** Mengaktifkan `mail.thread` dan `mail.activity.mixin` pada dokumen SPK dan klaim garansi untuk pencatatan *chatter* dan log perubahan status.

---

## 5. Roadmap Implementasi

1. **Phase 1: Foundation & Alignment** (Dokumentasi PRD, README, dan Diagram ERD).
2. **Phase 2: Master Data & Standard Configuration** (`stock`, `fleet`, `repair`, `appointment`, `point_of_sale`).
3. **Phase 3: Custom Addon Development** (Modul Queue, Warranty Engine, & Commission Module).
4. **Phase 4: Digital Payment & WhatsApp Notification Integration**.
5. **Phase 5: Testing, Training, & Go-Live.**
