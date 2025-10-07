# Project 1 Instructions

## Project Overview
Learning objectives:

- Use pandas dataframes as a fundamental structure
- Filter, project, reassemble data frames to extract information
- Report and visualize information using a variety of plots

This project leads you through how to collect data from a web service through API connections. Rather than using data from Billboard, we will use and collect data from the Youtube Data API provided by Google. It is avaliable as a Python library through `google-api-python-client`. This allows you to collect and work with live data. We will use this to get data on the most viral Youtube videos and their features!

## Download instructions
Get your code by downloading the zip file provided on PrarieLearn. Move it to the directory where your coursework code is at.

To unzip a folder in Windows: right click the folder and select "Extract All". Follow the instructions shown to store the unzipped folder at a location you want.

To unzip a folder in MacOS: simply double click the folder and it should automatically unzip. The unzipped folder will be placed in the same directory. 

Links for reference, [Windows](https://support.microsoft.com/en-us/windows/zip-and-unzip-files-8d28fa72-f2f9-712f-67df-f80cf89fd4e5) and [MacOS](https://support.apple.com/en-ca/guide/mac-help/mchlp2528/mac).

## Setting up a virtual environment
Or something else, depending on how we decide to show students how to open the project.

## Creating an API Key
In this project, we will use the (free) Youtube Data API v3 . It provides a set of endpoints for us to query a wide variety of aggregated information about videos, channels, playlists, and more! Here is a link to the complete [Youtube Data API v3](https://developers.google.com/youtube/v3/getting-started). We encourage you to explore the API and maybe build a side project with it if you'd like! 

To access the endpoints, you will need to create an API Key:

- Step 1: Create a **free** [Google account](https://accounts.google.ca/), or use one you currently have. 

- Step 2: Navigate to the [Google Developer Console](https://console.developers.google.com/). Set your location to Canada and accept the terms and conditions.

- Click on "Select a Project" and then "New Project". Give your project a name and then submit. 

- Open the project. Under "APIs and Services" select **+ Enable APIs and Services**. Scroll or search until you find the "YouTube Data API v3". Click enable. This will add access to the Youtube Data API to your project. Notice the large range of other APIs avaliable to you through Google Developer. This is a great resource to make your own projects!

- Return to the APIs and Services page. Select "Credentials" on the side bar menu. Click on **+ Create Credentials** and select "API Key". Give this API Key a name (e.g. CPSC 203 Project 1). Accept the default selections and click create. You have successfully created your API Key! Copy the key to your clipboard. You can also revisit this page at any time to find your key again.

## Opening the project
Firstly, to get the project working, you have to enter the API key into your project. This key identifies you to the Google servers and is what allows you to access their resoures, in this case, the Youtube data. 

- Open the .env file provided.
- Replace `# paste your API-Key here` with your API Key (no need to wrap it in quotation marks).

In your terminal, navigate to the directory where the project is located. Remember that you can check your current directory with `pwd` and change directory with `cd`. 

Activate your virtual environment (if we're doing that).

Use the command `marimo edit youtube.py` to open the project. If everything has been installed correctly, you should be able to run and edit the project! 

## Task 1

## Task 2

## Task 3

## Submission instructions
