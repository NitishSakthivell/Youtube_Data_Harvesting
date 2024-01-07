# Youtube_Data_Harvesting
Youtube_Data_Harvesting using postgresSQL,Streamlit,MongoDB
LinkdIn: https://www.linkedin.com/in/nitish-sakthivell-47534717a/
 
The goal of the YouTube Data Harvesting and Warehousing project is to give users access to and analysis of data from several YouTube channels. The project uses Streamlit, SQL, and MongoDB to create an intuitive application that lets users retrieve, save, and query movie and channel data on YouTube.

TOOLS AND Technologies Used:

STREAMLIT: A user-friendly user interface (UI) was developed using the Streamlit library, allowing users to interact with the application and perform data retrieval and analysis tasks.

PYTHON: Python is a powerful programming language renowned for being easy to learn and understand. Python is the primary language employed in this project for the development of the complete application, including data retrieval, processing, analysis, and visualisation.

GOOGLE API CLIENT: The googleapiclient library in Python facilitates the communication with different Google APIs. Its primary purpose in this project is to interact with YouTube's Data API v3, allowing the retrieval of essential information like channel details, video specifics, and comments. By utilizing googleapiclient, developers can easily access and manipulate YouTube's extensive data resources through code.

MONGODB: The scale-out architecture on which MongoDB is based has gained popularity among developers of all stripes as a means of creating scalable applications with dynamic data structures. MongoDB, being a document database, facilitates the storing of both structured and unstructured data for developers. Documents are stored in a format akin to JSON.

POSTGRESQL: Advanced, highly scalable, and open-source, PostgreSQL is a database management system (DBMS) renowned for its feature-rich functionality and dependability. With support for multiple data types and sophisticated SQL features, it offers a framework for organizing and storing structured data.

An Ethical Viewpoint of Youtube Data Harvesting: It's important to approach YouTube content scraping in an ethical and responsible manner. Essential issues include observing data protection laws, securing the necessary authorization, and abiding by YouTube's terms and conditions. It is imperative that the gathered data be managed appropriately to protect privacy, maintain confidentiality, and avoid any potential misuse or deception. In addition, it's critical to consider the possible effects on the community and the platform in order to create a fair and sustainable scraping procedure. We can maintain integrity while deriving insightful information from YouTube data by adhering to these ethical rules.

LIBRARIES REQUIRED FOR THIS PROJECT:

1.googleapiclient.discovery

2.streamlit

3.psycopg2

4.pymongo

5.pandas

FEATURES: The following functions are available in the YouTube Data Harvesting and Warehousing application: Retrieval of channel and video data from YouTube using the YouTube API.

Storage of data in a MongoDB database as a data lake.

Migration of data from the data lake to a SQL database for efficient querying and analysis.

Search and retrieval of data from the SQL database using different search options.
