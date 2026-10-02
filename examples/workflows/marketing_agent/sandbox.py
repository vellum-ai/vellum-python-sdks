from vellum import ArrayChatMessageContent, ChatMessage, ImageChatMessageContent, StringChatMessageContent, VellumImage
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


runner = WorkflowSandboxRunner(
    workflow=Workflow(),
    inputs=[
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="Hello what can you do for me?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Hello what can you do for me?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="Hello! I can assist you with a variety of tasks, such as answering questions, providing information on a wide range of topics, helping with writing and editing, offering study tips, and even engaging in casual conversation. What do you need help with today?",
                    content=StringChatMessageContent(
                        value="Hello! I can assist you with a variety of tasks, such as answering questions, providing information on a wide range of topics, helping with writing and editing, offering study tips, and even engaging in casual conversation. What do you need help with today?"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="It's okay\nHey can you help me market my product?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="It's okay"),
                            StringChatMessageContent(value="Hey can you help me market my product?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Help me market Ipads",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Help me market Ipads"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Help me market laptops",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Help me market laptops"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I can't directly help you market iPads or laptops because I don't have access to marketing platforms or the ability to run advertising campaigns.  I also don't have access to real-time sales data or consumer preferences to tailor a specific marketing strategy.\n\nHowever, I can help you brainstorm marketing ideas. To do this effectively, I need some information from you.  For example:\n\n* **What is your target audience?** (e.g., students, professionals, gamers, etc.)\n* **What are the key features and benefits of the iPads/laptops you're selling?** (e.g., processing power, screen size, battery life, specific software compatibility)\n* **What is your budget?** (This will influence the types of marketing strategies you can employ.)\n* **What marketing channels are you considering?** (e.g., social media, email marketing, paid advertising, content marketing)\n* **What is your unique selling proposition (USP)?** What makes your offer different from competitors?\n\nOnce I have this information, I can help you develop a marketing plan, suggest relevant keywords for online searches, and even help you draft marketing copy.\n",
                    content=StringChatMessageContent(
                        value="I can't directly help you market iPads or laptops because I don't have access to marketing platforms or the ability to run advertising campaigns.  I also don't have access to real-time sales data or consumer preferences to tailor a specific marketing strategy.\n\nHowever, I can help you brainstorm marketing ideas. To do this effectively, I need some information from you.  For example:\n\n* **What is your target audience?** (e.g., students, professionals, gamers, etc.)\n* **What are the key features and benefits of the iPads/laptops you're selling?** (e.g., processing power, screen size, battery life, specific software compatibility)\n* **What is your budget?** (This will influence the types of marketing strategies you can employ.)\n* **What marketing channels are you considering?** (e.g., social media, email marketing, paid advertising, content marketing)\n* **What is your unique selling proposition (USP)?** What makes your offer different from competitors?\n\nOnce I have this information, I can help you develop a marketing plan, suggest relevant keywords for online searches, and even help you draft marketing copy.\n"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Got it, can you add my preferences to mongo db?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Got it, can you add my preferences to mongo db?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I cannot directly interact with MongoDB or any external databases.  I am a large language model; I don't have the capability to execute code that interacts with external systems or APIs unless those APIs are explicitly provided within my current context.  My abilities are limited to processing and generating text.  To store your preferences in MongoDB, you will need to use a programming language like Python and a MongoDB driver.\n",
                    content=StringChatMessageContent(
                        value="I cannot directly interact with MongoDB or any external databases.  I am a large language model; I don't have the capability to execute code that interacts with external systems or APIs unless those APIs are explicitly provided within my current context.  My abilities are limited to processing and generating text.  To store your preferences in MongoDB, you will need to use a programming language like Python and a MongoDB driver.\n"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="But what tools do you have at your disposal?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="But what tools do you have at your disposal?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="My tools are primarily linguistic and computational.  I don't have access to external websites, files, or databases unless they are explicitly provided as part of my context.  My capabilities include:\n\n* **Natural Language Processing (NLP):** I can understand, interpret, and generate human language.  This allows me to answer questions, summarize text, translate languages, and write different kinds of creative content.\n\n* **Knowledge Base:** I have been trained on a massive dataset of text and code, giving me a broad understanding of many topics.  I can access and process this information to answer your questions and provide relevant information.\n\n* **Code Generation (within limitations):** I can generate code snippets in various programming languages, but only using the APIs and libraries that are explicitly provided to me within my current session.  I cannot access or use external APIs or libraries.\n\n* **Reasoning and Logic:** I can perform logical reasoning and deduction to answer complex questions and solve problems.\n\nIn short, my tools are focused on text processing and generation, not direct interaction with the real world or external systems beyond what is explicitly given to me.\n",
                    content=StringChatMessageContent(
                        value="My tools are primarily linguistic and computational.  I don't have access to external websites, files, or databases unless they are explicitly provided as part of my context.  My capabilities include:\n\n* **Natural Language Processing (NLP):** I can understand, interpret, and generate human language.  This allows me to answer questions, summarize text, translate languages, and write different kinds of creative content.\n\n* **Knowledge Base:** I have been trained on a massive dataset of text and code, giving me a broad understanding of many topics.  I can access and process this information to answer your questions and provide relevant information.\n\n* **Code Generation (within limitations):** I can generate code snippets in various programming languages, but only using the APIs and libraries that are explicitly provided to me within my current session.  I cannot access or use external APIs or libraries.\n\n* **Reasoning and Logic:** I can perform logical reasoning and deduction to answer complex questions and solve problems.\n\nIn short, my tools are focused on text processing and generation, not direct interaction with the real world or external systems beyond what is explicitly given to me.\n"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Tell me about the tools that you have",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Tell me about the tools that you have"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I am a large language model, trained by Google.  My \"tools\" are primarily my internal capabilities, not external applications or programs.  These capabilities include:\n\n* **Natural Language Processing (NLP):**  This is my core functionality.  I can understand and generate human-like text, translate languages, and answer your questions in an informative way, even if they are open ended, challenging, or strange.\n\n* **Knowledge Base:** I have been trained on a massive dataset of text and code, which forms my knowledge base.  This allows me to access and process information from a wide range of sources to answer your questions and complete tasks.\n\n* **Code Generation:** I can generate code in various programming languages, but only within the constraints of the APIs and libraries provided to me in a given session. I cannot access or use external APIs or libraries on my own.\n\n* **Reasoning and Logic:** I can perform logical reasoning and deduction to answer complex questions and solve problems.  This includes identifying patterns, drawing inferences, and making predictions based on the information I have.\n\n* **Memory (within a conversation):** I can remember what we've discussed within our current conversation, allowing me to maintain context and provide relevant responses.  However, I don't have long-term memory across different conversations.\n\n\nEssentially, I'm a sophisticated text processing and generation engine with a vast knowledge base and the ability to reason and generate code (within limitations).  I don't have access to the internet or external filesystems unless explicitly provided within the current session.\n",
                    content=StringChatMessageContent(
                        value="I am a large language model, trained by Google.  My \"tools\" are primarily my internal capabilities, not external applications or programs.  These capabilities include:\n\n* **Natural Language Processing (NLP):**  This is my core functionality.  I can understand and generate human-like text, translate languages, and answer your questions in an informative way, even if they are open ended, challenging, or strange.\n\n* **Knowledge Base:** I have been trained on a massive dataset of text and code, which forms my knowledge base.  This allows me to access and process information from a wide range of sources to answer your questions and complete tasks.\n\n* **Code Generation:** I can generate code in various programming languages, but only within the constraints of the APIs and libraries provided to me in a given session. I cannot access or use external APIs or libraries on my own.\n\n* **Reasoning and Logic:** I can perform logical reasoning and deduction to answer complex questions and solve problems.  This includes identifying patterns, drawing inferences, and making predictions based on the information I have.\n\n* **Memory (within a conversation):** I can remember what we've discussed within our current conversation, allowing me to maintain context and provide relevant responses.  However, I don't have long-term memory across different conversations.\n\n\nEssentially, I'm a sophisticated text processing and generation engine with a vast knowledge base and the ability to reason and generate code (within limitations).  I don't have access to the internet or external filesystems unless explicitly provided within the current session.\n"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Tell me about the tools that you have",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Tell me about the tools that you have"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="Hello! I have access to a variety of tools that allow me to assist you with different tasks. Some of the tools at my disposal include:\n\n1. **Natural Language Processing (NLP):** I can understand and generate human-like text, translate languages, summarize information, and answer questions.\n\n2. **Knowledge Base:** I have been trained on a vast amount of text data, which allows me to provide information on a wide range of topics and answer questions based on that knowledge.\n\n3. **Code Generation:** I can generate code snippets in various programming languages to help with coding tasks or provide examples.\n\n4. **Logic and Reasoning:** I can perform logical reasoning and deduction to answer complex questions and solve problems.\n\n5. **Memory:** I can remember information shared within our conversation to maintain context and provide relevant responses.\n\nIf you have a specific task or question in mind, feel free to let me know how I can assist you!",
                    content=StringChatMessageContent(
                        value="Hello! I have access to a variety of tools that allow me to assist you with different tasks. Some of the tools at my disposal include:\n\n1. **Natural Language Processing (NLP):** I can understand and generate human-like text, translate languages, summarize information, and answer questions.\n\n2. **Knowledge Base:** I have been trained on a vast amount of text data, which allows me to provide information on a wide range of topics and answer questions based on that knowledge.\n\n3. **Code Generation:** I can generate code snippets in various programming languages to help with coding tasks or provide examples.\n\n4. **Logic and Reasoning:** I can perform logical reasoning and deduction to answer complex questions and solve problems.\n\n5. **Memory:** I can remember information shared within our conversation to maintain context and provide relevant responses.\n\nIf you have a specific task or question in mind, feel free to let me know how I can assist you!"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Can you find me the emails of the people?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Can you find me the emails of the people?"),
                        ]
                    ),
                ),
            ]
        ),
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="How can I upload the object to mongo db with you?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="How can I upload the object to mongo db with you?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I can help you with that! To upload an object to MongoDB, I need some information about the product. Could you please provide the product name and a brief description?",
                    content=StringChatMessageContent(
                        value="I can help you with that! To upload an object to MongoDB, I need some information about the product. Could you please provide the product name and a brief description?"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="My product name is sleaky ipad and it is really sick and cheap",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(
                                value="My product name is sleaky ipad and it is really sick and cheap"
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Can I pass image links to you as well?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Can I pass image links to you as well?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="Yes, you can! Please provide the image links, and I will include them when uploading the product information to MongoDB.",
                    content=StringChatMessageContent(
                        value="Yes, you can! Please provide the image links, and I will include them when uploading the product information to MongoDB."
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="\nhttps://media.licdn.com/dms/image/v2/D5603AQGj37IWHtx3lA/profile-displayphoto-shrink_200_200/B56ZQGzUrPHoAY-/0/1735280905226?e=2147483647&v=beta&t=F6JtlhnuR9GWNNGFq1CAt8EnsyIt9u412MGcmWBCqwk",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value=""),
                            ImageChatMessageContent(
                                value=VellumImage(
                                    src="https://media.licdn.com/dms/image/v2/D5603AQGj37IWHtx3lA/profile-displayphoto-shrink_200_200/B56ZQGzUrPHoAY-/0/1735280905226?e=2147483647&v=beta&t=F6JtlhnuR9GWNNGFq1CAt8EnsyIt9u412MGcmWBCqwk",
                                    metadata={
                                        "id": None,
                                        "type": "IMAGE",
                                        "detail": "high",
                                        "expiry": None,
                                        "signedUrl": None,
                                    },
                                )
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I'm sorry, I cannot directly process images. Please provide the image as a link (URL) so I can include it with the product information.",
                    content=StringChatMessageContent(
                        value="I'm sorry, I cannot directly process images. Please provide the image as a link (URL) so I can include it with the product information."
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text='"https://media.licdn.com/dms/image/v2/D5603AQGj37IWHtx3lA/profile-displayphoto-shrink_200_200/B56ZQGzUrPHoAY-/0/1735280905226?e=2147483647&v=beta&t=F6JtlhnuR9GWNNGFq1CAt8EnsyIt9u412MGcmWBCqwk"',
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(
                                value='"https://media.licdn.com/dms/image/v2/D5603AQGj37IWHtx3lA/profile-displayphoto-shrink_200_200/B56ZQGzUrPHoAY-/0/1735280905226?e=2147483647&v=beta&t=F6JtlhnuR9GWNNGFq1CAt8EnsyIt9u412MGcmWBCqwk"'
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="Thank you for providing the image link. Just to confirm, is this image for the 'sleaky ipad' product? Once confirmed, I will proceed to upload the product name, description, and this image link to MongoDB.",
                    content=StringChatMessageContent(
                        value="Thank you for providing the image link. Just to confirm, is this image for the 'sleaky ipad' product? Once confirmed, I will proceed to upload the product name, description, and this image link to MongoDB."
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Yes this is for that product",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Yes this is for that product"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I understand that the image is for the 'sleaky ipad' product. However, I am unable to directly upload product information, including images, to MongoDB with the current tools available to me. The `function_1` does not accept any parameters for product details.\n\nCould you please clarify how you expect me to upload this information, or if there's another method or tool I should be using?",
                    content=StringChatMessageContent(
                        value="I understand that the image is for the 'sleaky ipad' product. However, I am unable to directly upload product information, including images, to MongoDB with the current tools available to me. The `function_1` does not accept any parameters for product details.\n\nCould you please clarify how you expect me to upload this information, or if there's another method or tool I should be using?"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="It is okay I want you to create a new object with a product called Jashan. He is a really good toy that people can use",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(
                                value="It is okay I want you to create a new object with a product called Jashan. He is a really good toy that people can use"
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text='I understand you want to create a new product object for "Jashan" with the description "He is a really good toy that people can use."\n\nHowever, I am currently unable to create or upload new product objects with the available tools. The `function_1` does not have the capability to accept product details such as name or description.\n\nTherefore, I cannot fulfill this request at this moment.',
                    content=StringChatMessageContent(
                        value='I understand you want to create a new product object for "Jashan" with the description "He is a really good toy that people can use."\n\nHowever, I am currently unable to create or upload new product objects with the available tools. The `function_1` does not have the capability to accept product details such as name or description.\n\nTherefore, I cannot fulfill this request at this moment.'
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Can you try again once?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Can you try again once?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text='Can you try to add my image in this product as well. The link for that is "https://media.licdn.com/dms/image/v2/D5603AQGj37IWHtx3lA/profile-displayphoto-shrink_200_200/B56ZQGzUrPHoAY-/0/1735280905226?e=2147483647&v=beta&t=F6JtlhnuR9GWNNGFq1CAt8EnsyIt9u412MGcmWBCqwk"',
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(
                                value='Can you try to add my image in this product as well. The link for that is "https://media.licdn.com/dms/image/v2/D5603AQGj37IWHtx3lA/profile-displayphoto-shrink_200_200/B56ZQGzUrPHoAY-/0/1735280905226?e=2147483647&v=beta&t=F6JtlhnuR9GWNNGFq1CAt8EnsyIt9u412MGcmWBCqwk"'
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text='I have successfully created a new product named "Jashan" with the description "He is a really good toy that people can use" and included the provided image link. The product information has been stored in MongoDB with the ID "687c6e1018c14e740299c7d9".',
                    content=StringChatMessageContent(
                        value='I have successfully created a new product named "Jashan" with the description "He is a really good toy that people can use" and included the provided image link. The product information has been stored in MongoDB with the ID "687c6e1018c14e740299c7d9".'
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Can you add the image links to this object?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Can you add the image links to this object?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text='I have successfully added the image link to the "Jashan" product. The product information, including the image, has been stored in MongoDB with the ID "687c6e31a5ca66a1a899c7d9".',
                    content=StringChatMessageContent(
                        value='I have successfully added the image link to the "Jashan" product. The product information, including the image, has been stored in MongoDB with the ID "687c6e31a5ca66a1a899c7d9".'
                    ),
                ),
            ]
        ),
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="Find me all the emails that you can",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Find me all the emails that you can"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I can help you with that, but I need a little more information to find the right emails. Do you have a specific company, industry, or person in mind?",
                    content=StringChatMessageContent(
                        value="I can help you with that, but I need a little more information to find the right emails. Do you have a specific company, industry, or person in mind?"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Find me the emails of Jashan Pratap",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Find me the emails of Jashan Pratap"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I found the following emails for Jashan Pratap:\n\n1. jashanpratap123456@gmail.com - Senior Software Engineer at Tech Innovations Inc., San Francisco, CA\n2. jashanpratap123@gmail.com - Data Scientist at AI Research Labs, Seattle, WA\n\nIf you need more details or want emails for a different person or company, please let me know!",
                    content=StringChatMessageContent(
                        value="I found the following emails for Jashan Pratap:\n\n1. jashanpratap123456@gmail.com - Senior Software Engineer at Tech Innovations Inc., San Francisco, CA\n2. jashanpratap123@gmail.com - Data Scientist at AI Research Labs, Seattle, WA\n\nIf you need more details or want emails for a different person or company, please let me know!"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Find me relevant people's email for my product",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Find me relevant people's email for my product"),
                        ]
                    ),
                ),
            ]
        ),
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="Hey can you find emails of people on my behalf?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Hey can you find emails of people on my behalf?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Can you make a linkedin post for me and then upload it linkedin. Make a video about a sleaky ipad",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(
                                value="Can you make a linkedin post for me and then upload it linkedin. Make a video about a sleaky ipad"
                            ),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I can help you create a LinkedIn post and a video script about a sleek iPad. After that, I can upload the post to LinkedIn for you. Let's start with the content creation.\n\nCould you please provide me with some key points or features you'd like to highlight about the sleek iPad? Also, do you have any specific tone or style in mind for the post and video?",
                    content=StringChatMessageContent(
                        value="I can help you create a LinkedIn post and a video script about a sleek iPad. After that, I can upload the post to LinkedIn for you. Let's start with the content creation.\n\nCould you please provide me with some key points or features you'd like to highlight about the sleek iPad? Also, do you have any specific tone or style in mind for the post and video?"
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Quirky brainrot tone and good style",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Quirky brainrot tone and good style"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text='Great! I\'ll create a LinkedIn post and a video script about a sleek iPad with a quirky brainrot tone and good style. Here\'s a draft for your review:\n\nLinkedIn Post:\n"Say hello to the sleekest sidekick your brain ever dreamed of — the iPad that’s basically a genius in a slim, shiny package. Whether you’re doodling your next masterpiece, binge-watching your fave shows, or pretending to work (we won’t tell), this iPad’s got your back. Ready to upgrade your tech game? #SleekAndSmart #iPadMagic #TechGoals"\n\nVideo Script:\n[Opening shot of the sleek iPad spinning slowly]\nVoiceover: "Meet the iPad that’s so sleek, it’s basically a brain’s best friend."\n[Cut to someone using the iPad with exaggerated excitement]\nVoiceover: "Doodle, stream, work, or procrastinate — it handles it all with style."\n[Close-up of the iPad’s features]\nVoiceover: "Thin, light, and smarter than your average gadget. It’s not just a tablet; it’s a lifestyle."\n[Ending shot with the iPad logo and tagline]\nVoiceover: "Upgrade your vibe. Get the sleek iPad today."\n\nWould you like me to proceed with uploading this post and video script to LinkedIn? If you have any changes or additions, please let me know!',
                    content=StringChatMessageContent(
                        value='Great! I\'ll create a LinkedIn post and a video script about a sleek iPad with a quirky brainrot tone and good style. Here\'s a draft for your review:\n\nLinkedIn Post:\n"Say hello to the sleekest sidekick your brain ever dreamed of — the iPad that’s basically a genius in a slim, shiny package. Whether you’re doodling your next masterpiece, binge-watching your fave shows, or pretending to work (we won’t tell), this iPad’s got your back. Ready to upgrade your tech game? #SleekAndSmart #iPadMagic #TechGoals"\n\nVideo Script:\n[Opening shot of the sleek iPad spinning slowly]\nVoiceover: "Meet the iPad that’s so sleek, it’s basically a brain’s best friend."\n[Cut to someone using the iPad with exaggerated excitement]\nVoiceover: "Doodle, stream, work, or procrastinate — it handles it all with style."\n[Close-up of the iPad’s features]\nVoiceover: "Thin, light, and smarter than your average gadget. It’s not just a tablet; it’s a lifestyle."\n[Ending shot with the iPad logo and tagline]\nVoiceover: "Upgrade your vibe. Get the sleek iPad today."\n\nWould you like me to proceed with uploading this post and video script to LinkedIn? If you have any changes or additions, please let me know!'
                    ),
                ),
                ChatMessage(
                    role="USER",
                    text="Yes",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="Yes"),
                        ]
                    ),
                ),
            ]
        ),
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="What tools do you have?",
                    content=ArrayChatMessageContent(
                        value=[
                            StringChatMessageContent(value="What tools do you have?"),
                        ]
                    ),
                ),
                ChatMessage(
                    role="ASSISTANT",
                    text="I have the following tools available:\n\n1. functions.context_collector: Collects product marketing information and stores metadata in MongoDB.\n2. functions.email_getter: Extracts professional email addresses using multiple methods.\n3. functions.post_linkedin: Posts content to LinkedIn including text, video script, and optional images.\n4. multi_tool_use.parallel: Allows running multiple functions tools simultaneously in parallel.\n\nIf you want, I can provide more details or help you use any of these tools.",
                    content=StringChatMessageContent(
                        value="I have the following tools available:\n\n1. functions.context_collector: Collects product marketing information and stores metadata in MongoDB.\n2. functions.email_getter: Extracts professional email addresses using multiple methods.\n3. functions.post_linkedin: Posts content to LinkedIn including text, video script, and optional images.\n4. multi_tool_use.parallel: Allows running multiple functions tools simultaneously in parallel.\n\nIf you want, I can provide more details or help you use any of these tools."
                    ),
                ),
            ]
        ),
    ],
)

runner.run()
