# Odoo Service Supply Chain Management (SSCM)

Repositori ini memuat rancangan arsitektur, panduan alur operasional, spesifikasi kebutuhan, dan implementasi **Service Supply Chain Management (SSCM)** berbasis ERP Odoo untuk dua jenis bisnis jasa:
1. **Bengkel & Carwash (Automotive Workshop & Detailing)**
2. **Salon, Barbershop, & Klinik Kecantikan (Beauty & Wellness Clinic)**

> * Dokumen spesifikasi kebutuhan produk: [PRD.md](file:///c:/Users/ZYREX/Documents/odoo-SSCM/PRD.md)
> * Dokumen arsitektur teknis & ERD: [ARCHITECTURE.md](file:///c:/Users/ZYREX/Documents/odoo-SSCM/ARCHITECTURE.md)
> * Status Implementasi Live: **Aktif & Teruji di Odoo SaaS (`https://bengkelhanin1.odoo.com`)**

---

## 1. Pengertian: SCM Tradisional vs Service SCM (SSCM)

### SCM Tradisional (Barang Fisik)
Pada rantai pasok konvensional, arus utama adalah pergerakan barang fisik:
$$\text{Supplier} \longrightarrow \text{Bahan Baku} \longrightarrow \text{Pabrik / Manufaktur} \longrightarrow \text{Gudang / Distribusi} \longrightarrow \text{Pelanggan}$$
Tujuannya adalah memastikan ketersediaan barang jadi pada kuantitas dan waktu yang tepat dengan biaya logistik serendah mungkin.

### Service SCM / SSCM (Bisnis Jasa)
Pada bisnis layanan, produk yang dijual adalah **pelayanan**, bukan barang jadi. Karakteristik pembedanya:
1. **Perishability (Kapasitas Waktu Bersifat Hangus):**
   Kapasitas kursi salon atau pit bengkel yang menganggur selama 2 jam tidak dapat disimpan di gudang untuk dijual besok.
2. **Simultaneity (Produksi dan Konsumsi Terjadi Bersamaan):**
   Layanan diproduksi dan dikonsumsi secara *real-time* di hadapan pelanggan.
3. **Dual Supply Chain (Rantai Pasok Ganda):**
   * **Rantai Kapasitas (Capacity Chain):** Manajemen waktu ketersediaan tenaga ahli (mekanik, terapis, dokter) dan fasilitas fisik (kursi, bed, pit/bay lift).
   * **Rantai Material Pendukung (Consumables Chain):** Manajemen bahan habis pakai dan suku cadang (oli, busi, sampo mobil, serum wajah, krim pewarna rambut).

---

## 2. Alur Operasional Langkah demi Langkah (User Journey)

```
[Tahap 1: Inisiasi] ──> [Tahap 2: Alokasi Kapasitas] ──> [Tahap 3: Eksekusi & Konsumsi] ──> [Tahap 4: QC & Finalisasi] ──> [Tahap 5: Kasir & Pembayaran]
```

### Tahap 1: Inisiasi & Check-In Pelanggan (Front Desk)
* **Bengkel & Carwash:**
  * Pelanggan datang *walk-in* atau reservasi. Service Advisor (SA) mencari/input nomor polisi di modul `fleet.vehicle` yang terhubung ke data pelanggan (`res.partner`).
  * Input Odometer (KM) saat masuk dan catatan keluhan/permintaan servis.
  * Menghasilkan **Surat Perintah Kerja (SPK) / Draft Repair Order**.
* **Salon & Klinik Kecantikan:**
  * Pelanggan datang *walk-in* atau reservasi via `appointment`.
  * Resepsionis membuka profil pelanggan (`res.partner`) dan mengecek tab **Treatment History**: memeriksa formula pewarna rambut sebelumnya, catatan alergi kulit, atau resep dokter.
  * Menghasilkan **Service Order / Appointment Ticket**.

### Tahap 2: Alokasi Kapasitas Antrean (Resource Scheduling)
* **Bengkel & Carwash:**
  * SPK dialokasikan ke **Bay / Pit / Lift Servis** yang kosong (misal: Pit 2 Servis Ringan) dan menugaskan Mekanik penanggung jawab.
  * Tampil di **Kanban Board Antrean** di ruang bengkel (*Shop Floor Display*).
* **Salon & Klinik Kecantikan:**
  * Modul `appointment` / `planning` mengunci jam reservasi.
  * Sistem memvalidasi ketersediaan ganda: Kursi/Bed terkunci dan Terapis/Dokter terkunci. Validasi backend mencegah *double-booking* secara otomatis.

### Tahap 3: Eksekusi Layanan & Konsumsi Material (The Core SCM)
* **Bengkel & Carwash:**
  * Mekanik mengubah status menjadi `Sedang Dikerjakan`.
  * Kebutuhan suku cadang (oli, filter, kampas rem) dimasukkan ke baris order servis. Odoo memeriksa ketersediaan stok gudang secara *real-time* dan mencadangkan (*reserved*) barang tersebut.
* **Salon & Klinik Kecantikan:**
  * Terapis membawa pelanggan ke kursi/bed dan memulai perawatan.
  * Layanan yang memiliki **BOM tipe Kit** (misal: Facial Acne membutuhkan 1 ampul serum, 20g masker, spuit steril) otomatis mencatat bahan habis pakai yang terpakai di gudang kabinet salon.

### Tahap 4: Quality Control, Serah Terima, & Rekam Historis
* **Bengkel & Carwash:**
  * Foreman / QC memeriksa hasil kerja; kendaraan diarahkan ke Bay Cuci (Carwash) untuk *finishing*.
  * Odometer terbaru tersimpan permanen di `fleet.vehicle`, riwayat suku cadang tercatat, dan Odoo mengkalkulasi estimasi servis berkala berikutnya (misal: 6 bulan / 10.000 KM ke depan).
* **Salon & Klinik Kecantikan:**
  * Hasil perawatan diperlihatkan ke pelanggan; staf mendokumentasikan foto *After* (pada klinik estetika).
  * Catatan formula baru atau reaksi kulit dicatat pada riwayat perawatan pelanggan untuk referensi kunjungan berikutnya.

### Tahap 5: Kasir, Pembayaran Digital, & Otomatisasi Akuntansi
* **Bengkel & Carwash:**
  * Kasir memanggil No. Polisi / SPK di modul POS / Invoicing. Seluruh biaya jasa, suku cadang, dan cuci terangkum otomatis.
  * Pelanggan memindai **QRIS Dinamis** di layar kasir. Begitu terbayar, webhook otomatis mengubah status menjadi **Paid**, stok suku cadang tervalidasi keluar gudang, dan jurnal pendapatan + HPP terbentuk tanpa rekonsiliasi manual.
* **Salon & Klinik Kecantikan:**
  * Kasir memanggil nama pelanggan di Odoo POS. Paket treatment dan produk *skincare homecare* tambahan langsung tampil.
  * Pelanggan membayar via QRIS/EDC. Stok bahan terpotong otomatis dari sistem, dan komisi terapis langsung terkalkulasi.

---

## 3. Fitur Utama: Garansi Servis & Komisi Karyawan

### A. Garansi Servis & Penanganan Klaim (Service Warranty)
* **Pada Bengkel:**
  * **Garansi Jasa:** Otomatis berlaku 14 hari atau 1.000 KM setelah pengerjaan.
  * **Garansi Suku Cadang:** Khusus part bernomor seri (misal: Aki garansi 12 bulan dengan *Serial Number Tracking*).
  * **Alur Klaim:** Diterbitkan **Warranty Claim Order** tertaut ke SPK asli. Biaya jasa kepada pelanggan digratiskan (**Rp 0**), sedangkan suku cadang cacat pabrik diretur ke vendor (*Vendor Return & Credit Note*).
* **Pada Salon & Klinik:**
  * **Garansi Revisi / Retouch:** Garansi 3–7 hari untuk pewarnaan rambut yang tidak merata atau perbaikan *nail art*.
  * **Alur Klaim:** Dibuatkan sesi *touch-up* gratis dengan penugasan ke terapis terkait untuk menjaga kepuasan pelanggan, tercatat sebagai biaya jaminan mutu internal.

### B. Sistem Komisi & Insentif Karyawan (Commission Engine)
* **Struktur Komisi:**
  1. **Komisi Jasa Servis:** Persentase (%) dari nilai jasa (misal: Mekanik 15% dari jasa servis; Terapis 15%–20% dari nilai *treatment*).
  2. **Insentif Up-Selling Produk (Retail):** Bonus penjualan produk *homecare* salon atau aksesoris mobil (misal: 5%–10% dari harga jual produk retail).
  3. **Komisi Tim / Pool (Carwash Bay):** Insentif berbasis kelompok yang dibagi rata per unit kendaraan yang dicuci.
* **Otomatisasi:** Terhitung otomatis saat tagihan berstatus **Paid** dan terhubung ke slip gaji (`hr.payslip`).

---

## 4. Dua Pendekatan Implementasi (Dual Implementation Delivery)

Proyek ini menyediakan dua mode implementasi:

### Pendekatan 1: Live SaaS & Studio API Deployment (Aktif di `bengkelhanin1.odoo.com`)
* **Host:** `https://bengkelhanin1.odoo.com` (Odoo 20.0+e)
* **Metode:** Integrasi JSON-RPC & Studio Metadata API (`ir.model.fields`, `ir.ui.view`).
* **Status:**
  * 7 Modul Fondasi Terpasang: `repair`, `fleet`, `stock`, `point_of_sale`, `account`, `hr`, `appointment`.
  * 17 Custom Fields Diterapkan pada `fleet.vehicle`, `repair.order`, `res.partner`, dan `hr.employee`.
  * Tampilan Antrean Kanban Visual & Form Inherited telah aktif.
  * Data master percontohan aktif (Budi Santoso, Toyota Avanza B 1234 ABC, SPK `WH/RO/00002` di Pit 1, Citra Lestari, Siti Rahmawati, Joko Susanto).

### Pendekatan 2: Standalone Codebase Addons (Tersedia di Direktori `addons/`)
Untuk deployment pada **Odoo.sh** atau **On-Premise**, paket modul Python mandiri telah tersedia:
* **`addons/sscm_core`:** Fondasi buku besar komisi staf (`service.commission.line`) dan aturan keamanan grup.
* **`addons/sscm_workshop`:** Manajemen antrean bay bengkel, SPK servis, kendaraan pelanggan, dan klaim garansi.
* **`addons/sscm_salon`:** Dual-resource booking kursi & terapis dengan pencegahan bentrok jadwal, kartu perawatan pelanggan, dan retouch.

---

## 5. Matriks Pemetaan Kebutuhan vs Modul Odoo

| Komponen Bisnis | Kasus 1: Bengkel & Carwash | Kasus 2: Salon & Klinik Kecantikan | Modul Utama Odoo |
| :--- | :--- | :--- | :--- |
| **Kapasitas / Antrean** | Antrean Pit/Bay berbasis status | Jadwal Jam, Kursi, & Terapis | `repair`, `mrp`, `appointment`, `planning` |
| **Aset / Objek Layanan** | Kendaraan (Plat No, KM, Mesin) | Kartu Perawatan Pelanggan (Kulit/Rambut) | `fleet`, `contacts` (extended) |
| **Material SCM** | Suku Cadang, Aki, Oli Mesin | Krim Facial, Pewarna, Serum | `stock`, `mrp` (BoM Kit) |
| **Garansi Servis** | Garansi 14 Hari / 1.000 KM & Part Serial | Garansi Retouch Warna / Nail Art 7 Hari | Custom `service_warranty` / `repair` |
| **Komisi Staf** | Komisi Jasa Mekanik + Insentif Cuci | Komisi Treatment + Bonus Skincare | Custom `commission_engine` + `hr_payroll` |
| **Transaksi Kasir** | Cetak SPK & Invoice Servis | POS Retail + Jasa Kasir Cepat | `point_of_sale`, `account` |
| **Pembayaran** | Digital QRIS / Payment Gateway | QRIS, EDC, Transfer, Cash | `payment` (integrasi gateway) |
| **Analisa Bisnis** | Utilisasi Pit & Penjualan Part | Layanan Terlaris & Produktivitas Terapis | `sale.report`, `pos.order` pivot |
