# Bezpieczna aplikacja internetowa

Projekt zrealizowany na koniec przedmiotu **Ochrona Danych w Systemach Informatycznych**.

## Spis treści

- [Cel projektu](#cel-projektu)
- [Opis projektu](#opis-projektu)
- [Bezpieczeństwo aplikacji](#bezpieczestwo-aplikacji)
- [Uruchomienie aplikacji](#uruchomienie-aplikacji)
- [Rozwój projektu](#rozwj-projektu)

## Cel projektu

Celem projektu było stworzenie bezpiecznej aplikacji internetowej umożliwiającej tworzenie oraz udostępnianie notatek przez użytkowników. Priorytetem podczas tworzenia tej aplikacji ma być bezpieczeństwo danych.

## Opis projektu

Aplikacja napisana jest w języku **Python** z użyciem bibliioteki **Flask**. Wykorzystywana jest również baza danych **Redis**. Całość aplikacji uruchamiana jest za pomocą **Dockera**.

Aplikacja zapewnia:
+ możliwość dodawania użytkowników,
+ możliwość dodawania notatek,
+ możliwość udostępniania notatek innym użytkownikom.

## Bezpieczeństwo aplikacji:

Aplikacji zapewnia wysokie bezpieczeństwo danych. Dane wejściowe są restrykcyjnie walidowane z negatywnym nastawieniem. Przechowywane hasła chronione są funkcja hash oraz solą. Wykorzystywanym algorytmem hashującym jest algorytm **PBKDF2**. Siła hasła sprawdzana jest poprzez liczenie entropii hasła. Transmisja w projekcie zabezpieczona jest za pomocą wykorzystania protokołu **https**.

## Uruchomienie aplikacji:

Aplikację można uruchomić za pomocą **Dockera**.

Przed uruchomieniem należy utworzyć plik **.env** w katalogu głównym repozytorium. W pliku należu zdefiniować zmienną **FLASK_SECRET**.

Projekt można uruchomić używając w katalogu głównym repozytorium polecenia:

```bash
docker-compose up --build
```

## Rozwój projektu

Projekt można rozwinąć poprzez:
+ Zmiana bazy danych na SQL (np. PostgreSQL),
+ Dodanie informacji o logowanich na profil użytkownika.