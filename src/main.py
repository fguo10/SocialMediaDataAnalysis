import json
import time

import tweepy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# twitter developer access token
# Your app's API/consumer key and secret can be found under the Consumer Keys
# section of the Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
CONSUMER_KEY = "xxxx"
CONSUMER_SECRET = "xxxx"

# Your account's (the app owner's account's) access token and secret for your
# app can be found under the Authentication Tokens section of the
# Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
ACCESS_TOKEN = "xxx"
ACCESS_TOKEN_SECRET = "xxx"

# read file which save users list
SCREEN_NAME_FILENAME = 'doc/users.txt'
ALL_FRIENDS_FILENAME = 'doc/all_friends.json'


def get_users():
    """get all usernames from files which is we want to get from twitter"""
    with open(SCREEN_NAME_FILENAME) as f:
        users = [line.strip() for line in f]
        return users


def load_friends_to_dict():
    with open(ALL_FRIENDS_FILENAME) as f:
        return json.load(f)


class TwitterDataCollection:
    def __init__(self):
        """
        Twitter requires all requests to use OAuth for authentication.
        The Authentication documentation goes into more details about authentication.
        """
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth, retry_count=5, retry_delay=60, wait_on_rate_limit=True)

    def get_one_user_detail(self, username):
        """
        get one user friends information: top_20_friends_list and friends_count
        :param username: twitter name, eg:HillaryClinton
        :return:top_20_friends_list, friends_count
        """
        user = self.api.get_user(screen_name=username)
        friends = []
        for friend in user.friends():
            friends.append(friend.screen_name)
        return friends, user.friends_count

    def get_all_friends(self, try_count=5) -> dict:
        """
        get the Twitter friends objects for each screen_name
        :return:
        """
        all_friends = {}
        load_users = get_users()
        for username in load_users:
            for i in range(try_count):
                try:
                    data = self.get_one_user_detail(username)
                    all_friends[username] = {
                        'friends': data[0],
                        'friends_count': data[1]
                    }
                except Exception as e:
                    print('get twitter friends limit, sleep 15min')
                    time.sleep(15)
                else:
                    break
        return all_friends

    def save_friends_to_json(self, all_friends):
        """
        save the data into file
        :param all_friends: dict, Twitter friends objects for each screen_name
        :return:
        """
        with open(ALL_FRIENDS_FILENAME, 'w') as f:
            json.dump(all_friends, f, indent=4)


class DataVisualization:
    def get_friends_count(self, screen_name):
        all_friends = load_friends_to_dict()
        return len(all_friends.get(screen_name, {}).get('friends_count'))

    def add_nodes(self, G_asymmetric, screen_name, friends):
        for friend in friends:
            G_asymmetric.add_edge(screen_name, friend)

    def get_graph_options(self):
        options = {
            "font_size": 3,
            "node_size": 100,
            "node_color": "#A0CBE2",
            "edgecolors": "#A0CBE2",
            "linewidths": 0.1,
            "width": 0.1,
        }
        return options

    def save_graph(self, G_asymmetric):
        nx.spring_layout(G_asymmetric)
        nx.draw_networkx(G_asymmetric, **self.get_graph_options())
        time_stamp = time.strftime('%m%d_%H%M')
        plt.axis("off")
        plt.savefig(f'doc/network_{time_stamp}.png', dpi=300)
        plt.show()

    def build_graph(self, draw_screen_names=None):
        G_asymmetric = nx.DiGraph()
        all_friends = load_friends_to_dict()
        for screen_name, data in all_friends.items():
            friends = data.get('friends', [])
            if not draw_screen_names:
                self.add_nodes(G_asymmetric, screen_name, friends)
            else:
                if screen_name in draw_screen_names:
                    self.add_nodes(G_asymmetric, screen_name, friends)
        return G_asymmetric



class DataAnalysis:
    def __init__(self):
        visualize_obj = DataVisualization()
        self.graph_obj = visualize_obj.build_graph()
        self.degree_sequence = sorted([d for n, d in self.graph_obj.degree()], reverse=True)

    def draw_degree_histogram(self):
        plt.bar(*np.unique(self.degree_sequence, return_counts=True))
        plt.title('Degree histogram')
        plt.xlabel('Degree')
        plt.ylabel('# of Nodes')
        plt.savefig(f'doc/degree_histogram.png', dpi=300)
        plt.show()

    def draw_degree_rank_plot(self):
        plt.plot(self.degree_sequence, "b-", marker="o", label='')
        plt.title('Degree Rank Plot')
        plt.xlabel('Degree')
        plt.ylabel('Rank')
        plt.savefig(f'doc/degree_rank_plot.png', dpi=300)
        plt.show()


def crawl_data():
    twitter = TwitterDataCollection()
    all_friends = twitter.get_all_friends()
    twitter.save_friends_to_json(all_friends)


def visualize_data():
    visualize_obj = DataVisualization()
    visualize_obj.build_graph(draw_screen_names=['BarackObama', 'BillGates', 'BillClinton'])
    visualize_obj.build_graph(draw_screen_names=['illinoistech', 'ILTechAthletics', 'CoachEdIIT'])
    visualize_obj.build_graph()


def analysis_data():
    analyze_obj = DataAnalysis()
    analyze_obj.draw_degree_rank_plot()
    analyze_obj.draw_degree_histogram()


if __name__ == '__main__':
    # crawl_data()
    # visualize_data()
    analysis_data()
