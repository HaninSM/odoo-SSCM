# Odoo Service Supply Chain Management (SSCM)

Repositori ini memuat panduan arsitektur, konsep pembelajaran, dan rancangan implementasi **Service Supply Chain Management (SSCM)** berbasis ERP Odoo untuk bisnis jasa.

---

## 1. Pengertian: Dari SCM Klasik ke Service SCM (SSCM)

### SCM Tradisional (Barang Fisik)
Pada rantai pasok manufaktur dan ritel konvensional, fokus utama adalah pengelolaan arus barang fisik:
$$\text{Supplier} \longrightarrow \text{Bahan Baku} \longrightarrow \text{Pabrik / Manufaktur} \longrightarrow \text{Gudang / Distribusi} \longrightarrow \text{Pelanggan}$$
Tujuannya adalah memastikan ketersediaan barang jadi pada kuantitas, lokasi, dan waktu yang tepat dengan biaya serendah mungkin.

### Service Supply Chain Management / SSCM (Bisnis Jasa)
Pada bisnis berbasis layanan (seperti bengkel, salon, klinik estetika, carwash), produk yang dijual adalah **pelayanan/jasa**, bukan barang jadi. Karakteristik pembeda utamanya adalah:

1. **Perishability (Kapasitas Layanan Tidak Bisa Digudangkan):**
   Kapasitas waktu terapis atau pit bengkel yang menganggur selama 2 jam tidak dapat disimpan sebagai stok untuk dijual keesokan harinya. Kapasitas waktu yang tidak terpakai akan hilang selamanya.
2. **Simultaneity (Produksi dan Konsumsi Bersamaan):**
   Layanan diproduksi dan dikonsumsi secara *real-time* di hadapan pelanggan.
3. **Dual Supply Chain (Rantai Pasok Ganda):**
   * **Rantai Kapasitas (Capacity Chain):** Manajemen waktu ketersediaan tenaga ahli (mekanik, dokter, terapis) dan fasilitas kerja (kursi potong, bed facial, lift/pit servis).
   * **Rantai Material Pendukung (Consumables Chain):** Manajemen bahan habis pakai dan suku cadang (oli, busi, shampoo mobil, serum wajah, krim pewarna rambut).

Di Odoo, tujuan implementasi SSCM adalah **menyatukan ketersediaan kapasitas sumber daya fisik & manusia dengan logistik bahan habis pakai secara real-time dan terintegrasi ke sistem pencatatan keuangan**.

---

## 2. Pemetaan Kasus Bisnis & Modul Odoo

### Kasus 1: Bengkel & Carwash

#### A. Antrean Servis yang Jelas (*Work Order & Bay Allocation*)
* **Tantangan:** Kendaraan pelanggan datang, dicatat keluhannya, dialokasikan ke area kerja (*Pit / Lift / Bay*) yang kosong, dipantau status pengerjaannya oleh mekanik, dan ditampilkan ke monitor antrean ruang tunggu.
* **Modul Odoo yang Ditawarkan:**
  * **`repair` (Repair Orders):** Modul bawaan Odoo untuk membuat Surat Perintah Kerja (SPK) perbaikan, merinci jasa servis dan suku cadang yang digunakan.
  * **`mrp` (Manufacturing & Work Centers):** Mendefinisikan *Bay / Pit / Lift Servis* sebagai work center untuk memonitor utilisasi kapasitas bengkel.
  * **Custom Addon (`workshop_queue`):** Tampilan **Kanban Board** antrean bengkel:
    $$\text{Booking / Datang} \longrightarrow \text{Pemeriksaan / Diagnosa} \longrightarrow \text{Pengerjaan Servis} \longrightarrow \text{QC / Cuci} \longrightarrow \text{Selesai \& Siap Bayar}$$

#### B. Catatan Kendaraan Pelanggan (*Customer Vehicle Asset*)
* **Tantangan:** Setiap kendaraan memerlukan catatan rekam jejak: nomor polisi, nomor rangka (VIN), odometer terakhir (KM), riwayat penggantian part, dan jadwal servis berkala.
* **Modul Odoo yang Ditawarkan:**
  * **`fleet` (Fleet Management):** Dimodifikasi (*inherit*) agar bukan hanya mencatat kendaraan armada perusahaan, melainkan dihubungkan ke data pelanggan (`res.partner`).
  * **`contacts` (`res.partner`):** Sebagai pusat data profil pemilik kendaraan, nomor kontak/WhatsApp, dan histori transaksi servis.

#### C. Pembayaran Digital Langsung Tercatat
* **Tantangan:** Setelah kendaraan selesai dikerjakan, kasir langsung menerbitkan tagihan digital tanpa input manual ulang, menerima pembayaran QRIS, dan otomatis menandai lunas.
* **Modul Odoo yang Ditawarkan:**
  * **`point_of_sale` (POS) / `account` (Invoicing):** Mengonversi Work Order servis menjadi transaksi kasir dalam 1 klik.
  * **`payment` (Payment Provider Integration):** Integrasi QRIS Dinamis atau Payment Gateway (Midtrans, Xendit, DOKU). Webhook otomatis mengubah status invoice menjadi **Paid** dan membentuk jurnal penerimaan kas/bank secara otomatis tanpa rekonsiliasi manual.

