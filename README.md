# Ceylon Micro Credit – Website

Company website for **Ceylon Micro Credit**, 62, Jaya Mawatha, Kadawatha · Tel 011-2224578.
Built with **Python (Flask)**, **SQL (SQLAlchemy – SQLite by default, MySQL/SQL Server ready)** and a
**Bootstrap 5** front end in the company colours: black, red and white.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5090. On Windows you can also double-click `run.bat`.

The database (`instance/ceylon_micro_credit.db`) and all default content are created automatically the first time the site starts.

## Admin panel – edit the site without touching code

URL: http://localhost:5090/admin (there is also a "Staff login" link in the footer)

Default login: `admin` / `ChangeMe@123`. **Change it right away** under *Change Password*,
or set `ADMIN_USERNAME` / `ADMIN_PASSWORD` in `.env` before the first run.

| Admin page      | What you can change |
|-----------------|--------------------|
| Applications    | Loan applications and contact messages from the website, with status and internal notes |
| Products        | Add, edit, hide or delete loans: text, features, documents, amounts, rates, terms |
| Categories      | The top menu groups (Business Loans, Micro Leasing, Micro Group Loans), or add new ones |
| Home Slides     | Homepage banner slides, with image upload |
| News & Events   | News, notices, tenders and auctions, with image upload |
| Site Settings   | Company name, address, phone, email, hours, About text, values, counters, Facebook/WhatsApp |

## Project structure

```
app.py             App setup, CSRF protection, template filters
config.py          Settings (database URL, secret key, port) – override via .env
models.py          SQL tables: settings, categories, products, inquiries, slides, news, admin_users
seed.py            Default content (python seed.py --reset rebuilds the DB – deletes data!)
routes_public.py   Public pages: home, about, services, product, calculator, apply, contact, news
routes_admin.py    Admin panel
templates/         Jinja2 HTML (base.html = header/footer, _macros.html = reusable cards)
templates/admin/   Admin panel HTML
static/css/style.css   All styling – brand colours are the variables at the top
static/js/main.js      Loan calculator and animated counters
static/uploads/        Images uploaded from the admin panel
```

## Images

The site comes with free photos from [Pexels](https://www.pexels.com/license/), which allows commercial use.
They are stored in `static/img/stock/`, so they work without internet.
Their names are listed in `IMAGE_KEYS` at the top of `seed.py`.

To change a picture, upload your own photo or paste an image link:

| Picture | Where to change it |
|---------|--------------------|
| Home page banner slides | Admin → Home Slides |
| Product photos | Admin → Products → Edit |
| Category banners (also used on product pages) | Admin → Categories → Edit |
| About / Services / Calculator / Apply / Contact / News banners, home "About us" photo | Admin → Site Settings → Page images |
| News photos | Admin → News & Events |

Your own photos of the Kadawatha office, staff and real customers (with their permission) will always look best.
`python seed.py --images` restores the default photo on any item that has no picture.

## Common changes

- **Colours:** edit `--red`, `--black` etc. at the top of `static/css/style.css`.
- **Logo:** replace the red "CMC" box (`brand-mark` in `templates/base.html`) with
  `<img src="{{ url_for('static', filename='img/logo.png') }}" height="46">`.
- **New page:** add a route in `routes_public.py` and a template that starts with `{% extends "base.html" %}`.
- **New loan type:** no code needed. Use Admin → Products → Add product.
- **Use MySQL / SQL Server:** install the driver (see `requirements.txt`) and set `DATABASE_URL` in `.env`.

## Going live

1. Copy `.env.example` to `.env`, set a long random `SECRET_KEY` and a strong admin password.
2. Run with a production server, e.g. `gunicorn app:app` (Linux) or `waitress-serve --port=5090 app:app` (Windows).
3. Put it behind HTTPS (e.g. through your hosting provider, or Nginx with Let's Encrypt).

## Hosting on Render

The repository includes `render.yaml`, which creates everything in one step:
the website (free plan, Singapore region) plus a PostgreSQL database.

1. Push this folder to a GitHub repository (private is fine).
2. On https://dashboard.render.com go to **New → Blueprint**, connect GitHub and pick the repository.
3. When asked, type your **ADMIN_PASSWORD** (at least 8 characters). Render generates `SECRET_KEY`
   and connects `DATABASE_URL` automatically.
4. Click **Apply**. After a few minutes the site is live at `https://ceylon-micro-credit.onrender.com`
   (or a similar address). All default content is created on the first start.

After that, every `git push` to the repository redeploys the site automatically.

Things to know about the free plan:
- The site goes to sleep after 15 minutes without visitors, so the first visit afterwards takes about a minute.
- The **free PostgreSQL database expires after 30 days**. Upgrade it (Render → the database → Upgrade)
  before then, or loan applications and admin changes will be lost.
- Images uploaded from the admin panel are stored in the database, so they survive restarts.
- To use your own domain (e.g. ceylonmicrocredit.lk): Render → the web service → Settings → Custom Domains.

## Live website (PythonAnywhere) and updating it

Live site: https://ceylonmicrocredit.pythonanywhere.com (admin: `/admin`).

Keep the local copy and the live site the same:

1. Change and test on your computer: `python app.py` → http://localhost:5090
2. Double-click **`deploy.bat`**, type a short description, press Enter (sends the changes to GitHub)
3. On the live Admin panel click **Update Website → Update from GitHub** (deploy.bat opens that page for you)

Only code, design and default photos travel this way. Products, settings, applications and uploads
edited in each Admin panel stay separate (local database = test data, live database = real data).

PythonAnywhere free plan: log in once a month and click **Run until 1 month from today** on the Web tab.
