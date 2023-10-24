import httpx
import asyncio
import os

# ANSI escape sequences untuk mengubah warna teks menjadi hijau
RED_TEXT = "\033[31m"
GREEN_TEXT = "\033[32m"
YELLOW_TEXT = "\033[33m"
RESET_TEXT = "\033[0m"

# URL tempat Anda ingin mengirim POST request
url = 'https://shopee.co.id/api/v1/microsite/get_vouchers_by_collections'

# Menampilkan daftar file cookie dalam folder "akun"
account_cookies = []

for root, _, files in os.walk("akun"):
    for file in files:
        if file.endswith(".txt"):
            account_cookies.append(file)

if not account_cookies:
    print("Tidak ada file cookie di dalam folder 'akun'.")
    exit()

# Menampilkan daftar file cookie yang tersedia
print("Daftar file cookie yang tersedia:")

for i, cookie_file in enumerate(account_cookies, 1):
    print(f"{i}. {cookie_file}")

# Meminta pengguna untuk memilih file cookie
selected_cookie_index = int(os.environ.get("COOKIE_IDX"))

if selected_cookie_index < 0 or selected_cookie_index >= len(account_cookies):
    print("Nomor file cookie yang dipilih tidak valid.")
    exit()

# Mendapatkan nama file cookie yang dipilih
selected_cookie_filename = account_cookies[selected_cookie_index]

# Membaca cookie dari file yang dipilih
selected_cookie_file = os.path.join("akun", selected_cookie_filename)

try:
    with open(selected_cookie_file, 'r') as file:
        cookies = file.read().strip()
except FileNotFoundError:
    cookies = ''

# Meminta masukan collection_id awal dan akhir dari pengguna
print("Contoh input: Awal: 12905192072, Akhir: 12905192100")
start_collection_id = int(os.environ.get("START_COLLECTION_ID"))
end_collection_id = int(os.environ.get("END_COLLECTION_ID"))

# Membuat daftar collection_id berdasarkan rentang yang dimasukkan oleh pengguna
collection_ids = list(range(start_collection_id, end_collection_id + 1, 128))

# Meminta masukan voucher_code dari pengguna
print("Contoh input DC10010RB1109")
voucher_code = os.environ.get("VOUCHER_CODE")

# Fungsi untuk mengirim permintaan POST untuk sekelompok collection_id
async def send_batch_post_request(batch_collection_ids):
    batch_responses = []
    for collection_id in batch_collection_ids:
        response = await send_post_request(collection_id)
        batch_responses.append((collection_id, response))
    return batch_responses


# Fungsi untuk mengirim permintaan POST untuk setiap collection_id dalam daftar
async def send_post_request(collection_id):
    data = {
        "voucher_collection_request_list": [
            {
                'collection_id': f'{collection_id}',
                'component_type': 2,
                'component_id': 1694165901230,
                'limit': 1,
                'microsite_id': 58982,
                'offset': 0,
                'number_of_vouchers_per_row': 1
            }
        ]
    }

    headers = {
        'sec-ch-ua': '"Chromium";v="117", "Not)A;Brand";v="24", "Google Chrome";v="117"',
        'x-sap-access-f': '3.2.116.2.0|13|3.0.0-2_5.1.0_0_190|784dd15ccce2475684721235da92b1b757f621a0156148|10900|1100',
        'x-sz-sdk-version': '3.0.0-2&1.4.1',
        'x-shopee-language': 'id',
        'x-requested-with': 'XMLHttpRequest',
        'x-sap-access-t': '1694342213',
        'af-ac-enc-dat': '',
        'x-sap-access-s': 'qnFNFMh0Mr_ZRQrNrEoy9VqxVSB13p_UxSaNfeTzGb0=',
        'x-csrftoken': '1mW7f6VfXqTkAnbJOY7oEJT3vrn9rXEj',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'x-api-source': 'pc',
        'content-type': 'application/json',
        'accept': 'application/json',
        'af-ac-enc-sz-token': 'KxZqTmsEqOjnfQd8f/IVvw==|6+FsNL8sN0Nv3RCgOMEW9TxuxhNhhZg/7J0heaEDEZBL5pVaH3HOicjqxZEPX4qvrbox6osc918=|6kNACG0agU32B4wE|08|3',
        'origin': 'https://shopee.co.id',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://shopee.co.id/m/9-9',
        #'accept-encoding': 'gzip, deflate, br',
        #'accept-language': 'en-US,en;q=0.9,id;q=0.8',
        'cookie': cookies,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers, timeout=30.0)

    return response

# Loop melalui setiap collection_id dalam daftar dan kirim permintaan POST
async def main():
    batch_size = 5  # Jumlah batch yang ingin Anda proses secara bersamaan
    total_batches = len(collection_ids) // batch_size + (1 if len(collection_ids) % batch_size != 0 else 0)

    for batch_num in range(total_batches):
        start_index = batch_num * batch_size
        end_index = (batch_num + 1) * batch_size
        batch_collection_ids = collection_ids[start_index:end_index]

        print(f"Processing Batch {batch_num + 1} of {total_batches}")
        batch_responses = await send_batch_post_request(batch_collection_ids)

        for collection_id, response in batch_responses:
            if response.status_code == 200:
                # print(f"POST request berhasil untuk collection_id: {collection_id}")
                # print("Response:")
                # Aktifkan print(response.json()) dengan menghapus tanda #
                # print(response.json())

                # Mengecek jika voucher_data_list adalah None
                response_data = response.json()
                voucher_data_list = response_data.get("data")

                if voucher_data_list is not None:
                    # Mencari 'voucher_code' dalam respons dan menampilkan informasi voucher jika ditemukan
                    voucher_found = False
                    for voucher_data in voucher_data_list:
                        vouchers = voucher_data.get("vouchers", [])
                        for voucher in vouchers:
                            voucher_info = voucher.get("voucher", {})
                            if voucher_info.get("voucher_identifier", {}).get("voucher_code") == voucher_code:
                                print("Voucher ditemukan:")
                                print(f"{GREEN_TEXT}promotion_id: {voucher_info.get('voucher_identifier', {}).get('promotion_id')}{RESET_TEXT}")
                                print(f"{GREEN_TEXT}voucher_code: {voucher_info.get('voucher_identifier', {}).get('voucher_code')}{RESET_TEXT}")
                                print(f"{GREEN_TEXT}signature: {voucher_info.get('voucher_identifier', {}).get('signature')}{RESET_TEXT}")
                                print(f"{GREEN_TEXT}collection_id: {collection_id}{RESET_TEXT}")
                                voucher_found = True
                                return
                        if voucher_found:
                            break
                    if not voucher_found:
                        print(f"{YELLOW_TEXT}Voucher dengan kode '{voucher_code}' tidak ditemukan.{RESET_TEXT}")
                        print(f"{GREEN_TEXT}voucher_code yang ditemukan: {voucher_info.get('voucher_identifier', {}).get('voucher_code')}{RESET_TEXT}")
                        print(f"{GREEN_TEXT}collection_id: {collection_id}{RESET_TEXT}")
                else:
                    print(f"{RED_TEXT}Tidak ada data ditemukan untuk collection_id: {collection_id}{RESET_TEXT}")

            else:
                print(f"{RED_TEXT}POST request gagal untuk collection_id: {collection_id}, dengan status code: {response.status_code}{RESET_TEXT}")

if __name__ == "__main__":
    asyncio.run(main())
