# cc-manager — Credit Card Perk Tracker

## Files
- `tracker.html` — main perk matrix (open in browser, data in localStorage)
- `cc` / `cc_manager.py` — CLI tool for card/fee management

## Cards tracked (13)
- Jin Bao: IHG Premier, United Explorer, World of Hyatt, Marriott Boundless, Hilton Aspire
- Xiaoguang Dai: United Explorer, Amex Platinum, Alaska Atmos Summit, World of Hyatt, Chase Sapphire Preferred, Delta Amex Gold

## Categories
1. Annual Fees — 10 cards, renewal dates
2. Hotel Free Nights — annual + bonus nights (counter type for bonuses)
3. Free Night on Award Stays — reminders only
4. Airline Credits — IHG TravelBank, Amex $200 (dollar_airline), Marriott $50 ($250 spend req'd), Hilton $50/qtr (TravelBank works)
5. Alaska Companion Awards — 25k annual + 100k after $60k spend
6. Hotel Credits — FHR/THC, resort, WA/Conrad, United Hotels, CSP $50
7. Dining Credits — Amex $400 Resy
8. Lounge Access — United Club, Alaska passes, Centurion, Priority Pass, Delta Sky Club, Escape/Plaza Premium/Lufthansa*
9. Rideshare/Transit — $5/mo rideshare, $200 Uber Cash, DashPass (Enrollment Required column)
10. Shopping/Wellness — Instacart, $300 digital entertainment, $50 Saks (ends Jun 30), $75/qtr Lululemon, $200 Oura Ring, $300 Equinox+
11. Global Entry/TSA/NEXUS/CLEAR+ — for all cards + CLEAR
12. Travel Reminders — bag, boarding, status reminders

## Type system
- `expiry` — checkbox + date picker
- `counter` — +/- buttons + progress bar (bonus nights)
- `dollar` — number input + progress bar
- `dollar_airline` — dollar + airline text field
- `reminder` — badge only

## Key rules
- Date fields: month+day only (e.g. "Jan 15"), no year
- Hotel Credits: "Renewal" dropdown (annual/semi-annual/quarterly)
- Rideshare/Transit: "Enrollment Required" column instead of Expiration/Status
- Lounge/Dining/GlobalEntry/TravelReminders/FNAS: no Expiration or Status columns
- Lufthansa lounge access ends Sep 30, 2026
- Saks credit ends Jun 30, 2026

## Next steps from last session
- None pending — all known perks added and validated

## How to continue
Run `opencode` and say "continue cc-manager" or reference this file.
