# 🎵 Chinook Database Guide

## Overview
The **Chinook Database** is a sample dataset representing a **digital media store** (music store). It contains information about:
- 🎼 Music tracks, albums, and artists
- 💿 Media types and genres
- 🛍️ Customer purchases and invoices
- 💰 Sales data and revenue
- 👥 Employees and support tickets

This is a real-world sample database commonly used for learning SQL and database design.

---

## Database Structure

### 📊 Core Tables

#### **1. Artist** 🎤
- Stores information about music artists
- **Key Fields:** `ArtistId`, `Name`
- Sample: "AC/DC", "Aerosmith", "Sting"

#### **2. Album** 💿
- Contains album information
- **Key Fields:** `AlbumId`, `Title`, `ArtistId`
- Links to: Artist
- Sample: "Let There Be Rock" by AC/DC

#### **3. Genre** 🎵
- Music categories
- **Key Fields:** `GenreId`, `Name`
- Sample: "Rock", "Jazz", "Latin", "Metal", "Pop"

#### **4. Track** 🎵
- Individual music tracks/songs
- **Key Fields:** `TrackId`, `Name`, `AlbumId`, `GenreId`, `MediaTypeId`, `Milliseconds`, `UnitPrice`
- **Important:** Has price information (typically $0.99 per track)
- Links to: Album, Genre, MediaType

#### **5. MediaType** 📀
- Types of media
- **Key Fields:** `MediaTypeId`, `Name`
- Sample: "MPEG audio file", "Protected AAC audio file", "Video"

#### **6. Customer** 👥
- Customers who made purchases
- **Key Fields:** `CustomerId`, `FirstName`, `LastName`, `Email`, `Country`, `City`, `State`, `Phone`
- Contains: ~60 customers from various countries

#### **7. Invoice** 🧾
- Customer purchase records
- **Key Fields:** `InvoiceId`, `CustomerId`, `InvoiceDate`, `Total`, `BillingCountry`, `BillingCity`
- Each invoice = one customer transaction

#### **8. InvoiceLine** 📝
- Details of items in each invoice
- **Key Fields:** `InvoiceLineId`, `InvoiceId`, `TrackId`, `UnitPrice`, `Quantity`
- Links: Invoice to Track
- Stores how many of each track was purchased

#### **9. Playlist** 📋
- Collections of tracks
- **Key Fields:** `PlaylistId`, `Name`
- Sample: "Music", "Grunge", "Heavy Metal Classical"

#### **10. PlaylistTrack** 🔗
- Many-to-many relationship between Playlist and Track
- **Key Fields:** `PlaylistId`, `TrackId`

#### **11. Employee** 👔
- Store employees
- **Key Fields:** `EmployeeId`, `FirstName`, `LastName`, `Title`, `ReportsTo`, `HireDate`
- Hierarchy: Employees report to managers

#### **12. Customer_Support** (implicit)
- Tracks customer relationship management
- **Key Fields:** `SupportRepId` (Employee ID), linked to Customer

---

## 🤔 Example Questions You Can Ask

### Sales & Revenue
- "How much revenue did we generate in 2013?"
- "Which countries generate the most revenue?"
- "What is the average order value?"
- "Who is our top customer by spending?"
- "Show total revenue by year"
- "Which customer spent the most in 2012?"

### Music Content
- "Which artist has the most tracks?"
- "How many albums does Metallica have?"
- "List all genres and their track count"
- "Which tracks are the most expensive?"
- "Show albums by AC/DC"

### Customer Behavior
- "How many customers are from USA?"
- "Show customer count by country"
- "Who bought the most tracks?"
- "List customers from Brazil and their total spending"

### Popularity & Analytics
- "Which genre generates the most revenue?"
- "Show average price by genre"
- "List top 5 best-selling tracks"
- "Show playlist with most tracks"
- "Which artist earns the most?"

### Date-based Queries
- "Show sales by month in 2009"
- "List customers who made purchases in December 2013"
- "Show revenue trend over years"

---

## 🔗 Table Relationships

