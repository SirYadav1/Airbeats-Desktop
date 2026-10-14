# 🚀 Airbeats Desktop v6.4.0 — The Ultimate Horizon Update

We are thrilled to present **Airbeats Desktop v6.4.0**! This massive milestone brings our desktop music experience to absolute parity with the beloved AirBeats Android ecosystem. From the ambient OLED **Always On Display**, a powerhouse **11-provider Lyrics Engine with Multi-LLM AI Translation**, to a completely reimagined **Home & Explore Experience**, **Stats & Insights Tiers**, and **offline visual rock-solid stability** — this is the most refined and complete version of Airbeats Desktop ever built.

---

## 🌟 Major Highlights

### 🌙 Always On Display (AOD) & Mini-Player Bottom Sheet
- **Full-Screen Ambient OLED Player**: Experience music in a distraction-free, battery-friendly ambient mode. Choose between multiple clock faces (Classic, Minimal, Digital, OLED Glow, Vinyl Spin) with smooth glowing scrubbers.
- **Keyboard & Touch Ergonomics**: Instantly enter or dismiss AOD with keyboard shortcut (`Esc`), smooth animations, and zero clutter.
- **Mini-Player 3-Dot Bottom Sheet**: Quick-access popup on the persistent player bar with instant shortcuts:
  - Launch Always On Display
  - Download Track locally (`.m4a`)
  - Listen Together synchronized session
  - Add to Custom Playlist
  - Toggle High-Definition Lyrics
  - Smooth interactive Volume Slider with custom popup controls

---

### 🎤 Supercharged Lyrics Engine & AI Translation
- **11 Integrated Lyrics Providers**: Seamlessly cycle between the world's top lyrics backends matching the Android app:
  * LRCLIB, Musixmatch, Genius, Spotify, NetEase, KuGou, QQ Music, Deezer, AZLyrics, SimpMusic, and Custom Provider.
- **Multi-LLM AI Translation**: Real-time lyrics translation powered by your choice of 11 AI providers:
  * OpenRouter, DeepSeek, Groq, Mistral, OpenAI, Anthropic, Gemini, Nvidia NIM, OrcaRouter, Puter, and Custom OpenAI-compatible endpoints.
- **52 Languages Supported**: Translate synchronized lyrics line-by-line into 52 world languages with instant search filtering.
- **Enhanced 3-Dot Lyrics Controls**: In-lyrics floating control sheet with provider switching, time synchronization offset adjustments, and typography scaling.

---

### 📊 Rebuilt Stats & AirBeats Insight
- **18 Dynamic Rank Tiers**: Track your musical journey from Bronze to Celestial and Godlike tiers based on your actual listening milestones.
- **Deep Listening Analytics**: Visual listening clock, top artists, top albums, favorite tracks, and genre breakdowns.
- **High-Res Visual Polish**: Eliminated blurry artwork and placeholder avatars — stats cards now feature crisp CDN album art with smooth hover-zoom and ambient glow effects matching the Home screen.
- **Profile Customization**: Personalize your display name, bio, avatar, and rank badges with full local persistence.

---

### 🏠 Classic Android-Inspired Home & Explore Screen
- **Full-Width Liquid Layout**: Removed restrictive side gutters for a spacious, modern edge-to-edge canvas.
- **Intelligent Home Shelves**: Browse personalized shelves including:
  * **Quick Picks** with one-tap Instant Radio
  * **Forgotten Favorites** rediscovery shelf
  * **Albums For You** & **Artists For You** with high-resolution portraits
- **Quick-Filter Chips Bar**: Effortlessly jump between Recently Played, Favorite Songs, Playlists, Cached Tracks, New Releases, and instant Shuffle Play.
- **Brand New Explore Tab**: Discover trending global charts, curated mood playlists (Chill, Workout, Focus, Party, Romance), and fresh weekly releases.
- **Smart Now-Playing Panel**: Right-hand queue sidebar auto-collapses when idle to give your browsing maximum screen space, expanding dynamically during playback.

---

### 📰 News from Developers
- Stay in the loop with live community broadcasts, major changelogs, feature previews, and urgent announcements fetched directly via Firebase Realtime Database.
- Includes priority announcements, pinned developer alerts, search, and direct action links.

---

### 🔒 Privacy-First Android `.backup` Restore
- **Zero Account Bloat**: Removed invasive external account sign-ins and unwanted cloud telemetry for a 100% private, locally stored music library.
- **Direct Android Migration**: Seamlessly import your `.backup` file generated from AirBeats Android directly in **Settings > Backup & Restore** to restore your favorites, custom playlists, and play history instantly.

---

### 🎨 Settings Navigation & Offline UI Perfection
- **Refined Settings Sidebar**: Re-architected sidebar navigation submenu with dedicated, aligned FontAwesome icons:
  * 🗄️ **Backup & Restore** (`fa-database`)
  * 🎨 **Appearance** (`fa-palette`)
  * 🌙 **Always On Display** (`fa-moon`)
  * 📰 **News from Developers** (`fa-newspaper`)
  * ℹ️ **About** (`fa-info-circle`)
  * 🔄 **Updates** (`fa-sync-alt`)
- **Offline FontAwesome 6 Bundle**: All icon webfonts are now packaged locally directly inside `static/webfonts/`, ensuring 0ms latency and 100% reliability offline without missing glyph boxes or CDN blocking.
- **No More Accidental Text Carets**: Fixed irritating blinking text cursors and accidental text selection when clicking buttons, chips, and color swatches.
- **Button Actions Everywhere**: Restored `+` (Add to Playlist) and `...` (3-Dots Context Menu) across all shelves, search results, and tracklists.
- **Fixed Heart Toggle**: Eliminated duplicate heart element duplication when favoriting tracks.

---

## 🛠️ Complete Technical Changelog

* **Engine & Backend**:
  - Implemented `@app.after_request` with `Cache-Control: no-cache, no-store, must-revalidate` for instant template hot-reloads.
  - Sanitized stats event logging preventing `UnboundLocalError: stats_events`.
  - Added safe string normalization to protect against `alb.title.replace` exceptions.
  - Resolved lingering zombie server processes on port `8000`.

* **Desktop & Linux Packaging**:
  - Configured Electron build with `useTemplateApp: false` in Snapcraft configuration to eliminate deprecated `desktop-init.sh` startup crash on modern Ubuntu distros.
  - Updated electron package specification to version `6.4.0`.

* **Frontend & Styling**:
  - Protected all FontAwesome `::before` pseudo-elements against global `font-family` font-matching collisions.
  - Enhanced responsive breakpoints for compact desktop and tablet viewports.

---

**Download Airbeats Desktop v6.4.0 today and elevate your desktop music streaming experience!** 🎧
