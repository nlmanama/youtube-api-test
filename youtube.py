import marimo

__generated_with = "0.17.2"
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
    load_dotenv(dotenv_path='.env')
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


@app.cell
def _(googleapiclient, os):
    # Setting up API

    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, developerKey=os.getenv("API_KEY"))
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
def _(plt):
    def save_graph(videos, axis, graph_name):
        # Parsing response
        # Response JSON format shown here: https://developers.google.com/youtube/v3/docs/videos/list
        # Video format: https://developers.google.com/youtube/v3/docs/videos#resource
        view_count = []
        axis_count = []

        for video in videos:
            view_count.append(video["statistics"]["viewCount"])
            axis_count.append(video["statistics"][axis])

        # Plotting a chart
    
        fig, ax = plt.subplots()
    
        ax.scatter(view_count, axis_count, alpha=0.6)
    
        # Slightly hacky solution to make the x-axis cleaner
        # Found here: https://stackoverflow.com/questions/54783160/x-axis-tick-labels-are-too-dense-when-drawing-plots
        ax.set_xticks(ax.get_xticks()[::3])
    
    
        ax.set_xlabel("View Count")
        ax.set_ylabel(axis)
        ax.set_title("Scatter Plot of View Count to " + axis)

        plt.savefig(graph_name, dpi=300, bbox_inches='tight')
        print(f"Plot saved as '{graph_name}'")
        plt.show()
    
        return 0
    return (save_graph,)


@app.cell
def _(response, save_graph):
    save_graph(response["items"], "likeCount", "like_scatter_plot.png")
    return


@app.cell
def _(youtube):
    def get_video_dislikes(r, n):
        """
        Return the n most disliked videos from the 30 most popular videos.
    
        Parameters:
        - r: like-to-dislike ratio (0 < r < 1)
        - n: number of videos to return (0 < n <= 30)
    
        Returns:
        - list of n videos
        """

        videos = []
        request = youtube.videos().list(
            part="statistics",
            chart="mostPopular",
            maxResults = 30
        )
        response = request.execute()

        for v in response["items"]:
            stats = v["statistics"]

            if "likeCount" not in stats:
                like_count = 0
            else:    
                like_count = int(stats["likeCount"])
        
            view_count = int(stats["viewCount"])

            estimated_dislikes = like_count * (1 - r) / r
            v["statistics"]["dislikeCount"] = estimated_dislikes
            videos.append(v)

        videos.sort(key=lambda x: x["statistics"]["dislikeCount"], reverse=True)
    
        return videos[:n]

    return (get_video_dislikes,)


@app.cell
def _(get_video_dislikes, save_graph):
    save_graph(get_video_dislikes(0.86, 30), "dislikeCount", "dislike_scatter_plot_1.png")
    save_graph(get_video_dislikes(0.5, 15), "dislikeCount", "dislike_scatter_plot_2.png")
    return


if __name__ == "__main__":
    app.run()
