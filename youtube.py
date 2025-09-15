# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "google-api-python-client==2.181.0",
#     "matplotlib==3.10.6",
#     "python-dotenv==1.1.1",
# ]
# ///

import marimo

__generated_with = "0.15.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Youtube API Project""")
    return


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    return mo, plt


@app.cell
def _():
    # To access API_KEY
    # Code taken from https://www.geeksforgeeks.org/python/how-to-create-and-use-env-files-in-python/

    import os
    from dotenv import load_dotenv, dotenv_values 
    load_dotenv() 
    return (os,)


@app.cell
def _(os):
    # Next three cells are code taken from the Google Developer Guide and modified
    # https://developers.google.com/youtube/v3/docs/videos/list
    # -*- coding: utf-8 -*-

    # Sample Python code for youtube.videos.list
    # See instructions for running these code samples locally:
    # https://developers.google.com/explorer-help/code-samples#python
    import googleapiclient.discovery
    import googleapiclient.errors

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # The line above is taken straight from the Google Developer Guide and I don't really understand the consequences of this right now so I will not touch it
    return (googleapiclient,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    - Create a Google Developer account on [Google Developer Console](https://console.cloud.google.com)
    - Create a project called `cpsc-203`
    - Go to [API Library – APIs & Services](https://console.cloud.google.com/apis/library), search for `youtube data api v3` and select *YouTube Data API v3*
    - Click on *Create credentials* in the top right
    - In the create credentials screen, choose the *Public data* radio button and click on *Next*.
    - Copy the API key and treat it like a password by saving it in save place (for example, a password manager)
    - In your project directory, create a `.env` file and add the following line:

      ```
      API_KEY=<your-youtube-api-key>
      ```

    - Save and close the file.
    """
    )
    return


@app.cell
def _(googleapiclient, os):
    # Setting up API using `API_KEY` in `.env`
    # load_dotenv()

    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, developerKey=os.getenv("API_KEY")
    )
    return (youtube,)


@app.cell
def _(youtube):
    # Making the request for the 20 most viral videos

    request = youtube.videos().list(
        part="statistics",
        chart="mostPopular",
        maxResults = 20
    )
    response = request.execute()
    return (response,)


@app.cell
def _(response):
    # Parsing response
    # Response JSON format shown here: https://developers.google.com/youtube/v3/docs/videos/list
    # Video format: https://developers.google.com/youtube/v3/docs/videos#resource

    view_count = []
    like_count = []

    for video in response["items"]:
        view_count.append(video["statistics"]["viewCount"])
        like_count.append(video["statistics"]["likeCount"])

    return like_count, view_count


@app.cell
def _(like_count, plt, view_count):
    # Plotting a chart

    fig, ax = plt.subplots()

    ax.scatter(view_count, like_count, alpha=0.6)

    # Slightly hacky solution to make the x-axis cleaner
    # Found here: https://stackoverflow.com/questions/54783160/x-axis-tick-labels-are-too-dense-when-drawing-plots
    ax.set_xticks(ax.get_xticks()[::3])


    ax.set_xlabel("View Count")
    ax.set_ylabel("Like Count")
    ax.set_title("Scatter Plot of View Count to Like Count")


    return


if __name__ == "__main__":
    app.run()
