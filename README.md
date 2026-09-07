<h2 align="center">CÁCH CÀI ĐẶT VÀ CHẠY SERVER</h2>Bước 1: Cài đặt Git

```pkg install git -y```

Bước 2: Clone source server

```git clone https://github.com/ALKAstraverse/hso-server```

Sau khi clone xong, truy cập vào thư mục source:

```cd hso-server```

Kiểm tra đường dẫn hiện tại:

```pwd```

Ví dụ Termux sẽ hiển thị:

```/data/data/com.termux/files/home/hso-server```

«Lưu ý: Đường dẫn có thể khác tùy thiết bị và cách cài đặt Termux. Hãy dùng kết quả của "pwd" làm đường dẫn source server.»

---

<h2 align="center">CÀI ĐẶT JAVA & MAVEN</h2>Bước 3: Cài đặt Java 17

```pkg install openjdk-17 -y```

Bước 4: Cài đặt Maven

```pkg install maven -y```

Kiểm tra:

```java -version```
```mvn -version```

---

<h2 align="center">BUILD SOURCE SERVER</h2>Bước 5: Build server

Nếu đang ở thư mục "hso-server":

```mvn clean package```

Sau khi build thành công, file ".jar" sẽ được tạo trong:

```target/```

File server:

```target/HSO_Re_2-1.0-jar-with-dependencies.jar```

---

<h2 align="center">CHẠY SERVER</h2>Từ thư mục "hso-server":

```java -jar -server target/HSO_Re_2-1.0-jar-with-dependencies.jar```

---

<h2 align="center">CÁCH SỬA IP FILE CLIENT</h2>Sửa IP

File: dw.class
Dòng: 51, 63, ...

Sửa Port

File: ft.class
Dòng: 273 -> 278

Port được mã hóa bằng HEX.

Ví dụ:

19129 = 0x4AB9

---

<h2 align="center">CẤU HÌNH KHÁC</h2>Kết nối Database

File cấu hình:

```hso.conf```

## ⚠️ Disclaimer

> **Mục đích sử dụng:** Source code này được công khai nhằm mục đích **học tập, nghiên cứu và tham khảo**.

- Không sử dụng source code cho các mục đích **vi phạm pháp luật**.
- Người sử dụng tự chịu trách nhiệm về mọi hoạt động và hành vi phát sinh từ việc sử dụng source code.
- Tác giả không chịu trách nhiệm đối với bất kỳ thiệt hại hoặc hành vi sử dụng sai mục đích nào.
- Vui lòng tuân thủ pháp luật hiện hành và các quy định liên quan khi sử dụng dự án.

**By using this source code, you agree to use it for lawful purposes only.**
