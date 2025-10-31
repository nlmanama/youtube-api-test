import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")

with app.setup:
    # Initialization code that runs before all other cells

    import marimo as mo
    import matplotlib.pyplot as plt
    import os
    import dotenv
    import googleapiclient.discovery
    import googleapiclient.errors
    import pandas as pd
    import isodate

    # To access API_KEY
    # Code taken from https://www.geeksforgeeks.org/python/how-to-create-and-use-env-files-in-python/

    dotenv.load_dotenv(dotenv_path='.env')

    # Setting up API

    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, developerKey=os.getenv("API_KEY"))


@app.cell
def _():
    # Next three cells are code taken from the Google Developer Guide and modified
    # https://developers.google.com/youtube/v3/docs/videos/list
    # -*- coding: utf-8 -*-

    # Sample Python code for youtube.videos.list
    # See instructions for running these code samples locally:
    # https://developers.google.com/explorer-help/code-samples#python


    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # The line above is taken straight from the Google Developer Guide and I don't really understand the consequences of this right now so I will not touch it
    return


@app.function
# Helper function 1

def request_videos(part, chart, amount):
    request = youtube.videos().list(
        part=part,
        chart=chart,
        maxResults = amount
    )
    response = request.execute()
    return response


@app.cell
def _():
    # Testing code - should probably be removed or comment out in student code version

    # Making the request for the statistics of 20 most viral videos
    # Contains things like viewCount, likeCount etc
    statistics_response = request_videos("statistics", "mostPopular", 20)

    # Making the request for the contentDetails of 20 most viral videos
    # Contains things like video duration
    content_response = request_videos("contentDetails", "mostPopular", 20)
    # Resopnse object to be passed into functions to use
    return content_response, statistics_response


@app.function
# Helper function 2

def save_graph_png(plt, graph_name):
    plt.savefig(graph_name, dpi=300, bbox_inches='tight')
    print(f"Plot saved as '{graph_name}'")
    plt.show()


@app.function
# Question 1 - easiest

def video_length_historgram(response):
    # Extract video durations
    durations = []
    for item in response["items"]:
        durations.append(item["contentDetails"]["duration"])

    # Convert ISO 8601 durations to seconds
    seconds = []
    for duration in durations:
        total_seconds = isodate.parse_duration(duration).total_seconds()
        seconds.append(total_seconds)

    # Create a DataFrame for easier handling
    df = pd.DataFrame(seconds, columns=["Video Length (seconds)"])

    # Plot histogram
    plt.figure(figsize=(8, 5))
    plt.hist(df["Video Length (seconds)"], bins=10, edgecolor="black")
    plt.title("Distribution of YouTube Video Lengths")
    plt.xlabel("Length (seconds)")
    plt.ylabel("Number of Videos")
    plt.grid(True, alpha=0.3)
    plt.show()
    save_graph_png(plt, "duration.png")


@app.cell
def _(content_response):
    # Testing code - should probably be removed or comment out in student code version

    video_length_historgram(content_response)
    return


@app.function
# Question 2 part 1 (parsing)

def get_video_dislikes(response, r, n):
    """
    Return the n most disliked videos from the 30 most popular videos.

    Parameters:
    - r: like-to-dislike ratio (0 < r < 1)
    - n: number of videos to return (0 < n <= 30)

    Returns:
    - list of n videos
    """

    videos = []

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


@app.function
# Question 2 part 2 - plotting (or we can just give code as it and not make it a question)

def dislike_count_scatter_plot(videos):
    # Parsing response
    # Response JSON format shown here: https://developers.google.com/youtube/v3/docs/videos/list
    # Video format: https://developers.google.com/youtube/v3/docs/videos#resource
    view_count = []
    dislike_count = []

    for video in videos:
        view_count.append(video["statistics"]["viewCount"])
        dislike_count.append(video["statistics"]["dislikeCount"])

    # Plotting a chart

    fig, ax = plt.subplots()

    ax.scatter(view_count, dislike_count, alpha=0.6)

    # Slightly hacky solution to make the x-axis cleaner
    # Found here: https://stackoverflow.com/questions/54783160/x-axis-tick-labels-are-too-dense-when-drawing-plots
    ax.set_xticks(ax.get_xticks()[::3])


    ax.set_xlabel("View Count")
    ax.set_ylabel("Dislike Count")
    ax.set_title("Scatter Plot of View Count to Dislike Count")

    save_graph_png(fig, "dislikeCount.png")
    return plt.gca()


@app.cell
def _(statistics_response):
    # Testing code - should probably be removed or comment out in student code version

    dislike_count_scatter_plot(get_video_dislikes(statistics_response, 0.86, 30))
    dislike_count_scatter_plot(get_video_dislikes(statistics_response, 0.5, 15))
    return


if __name__ == "__main__":
    app.run()
