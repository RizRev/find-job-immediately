# Extending JobSpy: JobStreet + Glints

**Context:** JobSpy adalah external package (python-jobspy v1.1.82), bukan source code yang kita maintain.

**Goal:** Menambahkan scraper untuk JobStreet dan Glints ke dalam job search pipeline.

---

## Opsi Implementation

### Opsi 1: Fork Official Repository ⭐

**Best for:** Contribution ke community, production use, long-term maintenance

**Pros:**
- Terintegrasi sempurna dengan `scrape_jobs()`
- Bisa contribute balik ke community
- Mengikuti pattern existing yang sudah proven
- Auto-update kalau ada perubahan di core library

**Cons:**
- Setup lebih kompleks
- Perlu maintain fork sendiri
- Harus follow upstream changes
- Review process untuk PR

**Cara:**
1. Fork repository: https://github.com/cullenwatson/JobSpy
2. Clone fork ke local machine
3. Create branch untuk feature baru
4. Tambahkan scraper baru:
   - Buat folder `jobspy/jobstreet/` dengan `__init__.py`
   - Buat folder `jobspy/glints/` dengan `__init__.py`
5. Update `model.py`:
   - Tambahkan `JOBSTREET = "jobstreet"` ke enum `Site`
   - Tambahkan `GLINTS = "glints"` ke enum `Site`
6. Update `__init__.py`:
   - Import scraper classes
   - Tambahkan ke `SCRAPER_MAPPING`
7. Test locally
8. Submit PR ke upstream repository

---

### Opsi 2: Wrapper/Extension 🚀 (RECOMMENDED)

**Best for:** Personal use, quick prototype, flexibility

**Pros:**
- Tidak perlu modify installed package
- Mudah maintain dan iterate
- Bisa custom sesuai kebutuhan tanpa terikat upstream
- No risk hilang saat reinstall package

**Cons:**
- Tidak terintegrasi dengan `scrape_jobs()` langsung
- Perlu wrapper function sendiri
- Duplikasi beberapa logic

**Implementation:**

```python
# File: jobspy_extension.py

from jobspy import scrape_jobs
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import Optional

class JobStreetScraper:
    """Scraper untuk JobStreet Indonesia"""
    
    base_url = "https://www.jobstreet.co.id"
    
    def scrape(
        self, 
        search_term: str, 
        location: str, 
        results_wanted: int = 10
    ) -> pd.DataFrame:
        """
        Scrape jobs dari JobStreet
        Returns DataFrame dengan schema yang sama dengan jobspy
        """
        jobs = []
        page = 1
        
        while len(jobs) < results_wanted:
            # TODO: Implement JobStreet scraping logic
            # - Build search URL
            # - Fetch HTML
            # - Parse job cards
            # - Extract: title, company, location, job_url, date_posted
            pass
        
        return pd.DataFrame(jobs)

class GlintsScraper:
    """Scraper untuk Glints Indonesia"""
    
    base_url = "https://glints.com"
    
    def scrape(
        self, 
        search_term: str, 
        location: str, 
        results_wanted: int = 10
    ) -> pd.DataFrame:
        """
        Scrape jobs dari Glints
        Returns DataFrame dengan schema yang sama dengan jobspy
        """
        jobs = []
        page = 1
        
        while len(jobs) < results_wanted:
            # TODO: Implement Glints scraping logic
            # - Build search URL or API endpoint
            # - Fetch data
            # - Parse response (JSON or HTML)
            # - Extract: title, company, location, job_url, date_posted
            pass
        
        return pd.DataFrame(jobs)

def scrape_all_jobs(
    search_term: str,
    location: str = "Jakarta, Indonesia",
    results_wanted: int = 10,
    include_jobstreet: bool = True,
    include_glints: bool = True,
    **kwargs
) -> pd.DataFrame:
    """
    Wrapper function untuk scrape dari semua sources
    Combines jobspy (Indeed, LinkedIn, dll) + custom scrapers (JobStreet, Glints)
    """
    all_dfs = []
    
    # Scrape dari jobspy platforms (Indeed, LinkedIn, dll)
    try:
        jobs_df = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            country_indeed='Indonesia',
            **kwargs
        )
        all_dfs.append(jobs_df)
        print(f"✅ JobSpy platforms: {len(jobs_df)} jobs")
    except Exception as e:
        print(f"❌ JobSpy error: {e}")
    
    # Scrape dari JobStreet
    if include_jobstreet:
        try:
            jobstreet_df = JobStreetScraper().scrape(
                search_term=search_term,
                location=location,
                results_wanted=results_wanted
            )
            all_dfs.append(jobstreet_df)
            print(f"✅ JobStreet: {len(jobstreet_df)} jobs")
        except Exception as e:
            print(f"❌ JobStreet error: {e}")
    
    # Scrape dari Glints
    if include_glints:
        try:
            glints_df = GlintsScraper().scrape(
                search_term=search_term,
                location=location,
                results_wanted=results_wanted
            )
            all_dfs.append(glints_df)
            print(f"✅ Glints: {len(glints_df)} jobs")
        except Exception as e:
            print(f"❌ Glints error: {e}")
    
    # Combine all results
    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        return combined.sort_values(by=['site', 'date_posted'], ascending=[True, False])
    else:
        return pd.DataFrame()

# Usage example:
if __name__ == "__main__":
    jobs = scrape_all_jobs(
        search_term="software engineer",
        location="Jakarta, Indonesia",
        results_wanted=10
    )
    
    print(f"\n📊 Total: {len(jobs)} jobs found")
    jobs.to_csv("all_jobs_results.csv", index=False)
```

