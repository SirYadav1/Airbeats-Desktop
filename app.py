import requests
from flask import Flask, render_template, Response, request, jsonify
import xml.etree.ElementTree as ET
import re
import math
import random
import uuid
import os
import sys
import time
import zipfile
import sqlite3
import tempfile

# Load .env if it exists (for local development and GitHub Actions secrets)
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip()


if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')


@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Allow: /
Sitemap: https://airbeats.xyz/sitemap.xml
''', 200, {'Content-Type': 'text/plain'}

@app.route('/sitemap.xml')
def sitemap():
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://airbeats.xyz/</loc>
    <lastmod>2026-06-30</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
    return xml, 200, {'Content-Type': 'application/xml'}


# Simple cache to avoid re-fetching the same mp4 url multiple times
stream_cache = {}


@app.route('/api/shuffle', methods=['POST'])
def shuffle_queue():
    try:
        data = request.json
        tracks = data.get('tracks', [])
        if tracks:
            random.shuffle(tracks)
        return jsonify({'success': True, 'shuffled': tracks})
    except Exception as e:
        print('Shuffle Error:', e)
        return jsonify({'success': False, 'shuffled': []}), 500


# ==================== ANDROID .BACKUP RESTORE SYSTEM ====================

@app.route('/api/restore_backup', methods=['POST'])
@app.route('/api/stats/restore_backup', methods=['POST'])
def restore_backup():
    """Restores Android AirBeats .backup or .zip file containing music.db and airbeats_global_stats.xml"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty file"}), 400
            
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'backup.zip')
            file.save(zip_path)
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(temp_dir)
            except zipfile.BadZipFile:
                return jsonify({"error": "Invalid backup file format. Must be a valid .backup or .zip file."}), 400
                
            history = []
            favorites = []
            playlists = []
            
            db_path = os.path.join(temp_dir, 'music.db')
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # 1. Query History from event joined with song & artist
                    try:
                        query = """
                        SELECT 
                            s.id, 
                            s.title, 
                            s.duration,
                            a.id as artistId,
                            a.name as artistName,
                            e.timestamp
                        FROM event e
                        JOIN song s ON e.songId = s.id
                        LEFT JOIN song_artist_map sam ON s.id = sam.songId AND sam.position = 0
                        LEFT JOIN artist a ON sam.artistId = a.id
                        ORDER BY e.timestamp DESC
                        LIMIT 200
                        """
                        cursor.execute(query)
                        for row in cursor.fetchall():
                            song_id, title, duration, artist_id, artist_name, timestamp = row
                            history.append({
                                "id": song_id,
                                "name": title,
                                "title": title,
                                "artist": artist_name or "Unknown Artist",
                                "subtitle": artist_name or "Unknown Artist",
                                "type": "song",
                                "image": "https://ui-avatars.com/api/?name=Song&background=333&color=fff",
                                "artistIds": artist_id or "",
                                "playedAt": timestamp
                            })
                    except Exception as e_hist:
                        print(f"[BACKUP] History parse notice: {e_hist}")

                    # 2. Query Favorites
                    try:
                        cursor.execute("PRAGMA table_info(song);")
                        cols = [c[1] for c in cursor.fetchall()]
                        fav_where = None
                        if 'inLibrary' in cols:
                            fav_where = "s.inLibrary = 1"
                        elif 'favorite' in cols:
                            fav_where = "s.favorite = 1"
                        
                        if fav_where:
                            cursor.execute(f"""
                                SELECT s.id, s.title, s.duration, a.name
                                FROM song s
                                LEFT JOIN song_artist_map sam ON s.id = sam.songId AND sam.position = 0
                                LEFT JOIN artist a ON sam.artistId = a.id
                                WHERE {fav_where}
                                ORDER BY s.id DESC
                            """)
                            for f_row in cursor.fetchall():
                                favorites.append({
                                    "id": f_row[0],
                                    "name": f_row[1],
                                    "title": f_row[1],
                                    "artist": f_row[3] or "Unknown Artist",
                                    "duration": f_row[2] or 0
                                })
                    except Exception as e_fav:
                        print(f"[BACKUP] Favorites parse notice: {e_fav}")

                    # 3. Query Playlists
                    try:
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='playlist';")
                        if cursor.fetchone():
                            cursor.execute("SELECT id, title FROM playlist;")
                            p_rows = cursor.fetchall()
                            
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='playlist_song_map';")
                            has_psm = bool(cursor.fetchone())
                            
                            for pid, ptitle in p_rows:
                                songs = []
                                if has_psm:
                                    cursor.execute("""
                                        SELECT s.id, s.title, s.duration, a.name
                                        FROM playlist_song_map psm
                                        JOIN song s ON psm.songId = s.id
                                        LEFT JOIN song_artist_map sam ON s.id = sam.songId AND sam.position = 0
                                        LEFT JOIN artist a ON sam.artistId = a.id
                                        WHERE psm.playlistId = ?
                                        ORDER BY psm.position ASC
                                    """, (pid,))
                                    for s_row in cursor.fetchall():
                                        songs.append({
                                            "id": s_row[0],
                                            "name": s_row[1],
                                            "title": s_row[1],
                                            "artist": s_row[3] or "Unknown Artist",
                                            "duration": s_row[2] or 0
                                        })
                                playlists.append({
                                    "id": f"pl_{pid}",
                                    "name": ptitle,
                                    "title": ptitle,
                                    "songs": songs
                                })
                    except Exception as e_pl:
                        print(f"[BACKUP] Playlists parse notice: {e_pl}")

                    # 4. Query Listening Events for Stats Engine
                    stats_events = []
                    try:
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event';")
                        if cursor.fetchone():
                            cursor.execute("PRAGMA table_info(event);")
                            e_cols = [c[1] for c in cursor.fetchall()]
                            cursor.execute("PRAGMA table_info(song);")
                            s_cols = [c[1] for c in cursor.fetchall()]

                            has_play_time = 'playTime' in e_cols
                            has_thumb = 'thumbnailUrl' in s_cols
                            has_album_id = 'albumId' in s_cols
                            has_album_name = 'albumName' in s_cols

                            play_time_expr = "e.playTime" if has_play_time else "COALESCE(s.duration * 1000, 180000)"
                            thumb_expr = "s.thumbnailUrl" if has_thumb else "NULL"
                            album_id_expr = "s.albumId" if has_album_id else "NULL"
                            album_name_expr = "s.albumName" if has_album_name else "NULL"

                            events_query = f"""
                            SELECT 
                                e.songId,
                                s.title,
                                s.duration,
                                {thumb_expr} as thumbnailUrl,
                                {album_id_expr} as albumId,
                                {album_name_expr} as albumName,
                                a.id as artistId,
                                a.name as artistName,
                                e.timestamp,
                                {play_time_expr} as playTime
                            FROM event e
                            JOIN song s ON e.songId = s.id
                            LEFT JOIN song_artist_map sam ON s.id = sam.songId AND sam.position = 0
                            LEFT JOIN artist a ON sam.artistId = a.id
                            ORDER BY e.timestamp DESC
                            """
                            cursor.execute(events_query)
                            for ev_row in cursor.fetchall():
                                song_id, title, duration, thumb, alb_id, alb_name, art_id, art_name, t_stamp, p_time = ev_row
                                stats_events.append({
                                    "songId": song_id,
                                    "title": title or "Unknown Track",
                                    "artist": art_name or "Unknown Artist",
                                    "artistId": art_id or "",
                                    "album": alb_name or "",
                                    "albumId": alb_id or "",
                                    "image": thumb or "https://ui-avatars.com/api/?name=Song&background=333&color=fff",
                                    "duration": duration or 0,
                                    "timeListenedMs": int(p_time if p_time is not None else (duration * 1000 if duration else 180000)),
                                    "timestamp": t_stamp
                                })
                    except Exception as e_ev:
                        print(f"[BACKUP] Stats events parse notice: {e_ev}")
                        
                    conn.close()
                except Exception as e_db:
                    print(f"[BACKUP] SQLite connection error: {e_db}")

            return jsonify({
                "success": True,
                "history": history,
                "favoriteSongs": favorites,
                "playlists": playlists,
                "statsEvents": stats_events
            })
    except Exception as e:
        print("[BACKUP] Restore exception:", e)
        return jsonify({"error": str(e)}), 500


# ==================== LYRICS SYSTEM ====================

def parse_time_ms(time_str):
    if not time_str:
        return 0
    if ':' not in time_str:
        return int(float(time_str) * 1000)
    parts = time_str.split(':')
    seconds = 0
    if len(parts) == 3:
        seconds = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        seconds = float(parts[0]) * 60 + float(parts[1])
    return int(seconds * 1000)

def parse_ttml(xml_string):
    try:
        root = ET.fromstring(xml_string)
        # Handle namespaces if any
        ns = {'tt': 'http://www.w3.org/ns/ttml'}
        body = root.find('.//body') or root.find('.//{http://www.w3.org/ns/ttml}body')
        if body is None: body = root
        
        parsed_lines = []
        p_tags = root.findall('.//p') or root.findall('.//{http://www.w3.org/ns/ttml}p')
        
        for p in p_tags:
            line_begin = parse_time_ms(p.get('begin'))
            line_end = parse_time_ms(p.get('end'))
            
            words = []
            spans = p.findall('.//span') or p.findall('.//{http://www.w3.org/ns/ttml}span')
            
            for span in spans:
                words.append({
                    'text': span.text or '',
                    'begin': parse_time_ms(span.get('begin')),
                    'end': parse_time_ms(span.get('end'))
                })
                
            if not words:
                text = ''.join(p.itertext()).strip()
                parts = [part for part in text.split(' ') if part]
                total_chars = len(''.join(parts)) or 1
                current_begin = line_begin
                
                for i, part in enumerate(parts):
                    char_ratio = len(part) / total_chars
                    duration = (line_end - line_begin) * char_ratio
                    words.append({
                        'text': part,
                        'begin': int(current_begin),
                        'end': int(current_begin + duration)
                    })
                    current_begin += duration
                    
            parsed_lines.append({
                'begin': line_begin,
                'end': line_end,
                'words': words,
                'rawText': ''.join(p.itertext()).strip()
            })
            
        return parsed_lines
    except Exception as e:
        print("TTML Parse Error:", e)
        return []

def parse_lrc(lrc_string):
    lines = lrc_string.split('\n')
    parsed_lines = []
    time_regex = re.compile(r'\[(\d{2}):(\d{2}\.\d{2,3})\]')
    
    for line in lines:
        match = time_regex.search(line)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            begin_ms = int((minutes * 60 + seconds) * 1000)
            text = time_regex.sub('', line).strip()
            parsed_lines.append({
                'begin': begin_ms,
                'end': 0,
                'words': [],
                'rawText': text
            })
            
    for i in range(len(parsed_lines)):
        current_line = parsed_lines[i]
        end_ms = current_line['begin'] + 5000
        if i < len(parsed_lines) - 1:
            end_ms = parsed_lines[i+1]['begin']
        current_line['end'] = end_ms
        
        parts = [p for p in current_line['rawText'].split(' ') if p]
        if not parts:
            current_line['words'] = [{'text': '', 'begin': current_line['begin'], 'end': current_line['end']}]
        else:
            time_per_word = int((current_line['end'] - current_line['begin']) / len(parts))
            current_word_begin = current_line['begin']
            for p in parts:
                current_line['words'].append({
                    'text': p,
                    'begin': current_word_begin,
                    'end': current_word_begin + time_per_word
                })
                current_word_begin += time_per_word
                
    return parsed_lines

def get_lyrics():
    song_name = request.args.get('s', '')
    artist_name = request.args.get('a', '')
    duration = request.args.get('d', '')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }
    
    artist_queries = [artist_name]
    if ',' in artist_name:
        individual = [a.strip() for a in artist_name.split(',') if a.strip()]
        for a in individual:
            if a != artist_name:
                artist_queries.append(a)
    
    force_refresh = request.args.get('force') == '1'
    
    for artist_q in artist_queries:
        if not force_refresh:
            # 1. Try Boidu API
            try:
                url = f"https://lyrics-api.boidu.dev/getLyrics?s={requests.utils.quote(song_name)}&a={requests.utils.quote(artist_q)}"
                if duration: url += f"&d={duration}"
                res = requests.get(url, headers=headers, timeout=10)
                if res.ok:
                    data = res.json()
                    ttml = data.get('ttml')
                    if ttml:
                        parsed = parse_ttml(ttml)
                        if parsed:
                            return jsonify(parsed)
            except Exception as e:
                print("Boidu API Error:", e)
                
            # 2. Try Boidu Kugou API
            try:
                url = f"https://lyrics-api.boidu.dev/kugou/getLyrics?s={requests.utils.quote(song_name)}&a={requests.utils.quote(artist_q)}"
                if duration: url += f"&d={duration}"
                res = requests.get(url, headers=headers, timeout=10)
                if res.ok:
                    data = res.json()
                    ttml = data.get('ttml')
                    if ttml:
                        parsed = parse_ttml(ttml)
                        if parsed:
                            return jsonify(parsed)
            except Exception as e:
                print("Boidu Kugou API Error:", e)

        # 3. Try LRCLIB API
        try:
            q = f"{song_name} {artist_q}".strip()
            url = f"https://lrclib.net/api/search?q={requests.utils.quote(q)}"
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.ok:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    for idx, item in enumerate(data):
                        if item.get('syncedLyrics'):
                            parsed = parse_lrc(item['syncedLyrics'])
                            if parsed:
                                return jsonify(parsed)
        except Exception as e:
            print("[LRCLIB] EXCEPTION OCCURRED:", e)

    # 4. Final fallback: try with just the song name, no artist
    try:
        url = f"https://lrclib.net/api/search?q={requests.utils.quote(song_name)}"
        res = requests.get(url, headers=headers, timeout=10)
        if res.ok:
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if item.get('syncedLyrics'):
                        parsed = parse_lrc(item['syncedLyrics'])
                        if parsed:
                            return jsonify(parsed)
    except Exception as e:
        print("[LRCLIB] Song-only fallback error:", e)

    return jsonify({"error": "No synchronized lyrics found."}), 404

import backend
backend.add_yt_routes(app, get_lyrics)

if __name__ == '__main__':
    print("Server started at http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000, debug=False)
