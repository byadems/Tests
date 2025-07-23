from colorama import Fore, Style
from time import sleep
from os import system
from sms import SendSms
import threading

servisler_sms = []
for attribute in dir(SendSms):
    attribute_value = getattr(SendSms, attribute)
    if callable(attribute_value):
        if attribute.startswith('__') == False:
            servisler_sms.append(attribute)

while 1:
    system("cls||clear")
    print("""{}
     ______                         _     
    |  ____|                       | |    
    | |__   _ __   ___  _   _  __ _| |__  
    |  __| | '_ \ / _ \| | | |/ _` | '_ \ 
    | |____| | | | (_) | |_| | (_| | | | |
    |______|_| |_|\___/ \__,_|\__, |_| |_|
                               __/ |      
                              |___/      

    Sms: {}           {}by {}@tingirifistik\n  
    """.format(Fore.LIGHTCYAN_EX, len(servisler_sms), Style.RESET_ALL,
               Fore.LIGHTRED_EX))

    try:
        menu = (input(
            Fore.LIGHTMAGENTA_EX +
            " 1- SMS Gönder (Normal)\n\n 2- SMS Gönder (Turbo)\n\n 3- Çıkış\n\n"
            + Fore.LIGHTYELLOW_EX + " Seçim: "))
        if menu == "":
            continue
        menu = int(menu)
    except ValueError:
        system("cls||clear")
        print(Fore.LIGHTRED_EX + "Hatalı giriş yaptın. Tekrar deneyiniz.")
        sleep(3)
        continue

    if menu == 1:
        system("cls||clear")
        print(
            Fore.LIGHTYELLOW_EX +
            "Telefon numaralarını başında '+90' olmadan yazınız\n" +
            "(Birden fazla numara için virgülle ayırın veya dosya yolu girin): "
            + Fore.LIGHTGREEN_EX,
            end="")
        tel_input = input()
        tel_liste = []

        # Dosya yolu kontrolü
        if '/' in tel_input or '\\' in tel_input or tel_input.endswith('.txt'):
            try:
                with open(tel_input.strip(), "r", encoding="utf-8") as f:
                    for line in f.read().strip().split("\n"):
                        line = line.strip()
                        if line and len(line) == 10 and line.isdigit():
                            tel_liste.append(line)
                if not tel_liste:
                    raise ValueError("Dosyada geçerli numara bulunamadı")
            except FileNotFoundError:
                system("cls||clear")
                print(Fore.LIGHTRED_EX + "Dosya bulunamadı. Tekrar deneyiniz.")
                sleep(3)
                continue
            except Exception as e:
                system("cls||clear")
                print(Fore.LIGHTRED_EX + f"Hata: {str(e)}")
                sleep(3)
                continue
        else:
            # Virgülle ayrılmış numaralar
            numaralar = tel_input.replace(" ", "").split(",")
            for numara in numaralar:
                numara = numara.strip()
                if numara:
                    try:
                        if len(numara) == 10 and numara.isdigit():
                            tel_liste.append(numara)
                        else:
                            raise ValueError
                    except ValueError:
                        system("cls||clear")
                        print(Fore.LIGHTRED_EX + f"Hatalı telefon numarası: {numara}. Tekrar deneyiniz.")
                        sleep(3)
                        tel_liste = []
                        break

            if not tel_liste:
                continue

        # Sonsuz gönderim kontrolü
        sonsuz = len(tel_liste) == 1

        system("cls||clear")
        try:
            print(Fore.LIGHTYELLOW_EX +
                  "Mail adresi (Bilmiyorsanız 'enter' tuşuna basın): " +
                  Fore.LIGHTGREEN_EX,
                  end="")
            mail = input()
            if mail and ("@" not in mail or "." not in mail.split("@")[-1]):
                raise ValueError("Geçersiz email formatı")
        except Exception as e:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı mail adresi. Tekrar deneyiniz.")
            sleep(3)
            continue

        system("cls||clear")
        try:
            sonsuz_str = "(Sonsuz için 'enter' tuşuna basınız)" if sonsuz else ""
            print(Fore.LIGHTYELLOW_EX +
                  f"Kaç adet SMS göndermek istiyorsun {sonsuz_str}: " +
                  Fore.LIGHTGREEN_EX,
                  end="")
            kere = input()
            if kere:
                kere = int(kere)
                if kere <= 0:
                    raise ValueError
            else:
                kere = None
        except ValueError:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı giriş yaptın. Tekrar deneyiniz.")
            sleep(3)
            continue

        system("cls||clear")
        try:
            print(Fore.LIGHTYELLOW_EX +
                  "Kaç saniye aralıkla göndermek istiyorsun: " +
                  Fore.LIGHTGREEN_EX,
                  end="")
            aralik = float(input())
            if aralik < 0:
                raise ValueError
        except ValueError:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı giriş yaptın. Tekrar deneyiniz.")
            sleep(3)
            continue

        system("cls||clear")

        # SMS gönderimi
        if kere is None:  # Sonsuz gönderim
            while True:
                for tel_no in tel_liste:
                    sms = SendSms(tel_no, mail)
                    for attribute in servisler_sms:
                        method = getattr(sms, attribute)
                        if callable(method):
                            try:
                                method()
                            except:
                                pass
                            sleep(aralik)
        else:  # Belirli sayıda gönderim
            for tel_no in tel_liste:
                sms = SendSms(tel_no, mail)
                while sms.adet < kere:
                    for attribute in servisler_sms:
                        if sms.adet >= kere:
                            break
                        method = getattr(sms, attribute)
                        if callable(method):
                            try:
                                method()
                            except:
                                pass
                            sleep(aralik)
                print(f"{Fore.LIGHTGREEN_EX}✓ {tel_no} için {sms.adet} SMS gönderildi.{Style.RESET_ALL}")

        print(Fore.LIGHTRED_EX + "\nMenüye dönmek için 'enter' tuşuna basınız..")
        input()

    elif menu == 2:  # Turbo mod
        system("cls||clear")
        print(Fore.LIGHTYELLOW_EX +
              "Telefon numarasını başında '+90' olmadan yazınız: " +
              Fore.LIGHTGREEN_EX,
              end="")
        tel_no = input()

        try:
            if len(tel_no) != 10 or not tel_no.isdigit():
                raise ValueError
        except ValueError:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı telefon numarası. Tekrar deneyiniz.")
            sleep(3)
            continue

        system("cls||clear")
        try:
            print(Fore.LIGHTYELLOW_EX +
                  "Mail adresi (Bilmiyorsanız 'enter' tuşuna basın): " +
                  Fore.LIGHTGREEN_EX,
                  end="")
            mail = input()
            if mail and ("@" not in mail or "." not in mail.split("@")[-1]):
                raise ValueError
        except:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Hatalı mail adresi. Tekrar deneyiniz.")
            sleep(3)
            continue

        system("cls||clear")
        print(Fore.LIGHTCYAN_EX + "Turbo mod başlatılıyor...")
        print(Fore.LIGHTYELLOW_EX + "Durdurmak için Ctrl+C tuş kombinasyonunu kullanın.")

        send_sms = SendSms(tel_no, mail)
        dur = threading.Event()

        def turbo_worker():
            while not dur.is_set():
                threads = []
                for fonk in servisler_sms:
                    if not dur.is_set():
                        t = threading.Thread(
                            target=lambda f=fonk: getattr(send_sms, f)(),
                            daemon=True
                        )
                        threads.append(t)
                        t.start()

                for t in threads:
                    t.join(timeout=0.1)

        try:
            turbo_thread = threading.Thread(target=turbo_worker, daemon=True)
            turbo_thread.start()
            turbo_thread.join()
        except KeyboardInterrupt:
            dur.set()
            system("cls||clear")
            print("\nCtrl+C tuş kombinasyonu algılandı. Menüye dönülüyor..")
            sleep(2)

    elif menu == 3:
        system("cls||clear")
        print(Fore.LIGHTRED_EX + "Çıkış yapılıyor...")
        break