---

### Opsi 3: Local Modification ⚠️

**Best for:** Quick testing only

**NOT RECOMMENDED** karena:
- ⚠️ **HILANG** kalau reinstall/update package
- Tidak portable ke environment lain
- Bad practice untuk production
- Sulit di-track di version control

---

## Challenges untuk JobStreet & Glints

### 1. Anti-scraping Protection
**Problem:** Modern websites pakai CAPTCHA, rate limiting, Cloudflare

**Solutions:**
- Gunakan proxies (already supported di jobspy via `proxies` parameter)
- Gunakan `tls-client` instead of `requests` (already available di jobspy)
- Add random delays between requests
- Rotate user agents
- Respect `robots.txt`

### 2. Dynamic Content (React/Vue)
**Problem:** Kalau website render via JavaScript, BeautifulSoup tidak bisa parse

**Solutions:**
- Analyze network requests di DevTools untuk find API endpoints
- Kalau ada public API, hit directly (faster + more reliable)
- Last resort: Gunakan Selenium atau Playwright (slower, heavier)

### 3. Data Structure Differences
**Problem:** JobStreet/Glints bisa punya custom fields yang tidak ada di `JobPost` model

**Solutions:**
- Map ke existing fields yang paling dekat
- Pakai `description` field untuk extra info
- Kalau fork: extend `JobPost` model dengan optional fields

### 4. Legal & ToS Considerations
**Problem:** Scraping might violate Terms of Service

**Solutions:**
- Check apakah ada official API (Glints punya?)
- Add disclaimer di documentation
- Respect rate limits dan robots.txt
- Consider untuk personal/research use only

---

## Implementation Checklist

Untuk setiap scraper baru:

- [ ] **Research Phase**
  - [ ] Analyze HTML structure atau API endpoints (DevTools Network tab)
  - [ ] Check robots.txt
  - [ ] Identify anti-scraping measures
  - [ ] Document URL patterns dan pagination logic

- [ ] **Development Phase**
  - [ ] Buat scraper class dengan `scrape()` method
  - [ ] Implement `_fetch_jobs()` untuk get job listings
  - [ ] Implement `_extract_job_info()` untuk parse individual job
  - [ ] Handle pagination properly
  - [ ] Extract minimal fields: title, company, location, job_url
  - [ ] Optional: description, date_posted, salary

- [ ] **Quality Phase**
  - [ ] Add rate limiting / random delays (avoid ban)
  - [ ] Error handling dan logging
  - [ ] Return pandas DataFrame dengan schema yang sama
  - [ ] Test dengan berbagai search terms
  - [ ] Test dengan berbagai locations

- [ ] **Integration Phase**
  - [ ] Integrate dengan existing jobspy results
  - [ ] Test combined output
  - [ ] Add to documentation

---

## DataFrame Schema (untuk konsistensi)

Pastikan output DataFrame punya kolom ini (minimal):

```python
columns = [
    'site',           # "jobstreet" atau "glints"
    'title',          # Job title
    'company',        # Company name
    'location',       # "Jakarta, Indonesia"
    'job_url',        # Direct link ke job posting
    'date_posted',    # Date object (optional)
    'description',    # Job description (optional)
]
```

---

## Next Steps

1. **Analyze Target Sites:**
   - Visit JobStreet dan Glints
   - Perform manual search
   - Inspect network traffic di DevTools
   - Identify API endpoints atau HTML structure

2. **Start with One Scraper:**
   - Implement JobStreet ATAU Glints dulu (not both)
   - Test thoroughly
   - Iterate based on hasil

3. **Expand:**
   - Add second scraper
   - Improve error handling
   - Add features (filters, sorting, etc.)

---

## Resources

- JobSpy GitHub: https://github.com/cullenwatson/JobSpy
- JobStreet Indonesia: https://www.jobstreet.co.id
- Glints: https://glints.com/id
- BeautifulSoup Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Pandas Docs: https://pandas.pydata.org/docs/