#### D. Sisi SCM Pendukung (Suku Cadang & Bahan)
* **`stock` (Inventory Management):** Mengelola stok fisik oli, kampas rem, filter udara, dan sampo cuci mobil.
* **`purchase` (Procurement):** *Automated Reordering Rules* (Min-Max Rule). Jika stok oli mencapai batas minimum, Odoo otomatis membuat draf *Request for Quotation* (RFQ) ke supplier.

---

### Kasus 2: Salon, Barbershop, & Klinik Kecantikan

#### A. Booking per Kursi dan per Terapis (*Dual-Resource Scheduling*)
* **Tantangan:** Mencegah *double-booking*. Satu layanan memerlukan 2 sumber daya sekaligus: staf terapis/stylist dan aset fisik (kursi potong, bed facial, atau alat laser).
* **Modul Odoo yang Ditawarkan:**
  * **`appointment`:** Memfasilitasi reservasi online mandiri oleh pelanggan maupun reservasi langsung oleh admin kasir.
  * **`resource` & `planning`:** Mengatur jadwal kerja staf (`hr.employee`) dan ketersediaan aset (`appointment.resource`).
  * **Custom Constraint Validation:** Menerapkan validasi backend (Python ORM `@api.constrains`) untuk memastikan tidak ada jadwal bentrok pada staf maupun kursi di rentang waktu yang sama.

#### B. Riwayat Perawatan Pelanggan (*Customer Treatment History / E-Medical Card*)
* **Tantangan:** Mencatat preferensi pelanggan, catatan resep formula pewarna rambut, riwayat alergi, kondisi kulit sebelum/sesudah, dan foto dokumentasi *before-after*.
* **Modul Odoo yang Ditawarkan:**
  * **`contacts` (Extended):** Tab kustom pada formulir pelanggan yang merangkum seluruh rekam jejak perawatan.
  * **Custom Model (`salon.treatment.record`):** Entitas khusus pencatatan hasil treatment yang otomatis terhubung ke faktur/POS order yang bersangkutan.

#### C. Analisa Layanan Paling Laris (*Business Intelligence & Analytics*)
* **Tantangan:** Mengidentifikasi layanan mana yang paling menghasilkan pendapatan, tren musim liburan, dan performa produktivitas per terapis.
* **Modul Odoo yang Ditawarkan:**
  * **`point_of_sale` (Reporting):** Laporan penjualan harian per kategori layanan dan per kasir/cabang.
  * **`sale` (Sales Analysis BI - Pivot & Graph):**
    * **Pivot Table View:** Matriks silang (Baris = Nama Layanan, Kolom = Bulan/Tahun, Nilai = Jumlah Kunjungan & Omzet).
    * **Graph View:** Grafik batang dan diagram lingkaran untuk visualisasi Top 5 Service terlaris.

#### D. Sisi SCM Pendukung (Bahan Habis Pakai / Consumables)
* **`mrp` (BoM Kit - Bill of Materials):**
  Layanan seperti *Hair Coloring* atau *Facial Treatment* tidak mengurangi stok jasa, melainkan menghabiskan bahan (tube cat rambut, developer, krim masker, serum). Dengan fitur **BOM tipe Kit**, setiap transaksi layanan otomatis memotong stok bahan baku di gudang secara proporsional.

---

## 3. Matriks Pemetaan Kebutuhan vs Modul Odoo

| Komponen Bisnis | Kasus 1: Bengkel & Carwash | Kasus 2: Salon & Klinik Kecantikan | Modul Utama Odoo |
| :--- | :--- | :--- | :--- |
| **Kapasitas / Jadwal** | Antrean Pit/Bay berbasis status | Jadwal Jam, Kursi, & Terapis | `repair`, `appointment`, `planning` |
| **Aset / Objek Layanan** | Kendaraan (Plat No, KM, Mesin) | Kartu Perawatan Pelanggan (Kulit/Rambut) | `fleet`, `contacts` (extended) |
| **Material SCM** | Suku Cadang, Aki, Oli Mesin | Krim Facial, Pewarna, Serum | `stock`, `mrp` (BoM Kit) |
| **Transaksi Kasir** | Cetak SPK & Invoice Servis | POS Retail + Jasa Kasir Cepat | `point_of_sale`, `account` |
| **Pembayaran** | Digital QRIS / Payment Gateway | QRIS, EDC, Transfer, Cash | `payment` (integrasi gateway) |
| **Analisa Bisnis** | Utilisasi Pit & Penjualan Part | Layanan Terlaris & Produktivitas Terapis | `sale.report`, `pos.order` pivot |

---

## 4. Rencana Tahapan Pengembangan (Development Roadmap)

1. **Review & Penyelarasan Konsep:** Menyetujui arsitektur modul dan alur operasional.
2. **Setup Modul Standar Odoo:** Instalasi dan konfigurasi basis modul (`stock`, `point_of_sale`, `fleet`, `repair`, `appointment`).
3. **Pengembangan Custom Addon (jika diperlukan):**
   * Modul kustom `workshop_management` untuk antrean bay bengkel & rekam servis kendaraan.
   * Modul kustom `salon_management` untuk dual-resource scheduling & customer treatment card.
4. **Integrasi Pembayaran Digital:** Konfigurasi provider QRIS/Payment Gateway.
5. **Testing & User Acceptance Testing (UAT).**
