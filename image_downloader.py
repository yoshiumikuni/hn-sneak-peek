# from tqdm import tqdm
# from time import sleep
# import concurrent.futures

# def count(range_count):
# 	for i in tqdm(range(int(range_count))):
# 		pass

# def main():
# 	with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
# 		executor.submit(count, 300000)
# 		executor.submit(count, 500000)
# 		executor.submit(count, 9000000)
# 		executor.submit(count, 1000000)

# if __name__ == '__main__':
# 	main()

# def split_list(a_list, wanted_parts=1):
# 	length = len(a_list)
# 	return [a_list[i*length // wanted_parts: (i+1)*length // wanted_parts]
# 		for i in range(wanted_parts)]

# lst = []
# for i in range(11):
# 	lst.append(i)

# for i in split_list(lst, 4):
# 	for j in i:
# 		print(j)
# 	print('---')

from tqdm import tqdm
import requests

url = "https://raw.githubusercontent.com/yoshiumikuni/hn-sneak-peek/main/res/image/catgirl.png" #big file test
# Streaming, so we can iterate over the response.
response = requests.get(url, stream=True)
print(response.raw)
# total_size_in_bytes= int(response.headers.get('content-length', 0))
# block_size = 1024 #1 Kibibyte
# progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
# with open('test.dat', 'wb') as file:
#     for data in response.iter_content(block_size):
#         progress_bar.update(len(data))
#         file.write(data)
# progress_bar.close()
# if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
#     print("ERROR, something went wrong")