```
┌─────────────┐
│   Artist    │
└──────┬──────┘
       │ (1-to-many)
       │
┌──────▼─────────┐
│     Album      │
└──────┬─────────┘
       │ (1-to-many)
       │
┌──────▼──────────────────┐
│      Track       ◄──────┼─────────┐
└──────┬────┬──────────────┘         │
       │    │                        │
   Genre  MediaType          InvoiceInvoiceLine│
                                     ├─────────┘
┌──────────────────┐                 │
│    Playlist      │◄────────────────┤
└──────────────────┘      many-to-many
     PlaylistTrack

┌──────────────┐
│   Customer   │◄─────────┐
└──────├───────┘          │
       │ (1-to-many)      │
       │                  │
┌──────▼────────┐    ┌────┴─────────┐
│    Invoice    │    │   Employee   │
└──────┬────────┘    └──────────────┘
       │ (1-to-many)
       │
┌──────▼──────────┐
│   InvoiceLine   │
└─────────────────┘
```

---

## 💡 Sample SQL Queries (What LLM Will Generate)

### Total Revenue by Country
```sql
SELECT 
    BillingCountry,
    SUM(Total) as Revenue
FROM Invoice
GROUP BY BillingCountry
ORDER BY Revenue DESC
LIMIT 10;
```

### Top 5 Artists by Revenue
```sql
SELECT 
    ar.Name,
    SUM(il.UnitPrice * il.Quantity) as Revenue
FROM Artist ar
JOIN Album a ON ar.ArtistId = a.ArtistId
JOIN Track t ON a.AlbumId = t.AlbumId
JOIN InvoiceLine il ON t.TrackId = il.TrackId
GROUP BY ar.Name
ORDER BY Revenue DESC
LIMIT 5;
```

### Best Selling Genres
```sql
SELECT 
    g.Name,
    COUNT(il.TrackId) as TracksSold,
    SUM(il.UnitPrice * il.Quantity) as Revenue
FROM Genre g
JOIN Track t ON g.GenreId = t.GenreId
JOIN InvoiceLine il ON t.TrackId = il.TrackId
GROUP BY g.Name
ORDER BY Revenue DESC;
```

---

## ⚡ Quick Tips for Asking Questions

1. **Be Specific:**
   - ❌ "Show data" 
   - ✅ "Show total revenue by month in 2013"

2. **Mention Time Periods:**
   - "In 2012..." 
   - "Over the last year..."
   - "By year..."

3. **Use Comparison Keywords:**
   - "Top 5...", "Most...", "Least...", "Compare..."
   - "By country", "By genre", "By customer"

4. **Ask About Relationships:**
   - "Which artist sold the most?"
   - "Show customers and their purchases"
   - "What genres do customers prefer?"

5. **Aggregate Questions:**
   - "Average...", "Total...", "Count of..."
   - "Revenue by...", "Sales by..."

---

## 📈 Data Statistics

- **~60 Customers** across 24 countries
- **~200 Albums** from various artists
- **~340 Tracks** across multiple genres
- **~230 Invoices** (customer transactions)
- **Time Period:** 2009 - 2013
- **Genres:** 25 different music genres
- **Total Revenue:** ~$2.3M (in dataset period)

---

## 🎯 Common Use Cases

| Question Type | Example |
|---------------|---------|
| **Revenue Analysis** | "What's our total revenue in 2013?" |
| **Customer Insights** | "Who are our top 5 customers?" |
| **Product Performance** | "Which genre is most popular?" |
| **Geographic Analysis** | "Show revenue by country" |
| **Trend Analysis** | "Show monthly revenue trend" |
| **Inventory** | "How many tracks per artist?" |
| **Marketing** | "Customers from which country spent most?" |

---

## 🚀 Try These Starter Questions

1. "How many customers do we have in total?"
2. "Which country has the most customers?"
3. "What is the total revenue?"
4. "Show top 5 genres by revenue"
5. "List the most expensive tracks"
6. "Who spent the most money?"
7. "How many employees do we have?"
8. "Show revenue by year"
9. "Which artist has the most albums?"
10. "Show customer count and revenue by country"

---

## 🔍 Looking for Something Specific?

- **Cost Analysis:** Ask about pricing, discounts, or unit prices
- **Time Series:** Ask about trends, monthly/yearly data
- **Rankings:** Ask for "top", "best", "least", "most"
- **Aggregates:** Ask for "total", "count", "average", "sum"
- **Relationships:** Ask "which", "show", "list" to explore connections

---

**Happy Querying! 🎵**
