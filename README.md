# Jetson

# 12.11.2019r.
Aktualny schemat ramki ustalony na:
```
[ [[cam1_obj1_frame], [cam1_obj2_frame], ...], [[cam2_obj2_frame], [cam2_obj2_frame], ...]]
```
Gdzie cam*i*_obj*j*_frame = [distance *(<-prawdopodobnie do wywalenia)*, offset_x, offset_y, detection]

# 4.11.2019r.
Generalny refactoring, uporządkowanie kodu - dodanie klasy Detector do obsługi detekcji darknetem, zmiany w celu obsługi dwóch kamer - output bazowane na detections w formie listy z elementami dla każdej kamery.
Działąjące rozpoznawanie na Jetsonie przy dwóch kamerach i sprawdzone zwracane dane - do przetestowania bezpośrednio w komunikacji z Odroidem.

# 30.10.2019r.

Migracja plików do nowego repozytorium.
Wersja działająca z zacinaniem się przy przesyłaniu danych Jetson->Odro
