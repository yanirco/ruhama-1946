# Publishing this site

Everything is built and committed. What's left needs your accounts — I can't buy a domain or push to your GitHub. Here is the whole path, in order, about 30 minutes.

---

## 0. The domain: `ruhama1946.site` ✅ bought

Registered 10 August 2026. The whole repo is already pointed at it — canonical URL, both `hreflang` links, `og:url`, `og:image`, `robots.txt` and `sitemap.xml`. **Nothing to edit.**

### ⚠️ One diary entry to make now

`.site` costs about **$1 for the first year and roughly $32/year to renew.** So:

| | Cost |
|---|---|
| Aug 2026 – Aug 2027 | ~$1 |
| Every year after | ~$32 |

**Set a calendar reminder for mid-July 2027**, two things on it:

1. **Turn off auto-renew** in Namecheap if you don't want the ~$32 to land silently, *or* budget for it deliberately.
2. **Decide whether to move.** Moving is cheap: this is a static site, and the domain string appears in exactly five files. Buy `ruhama1946.org` (~$11/yr flat), run the one command in step 4, add the new domain in Render, and set a permanent redirect from the old one. Half an hour, and the links people have already shared keep working.

Do not let the domain lapse without redirecting. A memorial page that 404s is worse than one that moved.

---

## 1. GitHub — ✅ repo created, ⬜ push pending

**Repository:** https://github.com/yanirco/ruhama-1946 — public, empty, correctly configured (no README, no .gitignore, no licence, so your first push won't be rejected).

The local repo at `ruhama-1946-site/` has 79 files, 11 MB, one commit on `main`. Push it:

```bash
cd ~/Workspace/ruhama80britishWea\[ponSearch/ruhama-1946-site

# one-time cleanup: the sandbox this was built in couldn't delete its own lock
# and temp files, so clear them before the first push
rm -f .git/*.lock
find .git/objects -name 'tmp_obj_*' -delete
git gc --prune=now -q

# commit the domain change and this guide (the stale lock blocked it earlier)
git add -A && git commit -m "Point metadata at ruhama1946.site; add deployment guide"

git remote add origin https://github.com/yanirco/ruhama-1946.git
git push -u origin main
```

If it asks for a password, GitHub wants a **personal access token**, not your account password. Two easier routes:

- **GitHub CLI** — `brew install gh && gh auth login`, then the push just works.
- **GitHub Desktop** — File → Add Local Repository → point at `ruhama-1946-site` → Publish. No tokens, no terminal.

You'll know it worked when the repo page shows 79 files instead of the setup instructions.

---

## 2. Render — the site itself

Free. Static sites on Render cost nothing and include TLS and a CDN.

1. **render.com** → sign in with GitHub
2. **New → Static Site** → pick `ruhama-1946`
3. Settings:
   - **Build command:** *(leave empty)*
   - **Publish directory:** `.`
4. **Create Static Site**

It deploys in under a minute and gives you `ruhama-1946-XXXX.onrender.com`. Open it and check the Hebrew/English toggle and a couple of photographs before going further.

`render.yaml` in the repo already sets cache headers (images cached for a year, HTML always revalidated so corrections reach readers immediately) and the pretty URLs `/story` and `/timeline`.

---

## 3. Namecheap — point the domain at Render

Domain's bought. Two housekeeping checks first, in **Domain List → Manage**:

- **WhoisGuard / Domain Privacy: ON.** Free, and it keeps your home address out of the public WHOIS record.
- You do **not** need their hosting, email, "PremiumDNS" or SSL. Render provides TLS free.

**Point it at Render:**

In Render: your site → **Settings → Custom Domains → Add Custom Domain**. Add both `ruhama1946.site` and `www.ruhama1946.site`. Render will show you what it wants.

In Namecheap: **Domain List → Manage → Advanced DNS**. Delete the two default parking records ("CNAME www → parkingpage" and "URL Redirect @"), then add:

| Type | Host | Value | TTL |
|---|---|---|---|
| ALIAS Record | `@` | `ruhama-1946-XXXX.onrender.com` | Automatic |
| CNAME Record | `www` | `ruhama-1946-XXXX.onrender.com` | Automatic |

Namecheap supports **ALIAS** on an apex domain, which is what Render recommends — it follows Render's load balancer if the IP ever changes. Only if ALIAS is unavailable, use `A Record · @ · 216.24.57.1` instead.

Back in Render, click **Verify**. DNS usually propagates in 5–30 minutes; TLS is issued automatically once it resolves. If the certificate doesn't issue, it is almost always a leftover parking record — check Advanced DNS again.

---

## 4. Changing the domain later

Not needed now — the repo already says `ruhama1946.site`. Keep this for July 2027, or if you ever move.

One command swaps it across `index.html` (canonical, both `hreflang` links, `og:url`, `og:image`), `robots.txt`, `sitemap.xml`, `README.md` and this file:

```bash
cd ~/Workspace/ruhama80britishWea\[ponSearch/ruhama-1946-site
grep -rl 'ruhama1946\.site' . --exclude-dir=.git \
  | xargs sed -i '' 's/ruhama1946\.site/NEWDOMAIN/g'
git commit -am "Point metadata at the new domain" && git push
```

Then in Render add the new domain alongside the old one, and keep the old one attached with a redirect for as long as you're paying for it. Render redeploys automatically on every push.

---

## 5. Before you announce it

From `NOTICE.md`, and I'd hold the launch for these:

- [ ] **The Kibbutz Ruhama Archive has approved it.** These are their photographs and their community's record of what was done to it. The site credits them throughout, but crediting is not the same as asking.
- [ ] **The siege dates are confirmed from a primary source.** Sources split between 28 August / six days and 25 August / seven. The site says 28 August. The *Mishmar* clipping on the board is headed "day five of the siege" — one clean scan of its date line settles it.
- [ ] **Anyone traceable in the photographs has been consulted.** Four people appear. They were photographed during the worst week of their year, in their own home, without being asked.

The 80th anniversary is **28 August 2026** — 18 days out. That is comfortable for steps 1–4 and tight but achievable for the sign-offs. If the archive can't review in time, publish on a quiet URL and announce after they've seen it. The date is a good hook, not a deadline worth spending someone else's trust on.

---

## Running costs

| | Year 1 | Year 2 onwards |
|---|---|---|
| Render static site | $0 | $0 |
| TLS certificate | $0 (automatic) | $0 |
| `ruhama1946.site` | ~$1 | **~$32** |
| **Total** | **~$1** | **~$32** — see the diary note in step 0 |

Render's free static tier includes 100 GB of bandwidth a month. This site is 11 MB, so that is roughly 9,000 full visits — and nearly everyone loads a fraction of that because the images are cached for a year.

---

Sources: [Render — Configuring Namecheap DNS](https://render.com/docs/configure-namecheap-dns) · [Render — Custom Domains](https://render.com/docs/custom-domains) · [Namecheap domain pricing](https://www.namecheap.com/domains/) · [TLD price comparison](https://tld-list.com/registrars/namecheap)
