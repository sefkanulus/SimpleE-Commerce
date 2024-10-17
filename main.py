import smtplib
import sqlite3 as sqlimport 
import sqlite3 as sql
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import re
     

     
conn = sql.connect('main.db')
cursor = conn.cursor()
     


def new_account():
    while True:     
        name = input("İsim: ")
        lastname = input("Soyisim: ")
        email = input("Email: ")
        vallet = int(input("Money: "))

        try: 
            cursor.execute('''CREATE TABLE IF NOT EXISTS customers(
                        name TEXT,
                        lastname TEXT,
                        email TEXT PRIMARY KEY,
                        vallet INTEGER
                        )''')
            
            cursor.execute('''INSERT INTO customers(name, lastname, email, vallet) VALUES (?, ?, ?, ?)''', (name, lastname, email, vallet))
            
            conn.commit() 
            print("Hesap oluşturuldu! \n Giriş sayfasına yönlendiriliyorsunuz.")

            login()
            break

        except sql.IntegrityError:
            print("Bu email ile kayıt oluşturuldu.")
    


def login():
    global email
    while True:
            email = input("Email: ")       
            cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
            user = cursor.fetchone() 

            if user:  
                print("Giriş başarılı!")
                break  
            else:
                print("Bu email kayıtlı değil. Tekrar deneyin.")



def first_page():
    choose = input("1. Yeni hesap oluştur\n2. Hesap girişi\n\nSeciminiz:")
    if (choose == "1"):
        new_account()
    elif (choose == "2"):
        login()



def new_order():
    while True:
        print("sipariş Oluşturun.")
        cursor.execute("SELECT id, name FROM products")
        rows = cursor.fetchall()
        print("Urunler:")
        for row in rows:
            print(row[0], row[1])
        
        choice_input = input("Siparişe eklemek istediğiniz ürünlerin numarasını boşluk bırakarak giriniz: ")
        try:
            choice = [int(num) for num in choice_input.split()]
            
            # Seçilen ürünlerin bilgilerini listeye ekle
            result = []
            for i in choice:
                cursor.execute(f"SELECT name,price FROM products WHERE id = ?", (i,))
                row = cursor.fetchone()
                if row:  # Eğer ürün bulunduysa
                    result.append(row)
            
            # result listesinde ürün bilgileri tuple olarak yer alacak
            if not result: # result boş ise
                print("Hatalı ürün girdiniz. Lütfen tekrar deneyin.")
                continue # Müşteriden tekrar sipariş alır

            print("Sepetiniz: ")
            for item in result:
                print(item[0], item[1])


            # Toplam fiyatı hesapla
            total_price = sum([item[1] for item in result])
            print("Toplam fiyat:", total_price)
            print("Siparişiniz hazırlanıyor...")
            break

            # if total_price > 0: # Fiyat 0 dan büyükse ürün girilmiş demektir.
            #     print("Siparişiniz hazırlanıyor...")
            #     break
            # else:
            #     print("Hatalı ürün girdiniz. Lütfen tekrar deneyin.")
            #     continue

        except ValueError:
            print("Lütfen sadece geçerli ürün numaralarını girin.")
            continue

    cursor.execute("SELECT name, lastname FROM customers WHERE email = ?", (email,))
    name, lastname = cursor.fetchone()

    # Ürün isimlerini birleştir
    product_names = ", ".join([item[0] for item in result])

    order_status = "Sipariş hazırlanıyor."

    cursor.execute(
        "INSERT INTO active_orders(email, name, lastname, products_names, total_price, order_status) VALUES(?,?,?,?,?,?)", 
        (email, name, lastname, product_names, total_price, order_status)
    )

    conn.commit()



def send_mail_hazirlaniyor():
   sender_email = "sfknulus01@gmail.com"
   receive_email = email
   sender_password = "bghc fjwy ghjv jcvb"
   smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
   smtp_server.starttls() # TLS başlatır.
   smtp_server.login(sender_email, sender_password)

   try:
      msg = MIMEMultipart()
      msg["From"] = sender_email
      msg["To"] = receive_email
      msg["Subject"] = "SİPARİŞİNİZ"

      body = "Siparişiniz hazırlanıyor..."
      msg.attach(MIMEText(body, "plain"))

      text = msg.as_string()
      smtp_server.send_message(msg)
      print("Hazırlanıyor emaili gönderildi.")

   except Exception as e:
      print(f"Bir hata oluştu: {e}")

   finally:
      smtp_server.quit()




def send_mail_teslim():
    print("Teslim edildi.")
    cursor.execute("UPDATE active_orders SET order_status = 'Teslim edildi.' WHERE email = ?", (email,))
    cursor.execute("INSERT INTO inactive_orders SELECT id, email, name, lastname, products_names, total_price, order_status from active_orders WHERE email = ?", (email,))
    cursor.execute("DELETE FROM active_orders WHERE email = ?", (email,))
    conn.commit()
    sender_email = "sfknulus01@gmail.com"
    receive_email = email
    sender_password = "bghc fjwy ghjv jcvb"
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls() # TLS başlatır.
    smtp_server.login(sender_email, sender_password)

    try:
       msg = MIMEMultipart()
       msg["From"] = sender_email
       msg["To"] = receive_email
       msg["Subject"] = "SİPARİŞ TESLİM"

       body = "Siparişiniz teslim edildi."
       msg.attach(MIMEText(body, "plain"))

       text = msg.as_string()
       smtp_server.send_message(msg)
       print("Teslim emaili gönderildi.")

    except Exception as e:
       print(f"Bir hata oluştu: {e}")

    finally:
       smtp_server.quit()





if __name__ == "__main__":
    first_page()
    print("Hosgeldiniz.")
    new_order()
    send_mail_hazirlaniyor()
    time.sleep(5)
    while True:    
        print("Siparişi teslim aldınız mı? Evet-Hayır")
        answer = input()
        if answer == "Evet" or answer == "evet":
            send_mail_teslim()
            break
        elif answer == "Hayır" or answer == "hayır":
            print("Gecikme için üzgünüz.")
            send_mail_hazirlaniyor()
            continue


conn.close()

