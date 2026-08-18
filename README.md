# JobSpy - Job Scraper

Proyek ini menggunakan [python-jobspy](https://github.com/cullenwatson/JobSpy) untuk scraping lowongan pekerjaan dari berbagai platform.

## 🚀 Cara Menjalankan

### 1. Aktifkan Virtual Environment

```bash
source venv/bin/activate
```

### 2. Jalankan Script

```bash
python example.py
```

atau

```bash
python3 example.py
```

### 3. Deaktivasi Virtual Environment (setelah selesai)

```bash
deactivate
```

## 📋 Fitur

Script `example.py` akan:
- Scrape lowongan dari Indeed, LinkedIn, ZipRecruiter, dan Glassdoor
- Mencari posisi "software engineer" di Jakarta, Indonesia
- Mengambil 10 hasil terbaru (72 jam terakhir)
- Menampilkan hasil di terminal
- Menyimpan semua hasil ke file `jobs_results.csv`

## ⚙️ Kustomisasi

Edit `example.py` untuk mengubah parameter pencarian:

```python
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term="software engineer",  # Ubah posisi yang dicari
    location="Jakarta, Indonesia",     # Ubah lokasi
    results_wanted=10,                 # Ubah jumlah hasil
    hours_old=72,                      # Ubah rentang waktu
    country_indeed='Indonesia'
)
```

## 📦 Package yang Terinstall

- python-jobspy==1.1.82
- pandas
- beautifulsoup4
- requests
- Dan dependensi lainnya

## 🔗 Resources

- [JobSpy GitHub](https://github.com/cullenwatson/JobSpy)
- [JobSpy Documentation](https://github.com/cullenwatson/JobSpy#readme)
