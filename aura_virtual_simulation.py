#!/usr/bin/env python3
"""
AURA 4-Quadrant Airbag Fall Detection Simulation (pygame)
---------------------------------------------------------
Simulasi perbandingan 4-layar:
1.  Layar 1: Jatuh tanpa airbag (Hasil: Cedera)
2.  Layar 2: Duduk normal (Sistem deteksi: Aman)
3.  Layar 3: Jatuh dengan airbag (Airbag mengembang, Hasil: Aman + Notifikasi)
4.  Layar 4: Dashboard Sistem (Status Baterai, Waktu, Ringkasan Hasil)

By: Samuel & Gemini (2025)
"""

import pygame
import sys
import math
import numpy as np

# --- Konfigurasi dasar ---
pygame.init()
SCREEN_W, SCREEN_H = 1200, 700
PANEL_W = SCREEN_W // 4
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("AURA - 4-Quadrant Airbag Simulation")

# --- Koordinat Tengah Panel ---
# Ini adalah koordinat X untuk tengah dari setiap 4 panel
CX_1 = PANEL_W // 2
CX_2 = (PANEL_W // 2) + PANEL_W
CX_3 = (PANEL_W // 2) + (PANEL_W * 2)
CX_4 = (PANEL_W // 2) + (PANEL_W * 3)
# Posisi Y figur (agar seragam)
FIG_Y = 450

FPS = 30
clock = pygame.time.Clock()
font_title = pygame.font.SysFont("Arial", 30, bold=True)
font_panel_title = pygame.font.SysFont("Arial", 20, bold=True)
font_info = pygame.font.SysFont("Consolas", 18)
font_small = pygame.font.SysFont("Consolas", 16)
font_result = pygame.font.SysFont("Arial", 22, bold=True)

# --- Fungsi bantu ---

def draw_text(text, font, color, surface, x, y, center=True):
    """Fungsi helper untuk menggambar teks terpusat."""
    textobj = font.render(text, True, color)
    if center:
        textrect = textobj.get_rect(center=(x, y))
    else:
        textrect = textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_stick_figure(surface, cx, cy, angle_deg, color=(0, 0, 0), sitting=False):
    """
    Gambar figur stickman dengan tangan & kaki dan rotasi.
    (Sama seperti kode asli Anda, hanya sedikit penyesuaian ukuran)
    """
    body_len = 120
    limb_len = 50
    body_w = 6
    head_r = 14

    # Buat surface terpisah untuk figur agar bisa dirotasi
    fig_surf = pygame.Surface((220, 220), pygame.SRCALPHA)
    center_x, center_y = 110, 110 # Titik tengah surface baru

    # Body
    pygame.draw.line(fig_surf, color, (center_x, center_y - 35), (center_x, center_y + 55), body_w)
    # Head
    pygame.draw.circle(fig_surf, color, (center_x, center_y - 55), head_r)
    # Arms
    pygame.draw.line(fig_surf, color, (center_x, center_y - 15), (center_x - limb_len, center_y + 15), body_w)
    pygame.draw.line(fig_surf, color, (center_x, center_y - 15), (center_x + limb_len, center_y + 15), body_w)
    
    # Legs
    if sitting:
        # Kaki membentuk sudut duduk
        # Kaki paha
        pygame.draw.line(fig_surf, color, (center_x, center_y + 55), (center_x - 35, center_y + 85), body_w)
        pygame.draw.line(fig_surf, color, (center_x, center_y + 55), (center_x + 35, center_y + 85), body_w)
        # Kaki betis (tegak lurus)
        pygame.draw.line(fig_surf, color, (center_x - 35, center_y + 85), (center_x - 35, center_y + 115), body_w)
        pygame.draw.line(fig_surf, color, (center_x + 35, center_y + 85), (center_x + 35, center_y + 115), body_w)
    else:
        # Kaki berdiri/jatuh
        pygame.draw.line(fig_surf, color, (center_x, center_y + 55), (center_x - 20, center_y + 105), body_w)
        pygame.draw.line(fig_surf, color, (center_x, center_y + 55), (center_x + 20, center_y + 105), body_w)

    # Rotasi tubuh
    rotated = pygame.transform.rotate(fig_surf, -angle_deg)
    rect = rotated.get_rect(center=(cx, cy))
    surface.blit(rotated, rect.topleft)

def draw_airbag(surface, cx, cy, angle_deg, deploy_progress):
    """
    Gambar airbag yang mengembang dan berotasi bersama figur.
    deploy_progress adalah float 0.0 (belum) hingga 1.0 (penuh).
    """
    if deploy_progress <= 0:
        return
    
    max_radius = 70
    current_radius = int(max_radius * deploy_progress)
    
    # Buat surface terpisah untuk airbag agar bisa dirotasi
    airbag_surf = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
    airbag_color = (173, 216, 230, 180) # Light blue, semi-transparan
    
    pygame.draw.circle(airbag_surf, airbag_color, (max_radius, max_radius), current_radius)
    
    # Rotasi airbag
    rotated = pygame.transform.rotate(airbag_surf, -angle_deg)
    rect = rotated.get_rect(center=(cx, cy - 20)) # Sedikit ke atas (di badan)
    surface.blit(rotated, rect.topleft)

def draw_phone(surface, x, y, vibrate_offset, is_active):
    """Gambar ikon ponsel bergetar."""
    offset = vibrate_offset if is_active else 0
    body_color = (30, 30, 30)
    screen_color = (230, 230, 230) if is_active else (200, 200, 200)
    pygame.draw.rect(surface, body_color, (x + offset, y, 60, 120), border_radius=10)
    pygame.draw.rect(surface, screen_color, (x + 6 + offset, y + 8, 48, 85), border_radius=6)
    pygame.draw.circle(surface, (180, 180, 180), (x + 30 + offset, y + 105), 4)
    if is_active:
        # efek getaran
        pygame.draw.line(surface, (255, 0, 0), (x - 8, y + 30), (x - 20, y + 25), 2)
        pygame.draw.line(surface, (255, 0, 0), (x + 68, y + 30), (x + 80, y + 25), 2)

def create_alarm(freq=800, duration=0.25):
    """Buat suara alarm."""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = (np.sin(freq * t * 2 * math.pi) * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(tone)

try:
    pygame.mixer.init()
    alarm_sound = create_alarm()
except:
    alarm_sound = None

# --- Variabel simulasi (Independen untuk setiap panel) ---
start_time = pygame.time.get_ticks()

# Skenario 1: Jatuh (Tanpa Airbag)
angle_fall_1 = 0
falling_1 = True
detected_1 = False
status_1_text = "STATUS: Berdiri Normal"
color_1 = (0, 0, 0)

# Skenario 2: Duduk (Normal)
angle_sit_2 = 0
sitting_2 = True # Ini mengontrol animasi duduk
detected_2 = False # Ini akan jadi 'True' saat duduk selesai
status_2_text = "STATUS: Berdiri Normal"
color_2 = (0, 180, 0)

# Skenario 3: Jatuh (Dengan Airbag)
angle_fall_3 = 0
falling_3 = True
detected_3 = False
airbag_deploy_progress_3 = 0.0 # 0.0 to 1.0
status_3_text = "STATUS: Berdiri Normal"
color_3 = (0, 0, 200) # Warna biru untuk pembeda

# Variabel Dashboard (Panel 4)
gps_data = {"lat": -6.2088, "lon": 106.8456}
battery_level = 100.0
vibrate_phase = 0
frame = 0

# --- Loop utama ---
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            running = False

    # --- Update Logika Simulasi ---

    # 1. Logika Skenario 1 (Jatuh Tanpa Airbag)
    if falling_1:
        if angle_fall_1 < 90:
            angle_fall_1 += 1.3
            status_1_text = "STATUS: Terjatuh..."
        else:
            angle_fall_1 = 90
            falling_1 = False
            detected_1 = True
            status_1_text = "HASIL: CEDERA SERIUS"
            color_1 = (200, 0, 0) # Merah

    # 2. Logika Skenario 2 (Duduk Normal)
    if sitting_2:
        # Simulasi duduk (berhenti di 45 derajat)
        if angle_sit_2 < 45:
            angle_sit_2 += 1.0
            status_2_text = "STATUS: Sedang Duduk..."
        else:
            angle_sit_2 = 45
            sitting_2 = False
            detected_2 = True # Deteksi selesai (tapi aman)
            status_2_text = "HASIL: AMAN (Duduk Normal)"
            color_2 = (0, 180, 0) # Hijau

    # 3. Logika Skenario 3 (Jatuh Dengan Airbag)
    if falling_3:
        if angle_fall_3 < 90:
            angle_fall_3 += 1.3
            status_3_text = "STATUS: Terjatuh..."
            
            # --- LOGIKA AIRBAG ---
            # Sesuai permintaan: airbag mengembang mulai dari 30 derajat
            if angle_fall_3 >= 30 and airbag_deploy_progress_3 < 1.0:
                airbag_deploy_progress_3 += 0.1 # Kecepatan mengembang
                airbag_deploy_progress_3 = min(1.0, airbag_deploy_progress_3)
                status_3_text = "STATUS: AIRBAG MENGEMBANG!"
                
        else:
            angle_fall_3 = 90
            falling_3 = False
            detected_3 = True # Memicu notifikasi darurat
            status_3_text = "HASIL: AMAN (Terlindungi)"
            color_3 = (0, 0, 200) # Biru
            if alarm_sound:
                alarm_sound.play() # Mainkan alarm hanya untuk skenario 3

    # 4. Logika Dashboard
    live_time_seconds = (pygame.time.get_ticks() - start_time) / 1000
    # Baterai berkurang sangat lambat
    battery_level = max(0.0, 100.0 - live_time_seconds * 0.01)
    if detected_3:
        vibrate_phase += 1


    # --- Gambar Tampilan ---
    
    # Latar belakang (berubah jika skenario 3 terdeteksi)
    bg_color = (255, 230, 230) if detected_3 else (240, 240, 255)
    screen.fill(bg_color)

    # --- Gambar Garis Pemisah Panel ---
    divider_color = (150, 150, 150)
    pygame.draw.line(screen, divider_color, (PANEL_W, 0), (PANEL_W, SCREEN_H), 3)
    pygame.draw.line(screen, divider_color, (PANEL_W * 2, 0), (PANEL_W * 2, SCREEN_H), 3)
    pygame.draw.line(screen, divider_color, (PANEL_W * 3, 0), (PANEL_W * 3, SCREEN_H), 3)

    # --- Judul Panel ---
    draw_text("SKENARIO 1: TANPA AIRBAG", font_panel_title, (0, 0, 0), screen, CX_1, 30)
    draw_text("SKENARIO 2: DUDUK (NORMAL)", font_panel_title, (0, 0, 0), screen, CX_2, 30)
    draw_text("SKENARIO 3: JATUH (AIRBAG)", font_panel_title, (0, 0, 0), screen, CX_3, 30)
    draw_text("SISTEM MONITOR AURA", font_panel_title, (0, 0, 0), screen, CX_4, 30)


    # --- Panel 1: Jatuh Tanpa Airbag ---
    draw_text(status_1_text, font_result, color_1, screen, CX_1, 80)
    draw_stick_figure(screen, CX_1, FIG_Y, angle_fall_1, color=color_1)

    # --- Panel 2: Duduk Normal ---
    draw_text(status_2_text, font_result, color_2, screen, CX_2, 80)
    # Parameter sitting=True membuat kaki menekuk
    draw_stick_figure(screen, CX_2, FIG_Y + 10, angle_sit_2, color=color_2, sitting=True)

    # --- Panel 3: Jatuh Dengan Airbag ---
    draw_text(status_3_text, font_result, color_3, screen, CX_3, 80)
    # Gambar airbag DULU (di belakang)
    draw_airbag(screen, CX_3, FIG_Y - 20, angle_fall_3, airbag_deploy_progress_3)
    # Gambar figur (di depan)
    draw_stick_figure(screen, CX_3, FIG_Y, angle_fall_3, color=color_3)

    # --- Panel 4: Dashboard Sistem ---
    # Info Baterai & Waktu
    bat_color = (0, 150, 0) if battery_level > 20 else (200, 0, 0)
    draw_text(f"BATERAI: {battery_level:.1f}%", font_info, bat_color, screen, CX_4, 80)
    draw_text(f"WAKTU AKTIF: {live_time_seconds:.1f} s", font_info, (0, 0, 0), screen, CX_4, 110)
    
    # Garis pemisah dashboard
    pygame.draw.line(screen, divider_color, (PANEL_W * 3 + 20, 140), (SCREEN_W - 20, 140), 1)

    # Ringkasan Hasil Skenario
    draw_text("RINGKASAN HASIL:", font_info, (0, 0, 0), screen, CX_4, 170)
    draw_text("Skenario 1 (Jatuh):", font_small, (0, 0, 0), screen, CX_4 - 120, 210, center=False)
    draw_text("CEDERA" if detected_1 else "OK", font_small, color_1, screen, CX_4 + 70, 210, center=False)
    
    draw_text("Skenario 2 (Duduk):", font_small, (0, 0, 0), screen, CX_4 - 120, 240, center=False)
    draw_text("AMAN" if detected_2 else "OK", font_small, color_2, screen, CX_4 + 70, 240, center=False)

    draw_text("Skenario 3 (Jatuh):", font_small, (0, 0, 0), screen, CX_4 - 120, 270, center=False)
    draw_text("AMAN" if detected_3 else "OK", font_small, color_3, screen, CX_4 + 70, 270, center=False)

    # Panel Notifikasi Darurat (HANYA jika skenario 3 terdeteksi)
    if detected_3:
        # Kotak notifikasi
        box_x = PANEL_W * 3 + 15
        box_y = 310
        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, PANEL_W - 30, 370), border_radius=10)
        pygame.draw.rect(screen, (220, 0, 0), (box_x, box_y, PANEL_W - 30, 370), 3, border_radius=10)
        
        draw_text("📡 ALERT DARURAT (SK 3) 📡", font_info, (220, 0, 0), screen, CX_4, box_y + 30)
        draw_text(f"Lat: {gps_data['lat']:.4f}", font_small, (0, 0, 0), screen, CX_4 - 110, box_y + 70, center=False)
        draw_text(f"Lon: {gps_data['lon']:.4f}", font_small, (0, 0, 0), screen, CX_4 - 110, box_y + 95, center=False)
        draw_text("Kontak: +62 812-3456-7890", font_small, (0, 100, 0), screen, CX_4 - 110, box_y + 130, center=False)
        draw_text("Status: Terkirim ✅", font_small, (0, 100, 0), screen, CX_4 - 110, box_y + 155, center=False)

        # Animasi ponsel bergetar
        vibrate_offset = 3 * math.sin(vibrate_phase * 0.5)
        draw_phone(screen, CX_4 - 30, box_y + 190, vibrate_offset, True)
        draw_text("Kontak Darurat", font_small, (100, 0, 0), screen, CX_4, box_y + 330)

    # --- Update Tampilan ---
    pygame.display.flip()
    clock.tick(FPS)
    frame += 1

# --- Keluar ---
pygame.quit()
sys.exit()