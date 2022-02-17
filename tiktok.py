# Import libraries
from time import sleep
from TikTokApi import TikTokApi as tiktok
from utils import processing
import pandas as pd
import sys


async def get_data(hashtag, nb_lines='50'):
    nb_lines = int(nb_lines)
    # Cookie data
    verifyFp = "verify_4fb73d0c964f3849e16574a5ac21ef7c"
    api = tiktok.get_instance(custom_verify=verifyFp, use_test_endpoints=True)
    # Get data by hashtag, try fetch data 3 times before giving up
    for i in range(0, 10):
        try:
            trending = await api.by_hashtag(hashtag, count=nb_lines)
            break
        except:
            print(f"Tried to fetch data {i + 1} times.")
            sleep(4)
        if i == 10:
            print("This challenge does not exists.")
            print()
            pd.DataFrame().to_csv('tiktokData.csv')
            exit()

    # Process data
    processed_data = processing(trending)

    # Convert processed data into csv
    pd.DataFrame.from_dict(
        processed_data, orient='index').to_csv('tiktokData.csv')
    return pd.DataFrame.from_dict(processed_data, orient='index')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        get_data(sys.argv[1])
    else:
        get_data(sys.argv[1], sys.argv[2])
