#!/usr/bin/env python3
"""
Contoh penggunaan JobSpy untuk scraping lowongan pekerjaan
"""

from jobspy import scrape_jobs
import sys

def main():
    print("🔍 Memulai pencarian lowongan pekerjaan...\n")

    try:
        # Scrape jobs dari berbagai platform
        # Catatan: Beberapa situs mungkin memblokir akses (error 403)
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],  # Fokus ke Indeed dan LinkedIn dulu
            search_term="software engineer",
            location="Jakarta, Indonesia",
            results_wanted=10,  # Jumlah hasil yang diinginkan
            hours_old=72,  # Lowongan dalam 72 jam terakhir
            country_indeed='Indonesia'  # Untuk Indeed
        )

        print(f"\n✅ Berhasil menemukan {len(jobs)} lowongan pekerjaan!\n")

        # Tampilkan beberapa hasil
        if len(jobs) > 0:
            print("=" * 80)
            for idx, job in jobs.head(5).iterrows():
                print(f"\n📌 Job #{idx + 1}")
                print(f"   Judul: {job.get('title', 'N/A')}")
                print(f"   Perusahaan: {job.get('company', 'N/A')}")
                print(f"   Lokasi: {job.get('location', 'N/A')}")
                print(f"   Situs: {job.get('site', 'N/A')}")
                print(f"   Link: {job.get('job_url', 'N/A')[:100]}...")
                print("-" * 80)

            # Simpan ke CSV
            output_file = "jobs_results.csv"
            jobs.to_csv(output_file, index=False)
            print(f"\n💾 Hasil lengkap disimpan ke: {output_file}")
            print(f"📊 Total kolom data: {list(jobs.columns)}")
        else:
            print("❌ Tidak ada lowongan ditemukan. Coba ubah parameter pencarian.")
            print("💡 Tip: Coba lokasi lain atau kata kunci berbeda")

    except Exception as e:
        print(f"\n❌ Error saat scraping: {e}")
        print("\n💡 Tips troubleshooting:")
        print("   - Beberapa situs mungkin memblokir akses otomatis")
        print("   - Coba gunakan VPN atau ubah koneksi internet")
        print("   - Coba kurangi jumlah results_wanted")
        sys.exit(1)

if __name__ == "__main__":
    main()
