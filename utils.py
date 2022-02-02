def processing(all_data):
    def check_nested(obj):
        if isinstance(obj, (list, tuple, dict)):
            return True
        else:
            return False

    # Nested values we want to keep
    nested_values = ['video', 'author', 'music', 'stats', 'authorStats']

    processed_data = {}

    # Loop through videos
    for idx, data in enumerate(all_data):
        processed_data[idx] = {}
        # Loop through video properties
        for data_key, data_val in data.items():
            if not check_nested(data_val):
                processed_data[idx][data_key] = data_val
            elif data_key in nested_values:
                # Loop through properties elements
                for nested_key, nested_val in data_val.items():
                    current_key = f"{data_key}_{nested_key}"
                    processed_data[idx][current_key] = nested_val

    return processed_data


def author_count_activity(dataframe, n_authors=5):
    from numpy import mean, sum
    sub_df = dataframe.groupby('author_nickname').agg({'video_duration': mean,
                                                       'id': len,
                                                       'NbOfLikes': sum})\
        .rename(columns={'id': 'activity', 'video_duration': 'video_mean_duration',
                         'NbOfLikes': 'sum_of_likes'}).sort_values('activity', ascending=False)\
        .iloc[:n_authors]
    sub_df['signature'] = sub_df.index.map(
        lambda x: dataframe[dataframe['author_nickname'] == x].iloc[0]['author_signature'])

    return sub_df.reset_index()


def build_word_cloud(dataframe, hashtag, n_words=10):
    import re
    from collections import Counter
    # List of list of hashtags. Each sublist is hashtag of one video
    all_hashtag_list = dataframe['desc'].apply(
        lambda x: re.findall(r"#(\w+)", x)).tolist()
    # Get one unique list
    all_hashtags = [word.lower()
                    for hashtag_list in all_hashtag_list for word in hashtag_list]
    # Get a dict with count for each hashtag
    counter_dic = Counter(all_hashtags)
    # Deleter the researched hashtag and the fyp ones
    key_to_delete = [hashtag.lower(), hashtag]
    for key in counter_dic:
        if 'fyp' in key:
            key_to_delete.append(key)
    for key in key_to_delete:
        del counter_dic[key]
    # Return the others
    return dict(counter_dic.most_common(n_words))
