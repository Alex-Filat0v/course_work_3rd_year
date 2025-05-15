import hashlib
import time


def md5_checksum(filepath):
    hash_md5 = hashlib.md5()
    # Открываем файл в бинарном режиме
    with open(filepath, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    # Возвращаем шестнадцатеричное представление контрольной суммы
    return hash_md5.hexdigest()



start_time = time.time()
checksum = md5_checksum("sum.txt")
end_time = time.time()

print(f"Контрольная сумма: {checksum}")
print(f"Время выполнения: {end_time - start_time:.16f} секунд")
