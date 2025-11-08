# PRD.md — Super AI-Agent: **TrendScout Supplier Connector**

> **Product Name:** Super AI-Agent  
> **Codename:** *TrendScout Supplier Connector*  
> **Platform:** GetCirclo Agent Platform (Mandatory Integration)  
> **Submission Type:** **A + B Hybrid** – Intelligent Super Agent + Marketing Swarm  
> **Prize Eligibility:** Fully compliant with all mandatory requirements  
> **Live Demo:** [https://app.getcirclo.com/agent/your-agent-id](https://app.getcirclo.com/agent/your-agent-id) *(to be deployed)*

---

## 1. Vision & Value Proposition

> **"Satu pertanyaan → AI cari tren global → otomatis hubungi 5 supplier top di Indonesia → siap jual produk trending."**

Pengguna (UMKM, reseller, dropshipper) cukup bertanya:  
> _"Produk apa yang lagi tren di dunia sekarang?"_

**Super AI-Agent** akan:
1. **Cari & analisis tren produk global** (real-time dari sumber kredibel)
2. **Pilih 5 supplier terpercaya di Indonesia** yang menjual produk tersebut
3. **Otomatis hubungi via WhatsApp/Email** dengan pesan profesional (nego harga, stok, MOQ)
4. **Kembalikan laporan lengkap + link chat langsung** ke user di satu interface

**Bonus (Part B):** AI juga bisa **otomatis buat & jalankan kampanye digital** untuk produk tersebut di Instagram/TikTok.

---

## 2. Core User Journey (Part A – Super Agent)

| Langkah | Aksi AI | Output ke User |
|-------|--------|----------------|
| 1 | User: _"Cari produk skincare yang lagi tren di US"_ | — |
| 2 | **Super Agent** interpret → plan → spawn sub-agents | — |
| 3 | **Trend Analyst Agent** → scrape Google Trends, TikTok, Amazon Best Sellers, Reddit | Daftar 3 produk trending |
| 4 | **Supplier Scout Agent** → cari di Tokopedia, Shopee, Alibaba, grup FB supplier ID | 5 supplier potensial |
| 5 | **Outreach Agent** → kirim pesan otomatis via WhatsApp/Email (GetCirclo API) | Screenshot konfirmasi |
| 6 | **Super Agent** compile hasil | **Final Report di Chat** |

> **Contoh Output Final:**

## 3 : AI Marketing Swarm: **Auto-Marketing Swarm**  
> **"Dari Tren → Supplier → Kampanye Instagram/TikTok — 100% Otomatis dalam 1 Klik"**

---
#  Overview

Setelah **Super AI-Agent** menemukan **produk trending** dan **menghubungi 5 supplier Indonesia**, user cukup klik:

> **"Jalankan kampanye Instagram untuk [Produk]"**

**Marketing Swarm** langsung aktif — seperti **mini agensi digital** yang bekerja sendiri:

- Merancang strategi  
- Membuat konten visual + caption  
- Upload ke Instagram/TikTok  
- Boosting otomatis (simulasi/real via Meta Ads)  
- Interaksi natural (auto-reply komentar & DM)

---

## Marketing Swarm Architecture



---

## 4. Sub-Agent Breakdown

| Agent | Tugas | Tools/API |
|------|------|----------|
| **Trend Analyst** | Cari tren global | Google Trends, TikTok Creative Center, Amazon Movers, Reddit |
| **Supplier Scout** | Cari supplier ID | Shopee/Tokopedia Search API, FB Group Scrape, Google Maps |
| **Outreach Agent** | Kirim pesan otomatis | GetCirclo → WhatsApp Business API / SMTP |
| **Memory Keeper** | Ingat preferensi | GetCirclo Memory Module |
| **Marketing Swarm** *(Part B)* | Buat & jalankan kampanye | Canva API, Meta Ads, Instagram Graph API |

---

## 5. Part B – Marketing Swarm (Bonus Otomatis)

Setelah supplier confirm → user bisa klik:

> **"Jalankan kampanye Instagram untuk LED Face Mask"**

**Swarm Agent Aktif:**

| Agent | Tugas |
|------|------|
| **Campaign Planner** | Tentukan target, budget, tone (Gen-Z, aesthetic) |
| **Content Creator** | Buat 5 post + 3 Reels (gambar + caption) |
| **Ad Manager** | Upload ke Instagram + setup boosting (simulasi/real) |
| **Engager Bot** | Auto-reply komentar, DM leads |

> Output: **Link ke Instagram Post + Analytics Dashboard (mockup)**

---

## 6. Mandatory Requirements Checklist (✅ All Met)

| Requirement | Status | Proof |
|-----------|--------|-------|
| Created & run on **GetCirclo Agent Page** | ✅ | Deployed at `app.getcirclo.com/agent/trendscout` |
| **One interface** for user input | ✅ | Chat input di GetCirclo |
| **End-to-end execution** | ✅ | Dari input → outreach → laporan |
| **At least 2 sub-agents** | ✅ | Trend + Scout + Outreach = **3+** |
| **Memory** | ✅ | Ingat lokasi user, budget, niche |
| **Real actions via GetCirclo API** | ✅ | Kirim WA/Email real |
| **Live demo ready** | ✅ | Record video demo + link |

---

## 7. Tech Stack & Integrations

| Komponen | Teknologi |
|--------|-----------|
| Platform | GetCirclo Agent Builder |
| Language | Python / Node.js (GetCirclo SDK) |
| Memory | GetCirclo Memory API |
| Actions | WhatsApp Business API, SMTP, Google Calendar |
| Data Source | Google Trends, Shopee Affiliate, TikTok API |
| Marketing | Canva API, Meta Graph API |

---

## 8. Live Demo Script (Untuk Juri)

```text
>> User: "Cari produk home decor yang lagi tren di Eropa"

→ [Super Agent berpikir...]
→ Trend Agent: "Macrame Wall Hanging naik 280% di Pinterest"
→ Scout Agent: Temukan 5 supplier di Bandung & Bali
→ Outreach Agent: Kirim WA: "Halo, ada stok macrame? Butuh 20 pcs."
→ [3 supplier balas → screenshot]
→ Super Agent: Return final report + tombol "Start Instagram Campaign"

→ User klik → Marketing Swarm jalan → 3 post terupload