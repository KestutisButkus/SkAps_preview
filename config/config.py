# langų dydžių konfiguracija
import ctypes

# main_window_size
width = 1300
height = width / 16 * 9
height_int = int(height)
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)  # 0 - ekrano plotis
screen_height = user32.GetSystemMetrics(1)  # 1 - ekrano aukštis
posx = (screen_width - width) // 2
posy = (screen_height - height_int) // 2
position_x = posx
position_y = posy
main_window_size = position_x, position_y, width, int(height)

main_margins = 0
main_windows_margins = (
main_margins, main_margins, main_margins, main_margins)  # Nustatome paraštes: kairė, viršus, dešinė, apačia

box_margins = 20
box_windows_margins = (box_margins, box_margins, box_margins, box_margins)

box_size = 100
small_size_x = (box_size * 3)
small_size_y = (box_size * 3)
small_windows_size = (
(screen_width - small_size_x) // 2, (screen_height - small_size_y) // 2, small_size_x, small_size_y)

medium_size_x = (box_size * 4)
medium_size_y = (box_size * 7)
medium_windows_size = (
(screen_width - medium_size_x) // 2, (screen_height - medium_size_y) // 2, medium_size_x, medium_size_x)

#  Fono spalva
fonas = ("#fafafa", "#f8f9fa")
