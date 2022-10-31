import os
from io import BytesIO

from slack_sdk import WebClient
from src.config import Credentials
from tabulate import tabulate

DEFAULT_SLACK_TOKEN = Credentials.SLACK_TOKEN


class SlackBot:
    """
    Class to create a SlackBot
    """

    def __init__(self, channel, token=DEFAULT_SLACK_TOKEN):
        """ 
        Create the object with a token and the target channel.
        """

        self.channel = channel
        self.client = WebClient(token=token)

    def send_message(self, text):
        """ 
        Send a simple message to the object channel

        :param text: (str) Desired message
        :return: Slack's api return to post_message

        Usage:
            slack.send_message('Hello World')
        """

        result = self.client.chat_postMessage(channel=self.channel, text=text)

        return result

    def send_dataframe(self, df, title=None):
        """ 
        Send a Dataframe to the object channel

        :param df: Desired Dataframe
        :param title: Header message
        :return: Slack's api return to post_message

        Usage:
            slack.send_dataframe(df, title = "This is the Dataframe")
        """

        df = df.copy()
        df.reset_index(drop=True, inplace=True)

        size = df.shape[0]
        slack_limit = 50

        for i in range(0, size, slack_limit):
            data = df.iloc[i:i + slack_limit]
            text = "```" + tabulate(data.values.tolist(),
                                    headers=data.columns.tolist()) + "```"

            if title:
                text = title + '\n' + text
                title = False

            result = self.send_message(text)

        return result

    def send_plot(self, plot, plot_name, title=None):
        """
        Send an Image to the object channel

        :param fig: plot made by seaborn or matplotlib
        :param fig_name: name of the image
        :param title: Header message
        :return: Slack's api return to post_message

        Usage:
            slack.send_plot(plot, "Sample Image", title = "This is the Image")
        """

        buf = BytesIO()
        plot.figure.savefig(buf, format='png')
        buf.seek(0)

        result = self.client.files_upload(channels=self.channel,
                                          filename='plot.png',
                                          title=plot_name,
                                          initial_comment=title,
                                          file=buf)

        return result
