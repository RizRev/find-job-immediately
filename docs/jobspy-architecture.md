# JobSpy Library Architecture

**Library:** `python-jobspy` v1.1.82  
**Repository:** https://github.com/cullenwatson/JobSpy  
**Installation Location:** `venv/lib/python3.14/site-packages/jobspy/`

---

## Cara Kerja

### Flow Scraping:
1. User calls `scrape_jobs()` dengan parameters (search_term, location, site_name, results_wanted, dll)
2. Buat `ScraperInput` object yang berisi semua parameter
3. `ThreadPoolExecutor` spawns threads untuk scrape setiap site secara **concurrent/parallel**
4. Setiap scraper:
   - Fetch HTML dari job board
   - Parse dengan BeautifulSoup
   - Extract data (title, company, location, URL)
   - Return `JobResponse` object
5. Semua hasil digabung jadi pandas DataFrame

---

## Arsitektur Pattern

### Abstract Base Class

Lokasi: `model.py`

```python
class Scraper(ABC):
    def __init__(self, site: Site, proxies, ca_cert, user_agent):
        self.site = site
        self.proxies = proxies
        self.ca_cert = ca_cert
        self.user_agent = user_agent
    
    @abstractmethod
    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        pass
```

### Scraper Implementation Pattern

- Setiap platform punya folder sendiri: `bayt/`, `indeed/`, `linkedin/`, `glassdoor/`, dll
- Setiap scraper extend dari `Scraper` abstract class
- Must implement `scrape(scraper_input: ScraperInput) -> JobResponse`

### Scraper Mapping

Lokasi: `__init__.py`

```python
SCRAPER_MAPPING = {
    Site.LINKEDIN: LinkedIn,
    Site.INDEED: Indeed,
    Site.ZIP_RECRUITER: ZipRecruiter,
    Site.GLASSDOOR: Glassdoor,
    Site.GOOGLE: Google,
    Site.BAYT: BaytScraper,
    Site.NAUKRI: Naukri,
    Site.BDJOBS: BDJobs,
}
```

---

## Data Model

### Key Classes

**JobPost** - Single job listing dengan fields:
- `id`, `title`, `company_name`, `job_url`, `location`
- `description`, `compensation`, `date_posted`
- `job_type`, `is_remote`, `emails`

**JobResponse** - Collection of JobPost objects
```python
class JobResponse(BaseModel):
    jobs: list[JobPost] = []
```

**Location** - Geographic data
```python
class Location(BaseModel):
    country: Country | str | None = None
    city: Optional[str] = None
    state: Optional[str] = None
```

**Compensation** - Salary information
```python
class Compensation(BaseModel):
    interval: Optional[CompensationInterval] = None
    min_amount: float | None = None
    max_amount: float | None = None
    currency: Optional[str] = "USD"
```

**Site (Enum)** - Platform identifiers
```python
class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIP_RECRUITER = "zip_recruiter"
    GLASSDOOR = "glassdoor"
    GOOGLE = "google"
    BAYT = "bayt"
    NAUKRI = "naukri"
    BDJOBS = "bdjobs"
```

**Country (Enum)** - Country codes dengan subdomain mapping untuk Indeed/Glassdoor

### File Locations

- Main entry: `__init__.py` - scrape_jobs() function
- Models: `model.py` - All data structures
- Utils: `util.py` - Helper functions (logger, session, salary extraction)

---

## Example Scraper Pattern (Bayt)

Lokasi: `bayt/__init__.py`

```python
class BaytScraper(Scraper):
    base_url = "https://www.bayt.com"
    delay = 2
    band_delay = 3
    
    def __init__(self, proxies=None, ca_cert=None, user_agent=None):
        super().__init__(Site.BAYT, proxies=proxies, ca_cert=ca_cert)
        self.session = None
    
    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        self.session = create_session(
            proxies=self.proxies, 
            ca_cert=self.ca_cert, 
            is_tls=False, 
            has_retry=True
        )
        job_list = []
        page = 1
        
        while len(job_list) < scraper_input.results_wanted:
            job_elements = self._fetch_jobs(scraper_input.search_term, page)
            if not job_elements:
                break
                
            for job in job_elements:
                job_post = self._extract_job_info(job)
                if job_post:
                    job_list.append(job_post)
                    if len(job_list) >= scraper_input.results_wanted:
                        break
            
            page += 1
            time.sleep(random.uniform(self.delay, self.delay + self.band_delay))
        
        return JobResponse(jobs=job_list[:scraper_input.results_wanted])
    
    def _fetch_jobs(self, query: str, page: int) -> list | None:
        """Fetch job listings from Bayt"""
        url = f"{self.base_url}/en/international/jobs/{query}-jobs/?page={page}"
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.find_all("li", attrs={"data-js-job": ""})
    
    def _extract_job_info(self, job: BeautifulSoup) -> JobPost | None:
        """Extract job information from HTML element"""
        job_general_information = job.find("h2")
        if not job_general_information:
            return None
        
        job_title = job_general_information.get_text(strip=True)
        job_url = self._extract_job_url(job_general_information)
        
        company_tag = job.find("div", class_="t-nowrap p10l")
        company_name = (
            company_tag.find("span").get_text(strip=True)
            if company_tag and company_tag.find("span")
            else None
        )
        
        location_tag = job.find("div", class_="t-mute t-small")
        location = location_tag.get_text(strip=True) if location_tag else None
        
        location_obj = Location(city=location, country=Country.from_string(self.country))
        
        return JobPost(
            id=f"bayt-{abs(hash(job_url))}",
            title=job_title,
            company_name=company_name,
            location=location_obj,
            job_url=job_url,
        )
```

---

## Key Dependencies

- `beautifulsoup4` - HTML parsing
- `pandas` - DataFrame output
- `requests` / `tls-client` - HTTP requests
- `pydantic` - Data validation
- `markdownify` - Description formatting

---

## Pattern untuk Menambahkan Site Baru

1. **Buat scraper class** yang extend `Scraper`
2. **Implement `scrape()` method** dengan logic:
   - Setup session dengan `create_session()`
   - Loop pagination untuk fetch job listings
   - Parse HTML dengan BeautifulSoup
   - Extract data dan buat `JobPost` objects
   - Return `JobResponse`
3. **Tambahkan ke `Site` enum** di `model.py`
4. **Tambahkan ke `SCRAPER_MAPPING`** di `__init__.py`

---

## Notes

- Library ini adalah **external package**, bukan source code yang kita maintain
- Untuk menambahkan site baru (JobStreet, Glints), ada 3 opsi: Fork repo, Wrapper/Extension, atau Local modification
- Pattern sudah production-ready: concurrent scraping, error handling, rate limiting
- Support multiple countries via `Country` enum dengan subdomain mapping
